# La app: main.mm enlazado con las bibliotecas estáticas de llama.cpp que deja construir.sh en LLAMA_BUILD.
# Se genera con -G Xcode para que xcodebuild la firme con el equipo personal de la cuenta de Apple (EQUIPO).
cmake_minimum_required(VERSION 3.24)
project(DetectorLab LANGUAGES CXX OBJCXX)

set(LLAMA_BUILD "" CACHE PATH "carpeta del build de llama.cpp para iOS")
set(EQUIPO "" CACHE STRING "Team ID de la cuenta de Apple")
set(BUNDLE_ID "" CACHE STRING "identificador de la app")

file(GLOB_RECURSE BIBLIOTECAS "${LLAMA_BUILD}/*.a")
if(NOT BIBLIOTECAS)
    message(FATAL_ERROR "No hay bibliotecas en LLAMA_BUILD=${LLAMA_BUILD}")
endif()

add_executable(DetectorLab MACOSX_BUNDLE main.mm)
target_compile_features(DetectorLab PRIVATE cxx_std_17)
target_link_libraries(DetectorLab PRIVATE ${BIBLIOTECAS}
    "-framework UIKit" "-framework Foundation" "-framework Metal" "-framework MetalKit" "-framework Accelerate")
set_target_properties(DetectorLab PROPERTIES
    MACOSX_BUNDLE_INFO_PLIST "${CMAKE_CURRENT_SOURCE_DIR}/Info.plist"
    XCODE_ATTRIBUTE_PRODUCT_BUNDLE_IDENTIFIER "${BUNDLE_ID}"
    XCODE_ATTRIBUTE_DEVELOPMENT_TEAM "${EQUIPO}"
    XCODE_ATTRIBUTE_CODE_SIGN_STYLE "Automatic"
    XCODE_ATTRIBUTE_TARGETED_DEVICE_FAMILY "1"
    XCODE_ATTRIBUTE_CLANG_ENABLE_OBJC_ARC "YES")
