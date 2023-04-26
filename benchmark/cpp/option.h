// Copyright (c) 2023 PaddlePaddle Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#pragma once

#include "fastdeploy/vision.h"

static bool CreateRuntimeOption(fastdeploy::RuntimeOption* option,
                        int argc, char* argv[], bool remove_flags) {
  google::ParseCommandLineFlags(&argc, &argv, remove_flags);
  option->DisableValidBackendCheck();
  std::unordered_map<std::string, std::string> config_info;
  fastdeploy::benchmark::ResultManager::LoadBenchmarkConfig(
                            FLAGS_config_path, &config_info);
  int warmup = std::stoi(config_info["warmup"]);
  int repeat = std::stoi(config_info["repeat"]);
  if (FLAGS_warmup != -1) {
    warmup = FLAGS_warmup;
  }
  if (FLAGS_repeat != -1) {
    repeat = FLAGS_repeat;
  }
  if (config_info["profile_mode"] == "runtime") {
    option->EnableProfiling(config_info["include_h2d_d2h"] == "true",
                            repeat, warmup);
  }
  if (config_info["device"] == "gpu") {
    option->UseGpu(std::stoi(config_info["device_id"]));
    if (config_info["backend"] == "ort") {
      option->UseOrtBackend();
    } else if (config_info["backend"] == "paddle") {
      option->UsePaddleInferBackend();
    } else if (config_info["backend"] == "trt" ||
               config_info["backend"] == "paddle_trt") {
      option->trt_option.serialize_file = FLAGS_model +
                                          sep + "trt_serialized.trt";
      option->UseTrtBackend();
      if (config_info["backend"] == "paddle_trt") {
        option->UsePaddleInferBackend();
        option->paddle_infer_option.enable_trt = true;
      }
      if (config_info["use_fp16"] == "true") {
        option->trt_option.enable_fp16 = true;
      }
    } else if (config_info["backend"] == "default") {
      PrintBenchmarkInfo(config_info);
      return true;
    } else {
      std::cout << "While inference with GPU, only support "
                   "default/ort/paddle/trt/paddle_trt now, "
                << config_info["backend"] << " is not supported." << std::endl;
      PrintUsage();
      return false;
    }
  } else if (config_info["device"] == "cpu") {
    option->SetCpuThreadNum(std::stoi(config_info["cpu_thread_nums"]));
    if (config_info["backend"] == "ort") {
      option->UseOrtBackend();
    } else if (config_info["backend"] == "ov") {
      option->UseOpenVINOBackend();
    } else if (config_info["backend"] == "paddle") {
      option->UsePaddleInferBackend();
    } else if (config_info["backend"] == "lite") {
      option->UsePaddleLiteBackend();
      if (config_info["use_fp16"] == "true") {
        option->paddle_lite_option.enable_fp16 = true;
      }
    } else if (config_info["backend"] == "default") {
      PrintBenchmarkInfo(config_info);
      return true;
    } else {
      std::cout << "While inference with CPU, only support "
                   "default/ort/ov/paddle/lite now, "
                << config_info["backend"] << " is not supported." << std::endl;
      PrintUsage();
      return false;
    }
  } else if (config_info["device"] == "xpu") {
    if (FLAGS_xpu_l3_cache >= 0) {
       option->UseKunlunXin(std::stoi(config_info["device_id"]),
                                      FLAGS_xpu_l3_cache);
    } else {
      option->UseKunlunXin(std::stoi(config_info["device_id"]),
                           std::stoi(config_info["xpu_l3_cache"]));
    }
    if (config_info["backend"] == "ort") {
      option->UseOrtBackend();
    } else if (config_info["backend"] == "paddle") {
      option->UsePaddleInferBackend();
    } else if (config_info["backend"] == "lite") {
      option->UsePaddleLiteBackend();
      if (config_info["use_fp16"] == "true") {
        option->paddle_lite_option.enable_fp16 = true;
      }
    } else if (config_info["backend"] == "default") {
      PrintBenchmarkInfo(config_info);
      return true;
    } else {
      std::cout << "While inference with XPU, only support "
                   "default/ort/paddle/lite now, "
                << config_info["backend"] << " is not supported." << std::endl;
      PrintUsage();
      return false;
    }
  } else {
    std::cerr << "Only support device CPU/GPU/XPU now, "
              << config_info["device"]
              << " is not supported." << std::endl;
    PrintUsage();
    return false;
  }
  PrintBenchmarkInfo(config_info);
  return true;
}
