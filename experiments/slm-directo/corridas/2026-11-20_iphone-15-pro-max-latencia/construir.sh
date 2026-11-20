#!/bin/sh
# Compila llama-server (llama.cpp 6c01da62, el commit del A56) para iOS y arma la app firmada.
#
#   ./construir.sh CARPETA_DE_TRABAJO TEAM_ID BUNDLE_ID
#
# Necesita Xcode con el componente de iOS, cmake y una cuenta de Apple con sesión iniciada en Xcode. Deja la app en
# CARPETA_DE_TRABAJO/app/Release-iphoneos/DetectorLab.app. No instala nada en el teléfono: eso lo hace medir.py.
set -eu
TRABAJO=$1 EQUIPO=$2 BUNDLE=$3
AQUI=$(cd "$(dirname "$0")" && pwd)
COMMIT=6c01da6278ab6c69ed67d9124806b50d2b299ba7

if [ ! -d "$TRABAJO/llama.cpp" ]; then
    git clone --filter=blob:none https://github.com/ggml-org/llama.cpp.git "$TRABAJO/llama.cpp"
fi
git -C "$TRABAJO/llama.cpp" checkout --quiet "$COMMIT"

# Las mismas opciones que build-xcframework.sh de llama.cpp, más el servidor (sin interfaz web, HTTPS ni subprocesos).
cmake -S "$TRABAJO/llama.cpp" -B "$TRABAJO/llama-ios" \
    -DCMAKE_SYSTEM_NAME=iOS -DCMAKE_OSX_SYSROOT=iphoneos -DCMAKE_OSX_ARCHITECTURES=arm64 \
    -DCMAKE_OSX_DEPLOYMENT_TARGET=16.4 -DCMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_MACOSX_BUNDLE=OFF -DBUILD_SHARED_LIBS=OFF -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=OFF -DLLAMA_BUILD_APP=OFF \
    -DLLAMA_BUILD_TOOLS=ON -DLLAMA_BUILD_SERVER=ON -DLLAMA_BUILD_UI=OFF -DLLAMA_USE_PREBUILT_UI=OFF \
    -DLLAMA_OPENSSL=OFF -DLLAMA_SUBPROCESS=OFF \
    -DGGML_METAL=ON -DGGML_METAL_EMBED_LIBRARY=ON -DGGML_BLAS_DEFAULT=ON -DGGML_OPENMP=OFF -DGGML_NATIVE=OFF
cmake --build "$TRABAJO/llama-ios" --target llama-server-impl -j 8

cmake -S "$AQUI/app" -B "$TRABAJO/app" -G Xcode -DCMAKE_SYSTEM_NAME=iOS -DCMAKE_OSX_DEPLOYMENT_TARGET=16.4 \
    -DLLAMA_BUILD="$TRABAJO/llama-ios" -DEQUIPO="$EQUIPO" -DBUNDLE_ID="$BUNDLE"
xcodebuild -project "$TRABAJO/app/DetectorLab.xcodeproj" -scheme DetectorLab -configuration Release \
    -destination generic/platform=iOS -allowProvisioningUpdates build
ls -d "$TRABAJO/app/Release-iphoneos/DetectorLab.app"
