# copyright (c) 2024 PaddlePaddle Authors. All Rights Reserve.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Any, Dict, Optional, Union, List
import numpy as np
from ...utils.pp_option import PaddlePredictorOption
from ..base import BasePipeline

from ...models.video_detection.result import DetVideoResult


class VideoDetectionPipeline(BasePipeline):
    """Video detection Pipeline"""

    entities = "video_detection"

    def __init__(
        self,
        config: Dict,
        device: str = None,
        pp_option: PaddlePredictorOption = None,
        use_hpip: bool = False,
    ) -> None:
        """
        Initializes the class with given configurations and options.

        Args:
            config (Dict): Configuration dictionary containing model and other parameters.
            device (str): The device to run the prediction on. Default is None.
            pp_option (PaddlePredictorOption): Options for PaddlePaddle predictor. Default is None.
            use_hpip (bool): Whether to use high-performance inference (hpip) for prediction. Defaults to False.
        """
        super().__init__(device=device, pp_option=pp_option, use_hpip=use_hpip)

        video_detection_model_config = config["SubModules"]["VideoDetection"]
        model_kwargs = {}
        if "nms_thresh" in video_detection_model_config:
            model_kwargs["nms_thresh"] = video_detection_model_config["nms_thresh"]
        if "score_thresh" in video_detection_model_config:
            model_kwargs["score_thresh"] = video_detection_model_config["score_thresh"]
        self.video_detection_model = self.create_model(video_detection_model_config, **model_kwargs)

    def predict(
        self,
        input: Union[str, List[str], np.ndarray, List[np.ndarray]],
        nms_thresh: float = 0.5,
        score_thresh: float = 0.4,
        **kwargs
    ) -> DetVideoResult:
        """Predicts video detection results for the given input.

        Args:
            input (Union[str, list[str], np.ndarray, list[np.ndarray]]): The input image(s) or path(s) to the images.
            **kwargs: Additional keyword arguments that can be passed to the function.

        Returns:
            DetVideoResult: The predicted video detection results.
        """

        yield from self.video_detection_model(
            input, nms_thresh=nms_thresh, score_thresh=score_thresh
        )
