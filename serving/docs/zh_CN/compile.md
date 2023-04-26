中文 ｜ [English](../EN/compile-en.md)
# 服务化部署编译

## 制作服务化部署镜像

### 制作GPU镜像

FastDploy发布的GPU镜像基于[Triton Inference Server](https://github.com/triton-inference-server/server)的21.10版本进行制作，如果有其他CUDA版本需求，可以参照[NVIDIA 官网](https://docs.nvidia.com/deeplearning/frameworks/support-matrix/index.html)中展示的版本信息修改Dockerfile和scripts中的脚本.

```
# 进入serving目录执行脚本编译fastdeploy和服务化的backend
cd serving
bash scripts/build.sh

# 退出到FastDeploy主目录，制作镜像
# x.y.z为FastDeploy版本号，可根据情况自己确定。比如: 1.0.5
cd ../
docker build -t paddlepaddle/fastdeploy:x.y.z-gpu-cuda11.4-trt8.5-21.10 -f serving/Dockerfile .
```

目前默认 TensorRT 版本为 8.5.2.2，如果需要切换 TensorRT 版本，则可执行以下编译命令：

```
cd serving
bash scripts/build.sh -tv 8.4.1.5

cd ../
docker build -t paddlepaddle/fastdeploy:x.y.z-gpu-cuda11.4-trt8.5-21.10 -f serving/Dockerfile_CUDA_11_4_TRT_8_4 .
```

比如在ubuntu 20.04，cuda11.2环境下制作基于FastDeploy v1.0.5的GPU镜像
```
# 进入serving目录执行脚本编译fastdeploy和服务化的backend
cd serving
bash scripts/build_fd_cuda_11_2.sh

# 退出到FastDeploy主目录，制作镜像
cd ../
docker build -t paddlepaddle/fastdeploy:1.0.5-gpu-cuda11.2-trt8.4-21.10 -f serving/Dockerfile_CUDA_11_2 .
```

### 制作CPU镜像

```
# 进入serving目录执行脚本编译fastdeploy和服务化的backend
cd serving
bash scripts/build.sh OFF

# 退出到FastDeploy主目录，制作镜像
# x.y.z为FastDeploy版本号，可根据情况自己确定。比如: 1.0.5
cd ../
docker build -t paddlepaddle/fastdeploy:x.y.z-cpu-only-21.10 -f serving/Dockerfile_cpu .
```

### 制作IPU镜像

```
# 进入serving目录执行脚本编译fastdeploy和服务化的backend
cd serving
bash scripts/build_fd_ipu.sh

# 退出到FastDeploy主目录，制作镜像
# x.y.z为FastDeploy版本号，可根据情况自己确定。比如: 1.0.5
cd ../
docker build -t paddlepaddle/fastdeploy:x.y.z-ipu-only-21.10 -f serving/Dockerfile_ipu .
```

## 非镜像方式编译

- [FastDeploy Serving CentOS编译教程](./compile_without_docker_centos.md)
