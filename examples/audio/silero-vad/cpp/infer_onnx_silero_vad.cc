#include <iostream>

#include "vad.h"

int main(int argc, char* argv[]) {
  if (argc < 3) {
    std::cout << "Usage: infer_onnx_silero_vad path/to/model path/to/audio "
                 "run_option, "
                 "e.g ./infer_onnx_silero_vad silero_vad.onnx sample.wav"
              << std::endl;
    return -1;
  }

  std::string model_file = argv[1];
  std::string audio_file = argv[2];

  Vad vad(model_file);
  // custom config, but must be set before init
  vad.SetConfig(16000, 32, 0.45f, 200, 0, 0);
  vad.Init();
  vad.LoadWav(audio_file);
  vad.Predict();
  std::vector<std::map<std::string, float>> result = vad.GetResult();
  for (auto& res : result) {
    std::cout << "speak start: " << res["start"] << " s, end: " << res["end"]
              << " s | ";
  }
  std::cout << std::endl;

  return 0;
}
