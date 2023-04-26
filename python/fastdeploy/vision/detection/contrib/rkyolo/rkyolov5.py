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
from ..... import FastDeployModel, ModelFormat
from ..... import c_lib_wrap as C


class RKYOLOPreprocessor:
    def __init__(self):
        """Create a preprocessor for RKYOLOV5
        """
        self._preprocessor = C.vision.detection.RKYOLOPreprocessor()

    def run(self, input_ims):
        """Preprocess input images for RKYOLOV5

        :param: input_ims: (list of numpy.ndarray)The input image
        :return: list of FDTensor
        """
        return self._preprocessor.run(input_ims)

    @property
    def size(self):
        """
        Argument for image preprocessing step, the preprocess image size, tuple of (width, height), default size = [640, 640]
        """
        return self._preprocessor.size

    @property
    def padding_value(self):
        """
        padding value for preprocessing, default [114.0, 114.0, 114.0]
        """
        #  padding value, size should be the same as channels
        return self._preprocessor.padding_value

    @property
    def is_scale_up(self):
        """
        is_scale_up for preprocessing, the input image only can be zoom out, the maximum resize scale cannot exceed 1.0, default true
        """
        return self._preprocessor.is_scale_up

    @size.setter
    def size(self, wh):
        assert isinstance(wh, (list, tuple)), \
            "The value to set `size` must be type of tuple or list."
        assert len(wh) == 2, \
            "The value to set `size` must contatins 2 elements means [width, height], but now it contains {} elements.".format(
                len(wh))
        self._preprocessor.size = wh

    @padding_value.setter
    def padding_value(self, value):
        assert isinstance(
            value,
            list), "The value to set `padding_value` must be type of list."
        self._preprocessor.padding_value = value

    @is_scale_up.setter
    def is_scale_up(self, value):
        assert isinstance(
            value,
            bool), "The value to set `is_scale_up` must be type of bool."
        self._preprocessor.is_scale_up = value


class RKYOLOPostprocessor:
    def __init__(self):
        """Create a postprocessor for RKYOLOV5
        """
        self._postprocessor = C.vision.detection.RKYOLOPostprocessor()

    def run(self, runtime_results):
        """Postprocess the runtime results for RKYOLOV5

        :param: runtime_results: (list of FDTensor)The output FDTensor results from runtime
        :param: ims_info: (list of dict)Record input_shape and output_shape
        :return: list of DetectionResult(If the runtime_results is predict by batched samples, the length of this list equals to the batch size)
        """
        return self._postprocessor.run(runtime_results)

    def set_anchor(self, anchor):
        self._postprocessor.set_anchor(anchor)

    @property
    def conf_threshold(self):
        """
        confidence threshold for postprocessing, default is 0.25
        """
        return self._postprocessor.conf_threshold

    @property
    def nms_threshold(self):
        """
        nms threshold for postprocessing, default is 0.5
        """
        return self._postprocessor.nms_threshold

    @property
    def class_num(self):
        """
        class_num for postprocessing, default is 80
        """
        return self._postprocessor.class_num

    @conf_threshold.setter
    def conf_threshold(self, conf_threshold):
        assert isinstance(conf_threshold, float), \
            "The value to set `conf_threshold` must be type of float."
        self._postprocessor.conf_threshold = conf_threshold

    @nms_threshold.setter
    def nms_threshold(self, nms_threshold):
        assert isinstance(nms_threshold, float), \
            "The value to set `nms_threshold` must be type of float."
        self._postprocessor.nms_threshold = nms_threshold

    @class_num.setter
    def class_num(self, class_num):
        """
        class_num for postprocessing, default is 80
        """
        assert isinstance(class_num, int), \
            "The value to set `nms_threshold` must be type of float."
        self._postprocessor.class_num = class_num


class RKYOLOV5(FastDeployModel):
    def __init__(self,
                 model_file,
                 runtime_option=None,
                 model_format=ModelFormat.RKNN):
        """Load a RKYOLOV5 model exported by RKYOLOV5.

        :param model_file: (str)Path of model file, e.g ./yolov5.rknn
        :param params_file: (str)Path of parameters file, e.g , if the model_fomat is ModelFormat.ONNX, this param will be ignored, can be set as empty string
        :param runtime_option: (fastdeploy.RuntimeOption)RuntimeOption for inference this model, if it's None, will use the default backend on CPU
        :param model_format: (fastdeploy.ModelForamt)Model format of the loaded model
        """
        # 调用基函数进行backend_option的初始化
        # 初始化后的option保存在self._runtime_option
        super(RKYOLOV5, self).__init__(runtime_option)

        self._model = C.vision.detection.RKYOLOV5(
            model_file, self._runtime_option, model_format)
        # 通过self.initialized判断整个模型的初始化是否成功
        assert self.initialized, "RKYOLOV5 initialize failed."

    def predict(self, input_image, conf_threshold=0.25, nms_iou_threshold=0.5):
        """Detect an input image

        :param input_image: (numpy.ndarray)The input image data, 3-D array with layout HWC, BGR format
        :param conf_threshold: confidence threshold for postprocessing, default is 0.25
        :param nms_iou_threshold: iou threshold for NMS, default is 0.5
        :return: DetectionResult
        """

        self.postprocessor.conf_threshold = conf_threshold
        self.postprocessor.nms_threshold = nms_iou_threshold
        return self._model.predict(input_image)

    def batch_predict(self, images):
        """Classify a batch of input image

        :param im: (list of numpy.ndarray) The input image list, each element is a 3-D array with layout HWC, BGR format
        :return list of DetectionResult
        """

        return self._model.batch_predict(images)

    @property
    def preprocessor(self):
        """Get RKYOLOV5Preprocessor object of the loaded model

        :return RKYOLOV5Preprocessor
        """
        return self._model.preprocessor

    @property
    def postprocessor(self):
        """Get RKYOLOV5Postprocessor object of the loaded model

        :return RKYOLOV5Postprocessor
        """
        return self._model.postprocessor


