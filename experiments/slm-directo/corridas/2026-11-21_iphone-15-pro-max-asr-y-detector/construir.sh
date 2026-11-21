#!/bin/sh
# Compila sherpa-onnx v1.13.8 para iOS y macOS, arma la app con llama-server y el ASR, y el binario de la prueba en
# seco en la Mac.
#
#   ./construir.sh CARPETA_DE_TRABAJO TEAM_ID BUNDLE_ID UDID
#
# Antes: ../2026-11-20_iphone-15-pro-max-latencia/construir.sh con la misma CARPETA_DE_TRABAJO, que deja llama.cpp
# compilado para iOS en CARPETA_DE_TRABAJO/llama-ios. Deja la app en CARPETA_DE_TRABAJO/app-asr/Release-iphoneos/ y
# asr-mac en CARPETA_DE_TRABAJO/asr-mac. No instala nada en el teléfono.
set -eu
TRABAJO=$1 EQUIPO=$2 BUNDLE=$3 UDID=$4
AQUI=$(cd "$(dirname "$0")" && pwd)
SH="$TRABAJO/sherpa-onnx"

if [ ! -d "$SH" ]; then
    git clone --depth 1 --branch v1.13.8 https://github.com/k2-fsa/sherpa-onnx.git "$SH"
fi

# iOS: las opciones de la parte os64 de build-ios-no-tts.sh, con el mínimo de iOS de la app. El script de sherpa baja
# la biblioteca estática de onnxruntime 1.28.2 a build-ios/ios-onnxruntime.
ORT="$SH/build-ios/ios-onnxruntime/onnxruntime.xcframework"
if [ ! -d "$ORT" ]; then
    mkdir -p "$SH/build-ios/ios-onnxruntime"
    (cd "$SH/build-ios/ios-onnxruntime" &&
        curl -sSLO https://github.com/csukuangfj/onnxruntime-libs/releases/download/v1.28.2/onnxruntime-ios-static-xcframework-1.28.2.xcframework.zip &&
        unzip -q onnxruntime-ios-static-xcframework-1.28.2.xcframework.zip && rm onnxruntime-ios-static-xcframework-1.28.2.xcframework.zip)
fi
cmake -S "$SH" -B "$SH/build-ios/build/os64" -DCMAKE_TOOLCHAIN_FILE="$SH/toolchains/ios.toolchain.cmake" \
    -DPLATFORM=OS64 -DENABLE_BITCODE=0 -DENABLE_ARC=1 -DENABLE_VISIBILITY=0 -DDEPLOYMENT_TARGET=16.4 \
    -DCMAKE_INSTALL_PREFIX="$SH/build-ios/install" -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF \
    -DSHERPA_ONNX_ENABLE_TTS=OFF -DSHERPA_ONNX_ENABLE_SPEAKER_DIARIZATION=OFF -DSHERPA_ONNX_ENABLE_PYTHON=OFF \
    -DSHERPA_ONNX_ENABLE_BINARY=OFF -DSHERPA_ONNX_ENABLE_TESTS=OFF -DSHERPA_ONNX_ENABLE_CHECK=OFF \
    -DSHERPA_ONNX_ENABLE_PORTAUDIO=OFF -DSHERPA_ONNX_ENABLE_JNI=OFF -DSHERPA_ONNX_ENABLE_C_API=ON \
    -DSHERPA_ONNX_ENABLE_WEBSOCKET=OFF
cmake --build "$SH/build-ios/build/os64" -j 8 --target install

# macOS, para la prueba en seco: estática, con la onnxruntime 1.28.2 que baja el propio cmake de sherpa.
cmake -S "$SH" -B "$SH/build-mac" -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF -DCMAKE_OSX_ARCHITECTURES=arm64 \
    -DCMAKE_INSTALL_PREFIX="$SH/build-mac/install" -DSHERPA_ONNX_ENABLE_TTS=OFF \
    -DSHERPA_ONNX_ENABLE_SPEAKER_DIARIZATION=OFF -DSHERPA_ONNX_ENABLE_PORTAUDIO=OFF -DSHERPA_ONNX_ENABLE_WEBSOCKET=OFF \
    -DSHERPA_ONNX_ENABLE_PYTHON=OFF -DSHERPA_ONNX_ENABLE_TESTS=OFF -DSHERPA_ONNX_ENABLE_BINARY=OFF \
    -DSHERPA_ONNX_BUILD_C_API_EXAMPLES=OFF -DSHERPA_ONNX_ENABLE_C_API=ON
cmake --build "$SH/build-mac" -j 8 --target install
L="$SH/build-mac/install/lib"
clang++ -std=c++17 -O2 -I"$SH" "$AQUI/app/asr.cpp" "$AQUI/app/asr_mac.cpp" -o "$TRABAJO/asr-mac" \
    "$L/libsherpa-onnx-c-api.a" "$L/libsherpa-onnx-core.a" "$L/libkaldi-decoder-core.a" \
    "$L/libsherpa-onnx-kaldifst-core.a" "$L/libsherpa-onnx-fstfar.a" "$L/libsherpa-onnx-fst.a" \
    "$L/libkaldi-native-fbank-core.a" "$L/libkissfft-float.a" "$L/libssentencepiece_core.a" "$L/libonnxruntime.a" \
    -framework Foundation

cmake -S "$AQUI/app" -B "$TRABAJO/app-asr" -G Xcode -DCMAKE_SYSTEM_NAME=iOS -DCMAKE_OSX_DEPLOYMENT_TARGET=16.4 \
    -DLLAMA_BUILD="$TRABAJO/llama-ios" -DSHERPA_SRC="$SH" -DSHERPA_LIB="$SH/build-ios/install/lib" \
    -DONNXRUNTIME="$ORT/ios-arm64/onnxruntime.framework/onnxruntime" -DEQUIPO="$EQUIPO" -DBUNDLE_ID="$BUNDLE"
xcodebuild -project "$TRABAJO/app-asr/DetectorLab.xcodeproj" -scheme DetectorLab -configuration Release \
    -destination "id=$UDID" -allowProvisioningUpdates -allowProvisioningDeviceRegistration build
ls -d "$TRABAJO/app-asr/Release-iphoneos/DetectorLab.app" "$TRABAJO/asr-mac"
