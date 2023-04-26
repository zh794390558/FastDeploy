#!/bin/bash
set -e
set +x

# -------------------------------------------------------------------------------
#                        mutable global variables
# -------------------------------------------------------------------------------
TOOLCHAIN=clang # gcc/clang toolchain

# -------------------------------------------------------------------------------
#                        readonly global variables
# -------------------------------------------------------------------------------
readonly ROOT_PATH=$(pwd)
readonly ANDROID_ABI=$1
readonly ANDROID_PLATFORM="android-$2"
readonly BUILD_ROOT=build/Android
readonly BUILD_DIR=${BUILD_ROOT}/${ANDROID_ABI}-api-$2
readonly ANDROID_NDK=~/Library/Android/sdk/ndk/20.0.5594570/

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
    echo "unset it before crossing compiling ${ANDROID_ABI}"
    unset LDFLAGS
  fi
  if [ $CPPFLAGS ]; then
    echo "-- [INFO] Found CPPFLAGS: ${CPPFLAGS}, \c"
    echo "unset it before crossing compiling ${ANDROID_ABI}"
    unset CPPFLAGS
  fi
  if [ $CPLUS_INCLUDE_PATH ]; then
    echo "-- [INFO] Found CPLUS_INCLUDE_PATH: ${CPLUS_INCLUDE_PATH}, \c"
    echo "unset it before crossing compiling ${ANDROID_ABI}"
    unset CPLUS_INCLUDE_PATH
  fi
  if [ $C_INCLUDE_PATH ]; then
    echo "-- [INFO] Found C_INCLUDE_PATH: ${C_INCLUDE_PATH}, \c"
    echo "unset it before crossing compiling ${ANDROID_ABI}"
    unset C_INCLUDE_PATH
  fi
}

__set_android_ndk() {
  if [ -z $ANDROID_NDK ]; then
    echo "-- [INFO] ANDROID_NDK not exists, please setup manually ..."
    exit 0
  else
    echo "-- [INFO] Found ANDROID_NDK: ${ANDROID_NDK}"
  fi
  if [ "$ANDROID_NDK" ]; then
      NDK_VERSION=$(echo $ANDROID_NDK | egrep -o "[0-9]{2}" | head -n 1)
      if [ "$NDK_VERSION" -gt 17 ]; then
          TOOLCHAIN=clang
      fi
      echo "-- [INFO] Checked ndk version: ${NDK_VERSION}"
      echo "-- [INFO] Selected toolchain: ${TOOLCHAIN}"
  fi
}

__build_fastdeploy_android_shared() {

  local ANDROID_STL=c++_shared  # c++_static
  local ANDROID_TOOLCHAIN=${TOOLCHAIN}
  local TOOLCHAIN_FILE=${ANDROID_NDK}/build/cmake/android.toolchain.cmake
  local FASDEPLOY_INSTALL_DIR="${ROOT_PATH}/${BUILD_DIR}/install"
  cd "${BUILD_DIR}" && echo "-- [INFO] Working Dir: ${PWD}"

  cmake -DCMAKE_TOOLCHAIN_FILE=${TOOLCHAIN_FILE} \
        -DCMAKE_BUILD_TYPE=MinSizeRel \
        -DANDROID_ABI=${ANDROID_ABI} \
        -DANDROID_NDK=${ANDROID_NDK} \
        -DANDROID_PLATFORM=${ANDROID_PLATFORM} \
        -DANDROID_STL=${ANDROID_STL} \
        -DANDROID_TOOLCHAIN=${ANDROID_TOOLCHAIN} \
        -DENABLE_ORT_BACKEND=ON \
        -DENABLE_LITE_BACKEND=OFF \
        -DENABLE_PADDLE2ONNX=OFF \
        -DENABLE_FLYCV=OFF \
        -DENABLE_TEXT=OFF \
		-DENABLE_VISION=OFF \
        -DBUILD_EXAMPLES=OFF \
        -DWITH_ANDROID_OPENCV_STATIC=OFF \
        -DWITH_ANDROID_LITE_STATIC=OFF \
        -DWITH_ANDROID_OPENMP=OFF \
		-DORT_DIRECTORY=/Users/masimeng/Documents/vad/libs/onnxruntime/Android/${ANDROID_ABI} \
        -DCMAKE_INSTALL_PREFIX=${FASDEPLOY_INSTALL_DIR} \
        -Wno-dev ../../.. && make -j8 && make install

  echo "-- [INFO][built][${ANDROID_ABI}][${BUILD_DIR}/install]"
}

main() {
  __make_build_dir
  __check_cxx_envs
  __set_android_ndk
  __build_fastdeploy_android_shared
  exit 0
}

main

# Usage:
# ./scripts/android/build_android_cpp.sh arm64-v8a 21
# ./scripts/android/build_android_cpp.sh armeabi-v7a 21
