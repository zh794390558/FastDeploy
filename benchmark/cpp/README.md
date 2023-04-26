# FastDeploy C++ Benchmarks

## 1. 编译选项  
以下选项为benchmark相关的编译选项，在编译用来跑benchmark的sdk时，必须开启。  

|选项|需要设置的值|说明|
|---|---|---|  
| ENABLE_BENCHMARK  | ON | 默认OFF, 是否打开BENCHMARK模式 |
| ENABLE_VISION     | ON | 默认OFF，是否编译集成视觉模型的部署模块 |
| ENABLE_TEXT       | ON | 默认OFF，是否编译集成文本NLP模型的部署模块 |  

运行FastDeploy C++ Benchmark，需先准备好相应的环境，并在ENABLE_BENCHMARK=ON模式下从源码编译FastDeploy C++ SDK. 以下将按照硬件维度，来说明相应的系统环境要求。不同环境下的详细要求，请参考[FastDeploy环境要求](../../docs/cn/build_and_install)  

## 2. Benchmark 设置说明  

具体flags.h提供选项如下:

<div id="选项设置说明"></div>  

| 选项                 | 作用                                        |
| -------------------- | ------------------------------------------ |
| --model              | 模型路径                                     |
| --image              | 图片路径    |
| --config_path        | config.txt路径，包含具体设备、后端等信息  |

具体config.txt包含信息含义如下:

<div id="参数设置说明"></div>  

| 参数                 | 作用                                        |
| -------------------- | ------------------------------------------ |
| device             | 选择 CPU/GPU/XPU，默认为 CPU  |
| device_id          | GPU/XPU 卡号，默认为 0 |
| cpu_thread_nums     | CPU 线程数，默认为 1      |
| warmup           | 跑benchmark的warmup次数，默认为 200 |
| repeat           | 跑benchmark的循环次数，默认为 1000 |
| backend            | 指定后端类型，有default, ort, ov, trt, paddle, paddle_trt, lite 等，为default时，会自动选择最优后端，推荐设置为显式设置明确的backend。默认为 default   |
| profile_mode      | 指定需要测试性能的模式，可选值为`[runtime, end2end]`，默认为 runtime |
| include_h2d_d2h   | 是否把H2D+D2H的耗时统计在内，该参数只在profile_mode为runtime时有效，默认为 false |  
| use_fp16    | 是否开启fp16，当前只对 trt, paddle-trt, lite后端有效，默认为 false |
| collect_memory_info    | 是否记录 cpu/gpu memory信息，默认 false  |
| sampling_interval    | 记录 cpu/gpu memory信息采样时间间隔，单位ms，默认为 50  |
| precision_compare    | 是否进行精度比较，默认为 false  |  
| result_path    | 记录 Benchmark 数据的 txt 文件路径  |  
| xpu_l3_cache | 设置XPU L3 Cache大小，默认值为0。设置策略，对于 昆仑2 XPU R200，L3 Cache可用的最大值为 62914560，对于 昆仑1 XPU 则为 16776192 |

## 3. X86_64 CPU 和 NVIDIA GPU 环境下运行 Benchmark

### 3.1 环境准备  

Linux上编译需满足:
  - gcc/g++ >= 5.4(推荐8.2)
  - cmake >= 3.18.0
  - CUDA >= 11.2
  - cuDNN >= 8.2
  - TensorRT >= 8.5

