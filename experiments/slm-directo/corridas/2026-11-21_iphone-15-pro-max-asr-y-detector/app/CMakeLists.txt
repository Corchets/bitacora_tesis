# La app de la corrida anterior (main.mm, Info.plist) con el ASR: main.mm compilado con CON_ASR más asr.cpp,
# enlazados con las bibliotecas estáticas de llama.cpp (LLAMA_BUILD) y de sherpa-onnx v1.13.8 para iOS (SHERPA_SRC,
# SHERPA_LIB, ONNXRUNTIME: la biblioteca estática de onnxruntime que baja build-ios.sh de sherpa-onnx).
cmake_minimum_required(VERSION 3.24)
project(DetectorLab LANGUAGES CXX OBJCXX)

set(LLAMA_BUILD "" CACHE PATH "carpeta del build de llama.cpp para iOS")
set(SHERPA_SRC "" CACHE PATH "clon de sherpa-onnx v1.13.8")
set(SHERPA_LIB "" CACHE PATH "carpeta con las bibliotecas de sherpa-onnx para iOS")
set(ONNXRUNTIME "" CACHE FILEPATH "biblioteca estática de onnxruntime para iOS")
set(EQUIPO "" CACHE STRING "Team ID de la cuenta de Apple")
set(BUNDLE_ID "" CACHE STRING "identificador de la app")
set(ANTERIOR "${CMAKE_CURRENT_SOURCE_DIR}/../../2026-11-20_iphone-15-pro-max-latencia/app")

file(GLOB_RECURSE BIBLIOTECAS "${LLAMA_BUILD}/*.a")
file(GLOB SHERPA "${SHERPA_LIB}/*.a")
if(NOT BIBLIOTECAS OR NOT SHERPA OR NOT EXISTS "${ONNXRUNTIME}")
    message(FATAL_ERROR "Faltan bibliotecas: LLAMA_BUILD=${LLAMA_BUILD} SHERPA_LIB=${SHERPA_LIB} ONNXRUNTIME=${ONNXRUNTIME}")
endif()

add_executable(DetectorLab MACOSX_BUNDLE "${ANTERIOR}/main.mm" asr.cpp)
target_compile_definitions(DetectorLab PRIVATE CON_ASR)
target_include_directories(DetectorLab PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}" "${SHERPA_SRC}")
target_compile_features(DetectorLab PRIVATE cxx_std_17)
target_link_libraries(DetectorLab PRIVATE ${BIBLIOTECAS} ${SHERPA} "${ONNXRUNTIME}"
    "-framework UIKit" "-framework Foundation" "-framework CoreGraphics" "-framework Metal" "-framework MetalKit"
    "-framework Accelerate" "-framework CoreML")
set_target_properties(DetectorLab PROPERTIES
    MACOSX_BUNDLE_INFO_PLIST "${ANTERIOR}/Info.plist"
    XCODE_ATTRIBUTE_PRODUCT_BUNDLE_IDENTIFIER "${BUNDLE_ID}"
    XCODE_ATTRIBUTE_DEVELOPMENT_TEAM "${EQUIPO}"
    XCODE_ATTRIBUTE_CODE_SIGN_STYLE "Automatic"
    XCODE_ATTRIBUTE_TARGETED_DEVICE_FAMILY "1"
    XCODE_ATTRIBUTE_CLANG_ENABLE_OBJC_ARC "YES")
