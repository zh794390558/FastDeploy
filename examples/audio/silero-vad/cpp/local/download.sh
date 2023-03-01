mkdir -p fdlib
cd fdlib

wget -c https://bj.bcebos.com/fastdeploy/release/android/fastdeploy-android-1.0.4-shared.tgz

wget -c https://bj.bcebos.com/fastdeploy/release/cpp/fastdeploy-linux-x64-1.0.4.tgz

wget -c https://fastdeploy.bj.bcebos.com/rel_tmp/cpp/fastdeploy-linux-aarch64-gpu-0.0.0.tgz

test -e fastdeploy-android-1.0.4-shared || tar zxvf fastdeploy-android-1.0.4-shared.tgz

test -e fastdeploy-linux-x64-1.0.4 || tar zxvf fastdeploy-linux-x64-1.0.4.tgz

test -e fastdeploy-linux-aarch64-gpu-0.0.0 || tar zxvf fastdeploy-linux-aarch64-gpu-0.0.0.tgz



wget -c https://bj.bcebos.com/paddlehub/fastdeploy/silero_vad.tgz

test -e silero_vad || tar zxvf silero_vad.tgz

wget -c https://bj.bcebos.com/paddlehub/fastdeploy/silero_vad_sample.wav
