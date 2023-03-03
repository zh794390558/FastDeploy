#!/bin/bash

# https://github.com/PaddlePaddle/X2Paddle/blob/develop/docs/inference_model_convertor/convert2lite_api.md

if [ $# != 1 ];then
    echo "usage: $0 onnx-model"
    exit -1
fi

onnx_model=$1


# lite_valid_places参数目前可支持 arm、 opencl、 x86、 metal、 xpu、 bm、 mlu、 intel_fpga、 huawei_ascend_npu、imagination_nna、 rockchip_npu、 mediatek_apu、 huawei_kirin_npu、 amlogic_npu，可以同时指定多个硬件平台(以逗号分隔，优先级高的在前)，opt 将会自动选择最佳方式。如果需要支持华为麒麟 NPU，应当设置为 "huawei_kirin_npu,arm"。

x2paddle --framework=onnx --model=$onnx_model --save_dir=pd_model --to_lite=True --lite_valid_places=arm --lite_model_type=naive_buffer
