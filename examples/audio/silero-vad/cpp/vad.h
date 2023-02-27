// Copyright (c) 2023 Chen Qianhe Authors. All Rights Reserved.
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
#include <vector>
#include <mutex>
#include "fastdeploy/fastdeploy_model.h"
#include "fastdeploy/runtime.h"
#include "./wav.h"

class Vad : public fastdeploy::FastDeployModel {
 public:
  Vad(const std::string& model_file,
      const fastdeploy::RuntimeOption& custom_option =
          fastdeploy::RuntimeOption()) {
    valid_cpu_backends = {fastdeploy::Backend::ORT,
                          fastdeploy::Backend::OPENVINO};
    valid_gpu_backends = {fastdeploy::Backend::ORT, fastdeploy::Backend::TRT};

    runtime_option = custom_option;
    // ORT backend
    runtime_option.UseCpu();
    runtime_option.UseOrtBackend();
    runtime_option.model_format = fastdeploy::ModelFormat::ONNX;
    // grap opt level
    runtime_option.ort_option.graph_optimization_level = 99;
    // one-thread
    runtime_option.ort_option.intra_op_num_threads = 1;
    runtime_option.ort_option.inter_op_num_threads = 1;
    // model path
    runtime_option.model_file = model_file;
  }

  void Init() {
    std::call_once(init_, [&]() {
      initialized = Initialize(); 
    });
  }

  void Reset();

  void SetConfig(int sr, int frame_ms, float threshold,
                     int min_silence_duration_ms, int speech_pad_left_ms, int speech_pad_right_ms);

  void Pcm2Float(const char* pcm_bytes);

  void LoadWav(const std::string& wavPath);

  bool Predict();

  //std::vector<std::map<std::string, float>>
  //getResult(float removeThreshold = 1.6, float expandHeadThreshold = 0.32,
  //          float expandTailThreshold = 0, float mergeThreshold = 0.3);
  std::vector<std::map<std::string, float>>
  GetResult(float removeThreshold = 0.0, float expandHeadThreshold = 0.0,
            float expandTailThreshold = 0, float mergeThreshold = 0.0);

  int SampleRate() const { return sample_rate_; }

  int FrameMs() const { return frame_ms_; }

  float Threshold() const { return threshold_; }

  const wav::WavReader& WavReader() const { return wavReader_; }

  const std::vector<float>& InputWav() const { return inputWav_; }

  int64_t WindowSizeSamples() const { return window_size_samples_; }

  int MinSilenceDurationMs() const { return min_silence_samples_ / sample_rate_; }
  int SpeechPadLeftMs() const { return speech_pad_left_samples_ / sample_rate_ ; }
  int SpeechPadRightMs() const { return speech_pad_right_samples_ / sample_rate_ ; }

  int MinSilenceSamples() const { return min_silence_samples_; }
  int SpeechPadLeftSamples() const { return speech_pad_left_samples_; }
  int SpeechPadRightSamples() const { return speech_pad_right_samples_; }

  std::string ModelName() const override { return "VAD"; }

 private:
  bool Initialize();

  bool ForwardChunk(std::vector<float>& chunk);

  bool Postprocess();

 private:
  std::once_flag init_;
  // input and output
  std::vector<fastdeploy::FDTensor> inputTensors_;
  std::vector<fastdeploy::FDTensor> outputTensors_;

  // model states
  bool triggerd_ = false;
  unsigned int speech_start_ = 0;
  unsigned int speech_end_ = 0;
  unsigned int temp_end_ = 0;
  unsigned int current_sample_ = 0;
  unsigned int current_chunk_size_ = 0;
  // MAX 4294967295 samples / 8sample per ms / 1000 / 60 = 8947 minutes
  float outputProb_;

  /* ======================================================================== */

  // input wav data
  wav::WavReader wavReader_;
  std::vector<float> inputWav_; // [0, 1]

  /* ======================================================================== */
  int sample_rate_ = 16000;
  int frame_ms_ = 32;  // 32, 64, 96 for 16k
  float threshold_ = 0.5f;

  int64_t window_size_samples_; // support 256 512 768 for 8k; 512 1024 1536 for 16k.
  int sr_per_ms_;            // support 8 or 16
  int min_silence_samples_;  // sr_per_ms_ * frame_ms_
  int speech_pad_left_samples_{0};    // usually 250ms
  int speech_pad_right_samples_{0};   // usually 0

  /* ======================================================================== */

  std::vector<float> input_;
  std::vector<int64_t> sr_;
  const size_t size_hc_ = 2 * 1 * 64;  // It's FIXED.
  std::vector<float> h_;
  std::vector<float> c_;

  std::vector<int64_t> input_node_dims_;
  const std::vector<int64_t> sr_node_dims_ = {1};
  const std::vector<int64_t> hc_node_dims_ = {2, 1, 64};

  /* ======================================================================== */

  std::vector<float> speakStart_;
  std::vector<float> speakEnd_;
};
