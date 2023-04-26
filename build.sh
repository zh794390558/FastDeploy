rm -rf build
mkdir build && cd build
cmake .. -DENABLE_ORT_BACKEND=ON \
         -DENABLE_PADDLE_BACKEND=OFF \
         -DENABLE_OPENVINO_BACKEND=OFF \
         -DCMAKE_INSTALL_PREFIX=${PWD}/compiled_fastdeploy_sdk \
         -DENABLE_VISION=OFF \
         -DENABLE_TEXT=OFF
make -j12
make install