class RKYOLOX(FastDeployModel):
    def __init__(self,
                 model_file,
                 runtime_option=None,
                 model_format=ModelFormat.RKNN):
        """Load a RKYOLOX model exported by RKYOLOX.

        :param model_file: (str)Path of model file, e.g ./yolox.rknn
        :param runtime_option: (fastdeploy.RuntimeOption)RuntimeOption for inference this model, if it's None, will use the default backend on CPU
        :param model_format: (fastdeploy.ModelForamt)Model format of the loaded model
        """
        # 调用基函数进行backend_option的初始化
        # 初始化后的option保存在self._runtime_option
        super(RKYOLOX, self).__init__(runtime_option)

        self._model = C.vision.detection.RKYOLOX(
            model_file, self._runtime_option, model_format)
        # 通过self.initialized判断整个模型的初始化是否成功
        assert self.initialized, "RKYOLOV5 initialize failed."

    def predict(self, input_image, conf_threshold=0.25, nms_iou_threshold=0.5):
        """Detect an input image

        :param input_image: (numpy.ndarray)The input image data, 3-D array with layout HWC, BGR format
        :param conf_threshold: confidence threshold for postprocessing, default is 0.25
        :param nms_iou_threshold: iou threshold for NMS, default is 0.5
        :return: DetectionResult
        """

        self.postprocessor.conf_threshold = conf_threshold
        self.postprocessor.nms_threshold = nms_iou_threshold
        return self._model.predict(input_image)

    def batch_predict(self, images):
        """Classify a batch of input image

        :param im: (list of numpy.ndarray) The input image list, each element is a 3-D array with layout HWC, BGR format
        :return list of DetectionResult
        """

        return self._model.batch_predict(images)

    @property
    def preprocessor(self):
        """Get RKYOLOV5Preprocessor object of the loaded model

        :return RKYOLOV5Preprocessor
        """
        return self._model.preprocessor

    @property
    def postprocessor(self):
        """Get RKYOLOV5Postprocessor object of the loaded model

        :return RKYOLOV5Postprocessor
        """
        return self._model.postprocessor


class RKYOLOV7(FastDeployModel):
    def __init__(self,
                 model_file,
                 runtime_option=None,
                 model_format=ModelFormat.RKNN):
        """Load a RKYOLOX model exported by RKYOLOV7.

        :param model_file: (str)Path of model file, e.g ./yolov7.rknn
        :param runtime_option: (fastdeploy.RuntimeOption)RuntimeOption for inference this model, if it's None, will use the default backend on CPU
        :param model_format: (fastdeploy.ModelForamt)Model format of the loaded model
        """
        # 调用基函数进行backend_option的初始化
        # 初始化后的option保存在self._runtime_option
        super(RKYOLOV7, self).__init__(runtime_option)

        self._model = C.vision.detection.RKYOLOV7(
            model_file, self._runtime_option, model_format)
        # 通过self.initialized判断整个模型的初始化是否成功
        assert self.initialized, "RKYOLOV5 initialize failed."

    def predict(self, input_image, conf_threshold=0.25, nms_iou_threshold=0.5):
        """Detect an input image

        :param input_image: (numpy.ndarray)The input image data, 3-D array with layout HWC, BGR format
        :param conf_threshold: confidence threshold for postprocessing, default is 0.25
        :param nms_iou_threshold: iou threshold for NMS, default is 0.5
        :return: DetectionResult
        """

        self.postprocessor.conf_threshold = conf_threshold
        self.postprocessor.nms_threshold = nms_iou_threshold
        return self._model.predict(input_image)

    def batch_predict(self, images):
        """Classify a batch of input image

        :param im: (list of numpy.ndarray) The input image list, each element is a 3-D array with layout HWC, BGR format
        :return list of DetectionResult
        """

        return self._model.batch_predict(images)

    @property
    def preprocessor(self):
        """Get RKYOLOV5Preprocessor object of the loaded model

        :return RKYOLOV5Preprocessor
        """
        return self._model.preprocessor

    @property
    def postprocessor(self):
        """Get RKYOLOV5Postprocessor object of the loaded model

        :return RKYOLOV5Postprocessor
        """
        return self._model.postprocessor
