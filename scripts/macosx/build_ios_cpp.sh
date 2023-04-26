#!/bin/bash
set -e
set +x

# -------------------------------------------------------------------------------
#                        readonly global variables
# -------------------------------------------------------------------------------
readonly ROOT_PATH=$(pwd)
readonly BUILD_ROOT=build/iOS
readonly ARCH=$1  # arm64, x86_64
readonly BUILD_DIR=${BUILD_ROOT}/${ARCH}
ios_toolchain_cmake="/Users/masimeng/Documents/ios-cmake-4.2.0/ios.toolchain.cmake"

# -------------------------------------------------------------------------------
#                                 tasks
# -------------------------------------------------------------------------------
__make_build_dir() {
  if [ ! -d "${BUILD_DIR}" ]; then
    echo "-- [INFO] BUILD_DIR: ${BUILD_DIR} not exists, setup manually ..."
    if [ ! -d "${BUILD_ROOT}" ]; then
      mkdir -p "${BUILD_ROOT}" && echo "-- [INFO] Created ${BUILD_ROOT} !"
    fi
    mkdir -p "${BUILD_DIR}" && echo "-- [INFO] Created ${BUILD_DIR} !"
  else
    echo "-- [INFO] Found BUILD_DIR: ${BUILD_DIR}"
  fi
}

__check_cxx_envs() {
  if [ $LDFLAGS ]; then
    echo "-- [INFO] Found LDFLAGS: ${LDFLAGS}, \c"
    echo "unset it before crossing compiling ${BUILD_DIR}"
    unset LDFLAGS
  fi
  if [ $CPPFLAGS ]; then
    echo "-- [INFO] Found CPPFLAGS: ${CPPFLAGS}, \c"
    echo "unset it before crossing compiling ${BUILD_DIR}"
    unset CPPFLAGS
  fi
  if [ $CPLUS_INCLUDE_PATH ]; then
    echo "-- [INFO] Found CPLUS_INCLUDE_PATH: ${CPLUS_INCLUDE_PATH}, \c"
    echo "unset it before crossing compiling ${BUILD_DIR}"
    unset CPLUS_INCLUDE_PATH
  fi
  if [ $C_INCLUDE_PATH ]; then
    echo "-- [INFO] Found C_INCLUDE_PATH: ${C_INCLUDE_PATH}, \c"
    echo "unset it before crossing compiling ${BUILD_DIR}"
    unset C_INCLUDE_PATH
  fi
}

__build_fastdeploy_ios_arm64_shared() {

  local FASDEPLOY_INSTALL_DIR="${ROOT_PATH}/${BUILD_DIR}/install"
  cd "${BUILD_DIR}" && echo "-- [INFO] Working Dir: ${PWD}"
  cmake -DCMAKE_TOOLCHAIN_FILE=${ios_toolchain_cmake} \
        -DCMAKE_BUILD_TYPE=MinSizeRel \
        -DENABLE_ORT_BACKEND=ON \
        -DENABLE_PADDLE2ONNX=OFF \
        -DENABLE_VISION=OFF \
        -DENABLE_BENCHMARK=OFF \
        -DBUILD_EXAMPLES=OFF \
        -DCMAKE_INSTALL_PREFIX=${FASDEPLOY_INSTALL_DIR} \
		-DORT_DIRECTORY=/Users/masimeng/Documents/vad/libs/onnxruntime/iOS/arm64 \
		-DENABLE_BITCODE=OFF \
		-DPLATFORM=OS \
		-DARCHS=arm64 \
        -Wno-dev ../../.. && make -j8 && mkdir -p third_libs/install && make install

  echo "-- [INFO][built][${ARCH}][${BUILD_DIR}/install]"
}

__build_fastdeploy_ios_x86_64_shared() {

  local FASDEPLOY_INSTALL_DIR="${ROOT_PATH}/${BUILD_DIR}/install"
  cd "${BUILD_DIR}" && echo "-- [INFO] Working Dir: ${PWD}"
  cmake -DCMAKE_TOOLCHAIN_FILE=${ios_toolchain_cmake} \
        -DCMAKE_BUILD_TYPE=MinSizeRel \
        -DENABLE_ORT_BACKEND=ON \
        -DENABLE_PADDLE2ONNX=OFF \
        -DENABLE_VISION=OFF \
        -DENABLE_BENCHMARK=OFF \
        -DBUILD_EXAMPLES=OFF \
        -DCMAKE_INSTALL_PREFIX=${FASDEPLOY_INSTALL_DIR} \
        -DORT_DIRECTORY=/Users/masimeng/Documents/vad/libs/onnxruntime/iOS/x86_64 \
        -DENABLE_BITCODE=OFF \
        -DPLATFORM=SIMULATOR64 \
        -Wno-dev ../../.. && make -j8 && mkdir -p third_libs/install && make install

  echo "-- [INFO][built][${ARCH}][${BUILD_DIR}/install]"
}

main() {
  __make_build_dir
  __check_cxx_envs
  if [ "$ARCH" = "arm64" ]; then
    __build_fastdeploy_ios_arm64_shared
  else
    __build_fastdeploy_ios_x86_64_shared
  fi
  exit 0
}

main

# Usage:
# ./scripts/macosx/build_ios_cpp.sh arm64
