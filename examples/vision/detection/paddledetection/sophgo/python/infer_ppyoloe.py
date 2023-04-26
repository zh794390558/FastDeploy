# Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import fastdeploy as fd
import cv2
import os
from subprocess import run
from prepare_npz import prepare

def parse_arguments():
    import argparse
    import ast
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--auto", required=True, help="Auto download, convert, compile and infer if True")
    parser.add_argument(
        "--pp_detect_path", default='/workspace/PaddleDetection', help="Path of PaddleDetection folder")
    parser.add_argument(
        "--model_file", required=True, help="Path of sophgo model.")
    parser.add_argument("--config_file", required=True, help="Path of config.")
    parser.add_argument(
        "--image", type=str, required=True, help="Path of test image file.")
    return parser.parse_args()

def export_model(args):
    PPDetection_path = args.pp_detect_path
    export_str = 'python3 tools/export_model.py \
                -c configs/ppyoloe/ppyoloe_crn_s_300e_coco.yml \
                -output_dir=output_inference \
                -o weights=https://paddledet.bj.bcebos.com/models/ppyoloe_crn_s_300e_coco.pdparams'
    cur_path = os.getcwd()
    os.chdir(PPDetection_path)
    print(export_str)
    run(export_str, shell=True)
    cp_str = 'cp -r ./output_inference/ppyoloe_crn_s_300e_coco ' + cur_path
    print(cp_str)
    run(cp_str, shell=True)
    os.chdir(cur_path)

def paddle2onnx():
    convert_str = 'paddle2onnx --model_dir ppyoloe_crn_s_300e_coco \
                --model_filename model.pdmodel \
                --params_filename model.pdiparams \
                --save_file ppyoloe_crn_s_300e_coco.onnx \
                --enable_dev_version True'
    print(convert_str)
    run(convert_str, shell=True)
    fix_shape_str = 'python3 -m paddle2onnx.optimize --input_model ppyoloe_crn_s_300e_coco.onnx \
                                --output_model ppyoloe_crn_s_300e_coco.onnx \
                                --input_shape_dict "{\'image\':[1,3,640,640]}"'
    print(fix_shape_str)
    run(fix_shape_str, shell=True)

def mlir_prepare():
    mlir_path = os.getenv("MODEL_ZOO_PATH")
    mlir_path = mlir_path[:-13]
    regression_path = os.path.join(mlir_path, 'regression')
    mv_str_list = ['mkdir ppyoloe', 
                'cp -rf ' + os.path.join(regression_path, 'dataset/COCO2017/') + ' ./ppyoloe', 
                'cp -rf ' + os.path.join(regression_path, 'image/') + ' ./ppyoloe',
                'cp ppyoloe_crn_s_300e_coco.onnx ./ppyoloe',
                'mkdir ./ppyoloe/workspace']
    for str in mv_str_list:
        print(str)
        run(str, shell=True)

def image_prepare():
    img_str = 'wget https://gitee.com/paddlepaddle/PaddleDetection/raw/release/2.4/demo/000000014439.jpg'
    if not os.path.exists('000000014439.jpg'):
        print(img_str)
        run(img_str, shell=True)
    prepare('000000014439.jpg', [640, 640])
    cp_npz_str = 'cp ./inputs.npz ./ppyoloe'
    print(cp_npz_str)
    run(cp_npz_str, shell=True)

def onnx2mlir():
    transform_str = 'model_transform.py \
            --model_name ppyoloe_crn_s_300e_coco \
            --model_def ../ppyoloe_crn_s_300e_coco.onnx \
            --input_shapes [[1,3,640,640],[1,2]] \
            --keep_aspect_ratio \
            --pixel_format rgb \
            --output_names p2o.Div.1,p2o.Concat.29 \
            --test_input ../inputs.npz \
            --test_result ppyoloe_crn_s_300e_coco_top_outputs.npz \
            --mlir ppyoloe_crn_s_300e_coco.mlir'
    os.chdir('./ppyoloe/workspace')
    print(transform_str)
    run(transform_str, shell=True)
    os.chdir('../../')

def mlir2bmodel():
    deploy_str = 'model_deploy.py \
            --mlir ppyoloe_crn_s_300e_coco.mlir \
            --quantize F32 \
            --chip bm1684x \
            --test_input ppyoloe_crn_s_300e_coco_in_f32.npz \
            --test_reference ppyoloe_crn_s_300e_coco_top_outputs.npz \
            --model ppyoloe_crn_s_300e_coco_1684x_f32.bmodel'
    os.chdir('./ppyoloe/workspace')
    print(deploy_str)
    run(deploy_str, shell=True)
    os.chdir('../../')

if __name__ == "__main__":
    args = parse_arguments()

    if args.auto:
        export_model(args)
        paddle2onnx()
        mlir_prepare()
        image_prepare()
        onnx2mlir()
        mlir2bmodel()

    model_file = './ppyoloe/workspace/ppyoloe_crn_s_300e_coco_1684x_f32.bmodel' if args.auto else args.model_file
    params_file = ""
    config_file = './ppyoloe_crn_s_300e_coco/infer_cfg.yml' if args.auto else args.config_file
    image_file = './000000014439.jpg' if args.auto else args.image

    # 配置runtime，加载模型
    runtime_option = fd.RuntimeOption()
    runtime_option.use_sophgo()

    model = fd.vision.detection.PPYOLOE(
        model_file,
        params_file,
        config_file,
        runtime_option=runtime_option,
        model_format=fd.ModelFormat.SOPHGO)

    model.postprocessor.apply_nms()

    # 预测图片分割结果
    im = cv2.imread(image_file)
    result = model.predict(im)
    print(result)

    # 可视化结果
    vis_im = fd.vision.vis_detection(im, result, score_threshold=0.5)
    cv2.imwrite("sophgo_result.jpg", vis_im)
    print("Visualized result save in ./sophgo_result_ppyoloe.jpg")