在GPU上编译FastDeploy需要准备好相应的CUDA环境以及TensorRT，详细文档请参考[GPU编译文档](https://github.com/PaddlePaddle/FastDeploy/blob/develop/docs/cn/build_and_install/gpu.md)。  

### 3.2 编译FastDeploy C++ SDK  
```bash
# 源码编译SDK
git clone https://github.com/PaddlePaddle/FastDeploy.git -b develop
cd FastDeploy
mkdir build && cd build
cmake .. -DWITH_GPU=ON \
         -DENABLE_ORT_BACKEND=ON \
         -DENABLE_PADDLE_BACKEND=ON \
         -DENABLE_OPENVINO_BACKEND=ON \
         -DENABLE_TRT_BACKEND=ON \
         -DENABLE_VISION=ON \
         -DENABLE_TEXT=ON \
         -DENABLE_BENCHMARK=ON \  # 开启benchmark模式
         -DTRT_DIRECTORY=/Paddle/TensorRT-8.5.2.2 \
         -DCUDA_DIRECTORY=/usr/local/cuda \
         -DCMAKE_INSTALL_PREFIX=${PWD}/compiled_fastdeploy_sdk

make -j12
make install  

# 配置SDK路径
cd ..  
export FD_GPU_SDK=${PWD}/build/compiled_fastdeploy_sdk
```  
### 3.3 编译 Benchmark 示例  
```bash  
cd benchmark/cpp
mkdir build && cd build  
cmake .. -DFASTDEPLOY_INSTALL_DIR=${FD_GPU_SDK}  
make -j4
```

### 3.4 运行 Benchmark 示例  

在X86 CPU + NVIDIA GPU下，FastDeploy 目前支持多种推理后端，下面以 PaddleYOLOv8 为例，跑出多后端在 CPU/GPU 对应 benchmark 数据。

- 下载模型文件和测试图片  
```bash  
wget https://bj.bcebos.com/paddlehub/fastdeploy/yolov8_s_500e_coco.tgz  
wget https://gitee.com/paddlepaddle/PaddleDetection/raw/release/2.4/demo/000000014439.jpg
tar -zxvf yolov8_s_500e_coco.tgz
```

- 运行 yolov8 benchmark 示例  

```bash  

# 统计性能，用户根据需求修改config.txt文件，具体含义参考上表
# eg：如果想测paddle gpu backend，将device改为gpu，backend修改为paddle即可
./benchmark_ppyolov8 --model yolov8_s_500e_coco --image 000000014439.jpg --config_path config.txt
```
注意，为避免对性能统计产生影响，测试性能时，最好不要开启内存显存统计的功能，当把collect_memory_info参数设置为true时，只有内存显存参数是稳定可靠的。更多参数设置，请参考[参数设置说明](#参数设置说明)

## 4. 各个硬件上的一键运行脚本  

在准备好相关的环境配置和SDK后，可以使用本目录提供的脚本一键运行后的benchmark数据。
- 获取模型和资源文件  
```bash
./get_models.sh
```  
- 运行benchmark脚本  
```bash
# x86 CPU Paddle backend fp32
./benchmark_x86.sh config/config.x86.paddle.fp32.txt
# x86 CPU ONNXRuntime backend fp32
./benchmark_x86.sh config/config.x86.ort.fp32.txt
# x86 CPU OpenVIVO backend fp32
./benchmark_x86.sh config/config.x86.ov.fp32.txt
# NVIDIA GPU Paddle backend fp32
./benchmark_gpu.sh config/config.gpu.paddle.fp32.txt
# NVIDIA GPU ONNXRuntime backend fp32
./benchmark_gpu.sh config/config.gpu.ort.fp32.txt
# NVIDIA GPU Paddle-TRT backend fp32
./benchmark_gpu_trt.sh config/config.gpu.paddle_trt.fp32.txt
# NVIDIA GPU Paddle-TRT backend fp16
./benchmark_gpu_trt.sh config/config.gpu.paddle_trt.fp16.txt
# NVIDIA GPU TRT backend fp32
./benchmark_gpu_trt.sh config/config.gpu.trt.fp32.txt
# NVIDIA GPU TRT backend fp16
./benchmark_gpu_trt.sh config/config.gpu.trt.fp16.txt

# Arm CPU Paddle Lite backend fp32
./benchmark_arm.sh config/config.arm.lite.fp32.txt
# Arm CPU Paddle Lite backend fp16
./benchmark_arm.sh config/config.arm.lite.fp16.txt
# XPU Paddle Lite backend fp32
./benchmark_xpu.sh config/config.xpu.lite.fp32.txt
```
