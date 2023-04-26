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

from __future__ import absolute_import
import logging
from .... import FastDeployModel, ModelFormat
from .... import c_lib_wrap as C


class SmokePreprocessor:
    def __init__(self, config_file):
        """Create a preprocessor for Smoke
        """
        self._preprocessor = C.vision.perception.SmokePreprocessor(config_file)

    def run(self, input_ims):
        """Preprocess input images for Smoke

        :param: input_ims: (list of numpy.ndarray)The input image
        :return: list of FDTensor
        """
        return self._preprocessor.run(input_ims)


class SmokePostprocessor:
    def __init__(self):
        """Create a postprocessor for Smoke
        """
        self._postprocessor = C.vision.perception.SmokePostprocessor()

    def run(self, runtime_results):
        """Postprocess the runtime results for Smoke

        :param: runtime_results: (list of FDTensor)The output FDTensor results from runtime
        :return: list of PerceptionResult(If the runtime_results is predict by batched samples, the length of this list equals to the batch size)
        """
        return self._postprocessor.run(runtime_results)


class Smoke(FastDeployModel):
    def __init__(self,
                 model_file,
                 params_file,
                 config_file,
                 runtime_option=None,
                 model_format=ModelFormat.PADDLE):
        """Load a SMoke model exported by Smoke.

        :param model_file: (str)Path of model file, e.g ./smoke.pdmodel
        :param params_file: (str)Path of parameters file, e.g ./smoke.pdiparams
        :param config_file: (str)Path of config file, e.g ./infer_cfg.yaml
        :param runtime_option: (fastdeploy.RuntimeOption)RuntimeOption for inference this model, if it's None, will use the default backend on CPU
        :param model_format: (fastdeploy.ModelForamt)Model format of the loaded model
        """
        super(Smoke, self).__init__(runtime_option)

        self._model = C.vision.perception.Smoke(
            model_file, params_file, config_file, self._runtime_option,
            model_format)
        assert self.initialized, "Smoke initialize failed."

    def predict(self, input_image):
        """Detect an input image

        :param input_image: (numpy.ndarray)The input image data, 3-D array with layout HWC, BGR format
        :param conf_threshold: confidence threshold for postprocessing, default is 0.25
        :param nms_iou_threshold: iou threshold for NMS, default is 0.5
        :return: PerceptionResult
        """
        return self._model.predict(input_image)

    def batch_predict(self, images):
        """Classify a batch of input image

        :param im: (list of numpy.ndarray) The input image list, each element is a 3-D array with layout HWC, BGR format
        :return list of PerceptionResult
        """

        return self._model.batch_predict(images)

    @property
    def preprocessor(self):
        """Get SmokePreprocessor object of the loaded model

        :return SmokePreprocessor
        """
        return self._model.preprocessor

    @property
    def postprocessor(self):
        """Get SmokePostprocessor object of the loaded model

        :return SmokePostprocessor
        """
        return self._model.postprocessor
