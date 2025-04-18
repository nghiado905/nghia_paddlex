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

import numpy as np
from typing import List, Union

from ....utils.func_register import FuncRegister
from ....modules.text_detection.model_list import MODELS
from ...common.batch_sampler import ImageBatchSampler
from ...common.reader import ReadImage
from ..common import (
    Resize,
    ResizeByShort,
    Normalize,
    ToCHWImage,
    ToBatch,
    StaticInfer,
)
from ..base import BasicPredictor
from .processors import DetResizeForTest, NormalizeImage, DBPostProcess
from .result import TextDetResult


class TextDetPredictor(BasicPredictor):

    entities = MODELS

    _FUNC_MAP = {}
    register = FuncRegister(_FUNC_MAP)

    def __init__(
        self,
        limit_side_len: Union[int, None] = None,
        limit_type: Union[str, None] = None,
        thresh: Union[float, None] = None,
        box_thresh: Union[float, None] = None,
        unclip_ratio: Union[float, None] = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.limit_side_len = limit_side_len
        self.limit_type = limit_type
        self.thresh = thresh
        self.box_thresh = box_thresh
        self.unclip_ratio = unclip_ratio
        self.pre_tfs, self.infer, self.post_op = self._build()

    def _build_batch_sampler(self):
        return ImageBatchSampler()

    def _get_result_class(self):
        return TextDetResult

    def _build(self):
        pre_tfs = {"Read": ReadImage(format="RGB")}

        for cfg in self.config["PreProcess"]["transform_ops"]:
            tf_key = list(cfg.keys())[0]
            func = self._FUNC_MAP[tf_key]
            args = cfg.get(tf_key, {})
            name, op = func(self, **args) if args else func(self)
            if op:
                pre_tfs[name] = op
        pre_tfs["ToBatch"] = ToBatch()

        infer = StaticInfer(
            model_dir=self.model_dir,
            model_prefix=self.MODEL_FILE_PREFIX,
            option=self.pp_option,
        )

        post_op = self.build_postprocess(**self.config["PostProcess"])
        return pre_tfs, infer, post_op

    def process(
        self,
        batch_data: List[Union[str, np.ndarray]],
        limit_side_len: Union[int, None] = None,
        limit_type: Union[str, None] = None,
        thresh: Union[float, None] = None,
        box_thresh: Union[float, None] = None,
        unclip_ratio: Union[float, None] = None,
    ):

        batch_raw_imgs = self.pre_tfs["Read"](imgs=batch_data.instances)
        batch_imgs, batch_shapes = self.pre_tfs["Resize"](
            imgs=batch_raw_imgs,
            limit_side_len=limit_side_len or self.limit_side_len,
            limit_type=limit_type or self.limit_type,
        )
        batch_imgs = self.pre_tfs["Normalize"](imgs=batch_imgs)
        batch_imgs = self.pre_tfs["ToCHW"](imgs=batch_imgs)
        x = self.pre_tfs["ToBatch"](imgs=batch_imgs)
        batch_preds = self.infer(x=x)
        polys, scores = self.post_op(
            batch_preds,
            batch_shapes,
            thresh=thresh or self.thresh,
            box_thresh=box_thresh or self.box_thresh,
            unclip_ratio=unclip_ratio or self.unclip_ratio,
        )
        return {
            "input_path": batch_data.input_paths,
            "page_index": batch_data.page_indexes,
            "input_img": batch_raw_imgs,
            "dt_polys": polys,
            "dt_scores": scores,
        }

    @register("DecodeImage")
    def build_readimg(self, channel_first, img_mode):
        assert channel_first == False
        return "Read", ReadImage(format=img_mode)

    @register("DetResizeForTest")
    def build_resize(
        self,
        limit_side_len: Union[int, None] = None,
        limit_type: Union[str, None] = None,
        **kwargs
    ):
        # TODO: align to PaddleOCR

        if self.model_name in (
            "PP-OCRv4_server_det",
            "PP-OCRv4_mobile_det",
            "PP-OCRv3_server_det",
            "PP-OCRv3_mobile_det",
        ):
            limit_side_len = self.limit_side_len or kwargs.get("resize_long", 960)
            limit_type = self.limit_type or kwargs.get("limit_type", "max")
        else:
            limit_side_len = self.limit_side_len or kwargs.get("resize_long", 736)
            limit_type = self.limit_type or kwargs.get("limit_type", "min")

        return "Resize", DetResizeForTest(
            limit_side_len=limit_side_len, limit_type=limit_type, **kwargs
        )

    @register("NormalizeImage")
    def build_normalize(
        self,
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
        scale=1 / 255,
        order="",
        channel_num=3,
    ):
        return "Normalize", NormalizeImage(
            mean=mean, std=std, scale=scale, order=order, channel_num=channel_num
        )

    @register("ToCHWImage")
    def build_to_chw(self):
        return "ToCHW", ToCHWImage()

    def build_postprocess(self, **kwargs):
        if kwargs.get("name") == "DBPostProcess":
            return DBPostProcess(
                thresh=self.thresh or kwargs.get("thresh", 0.3),
                box_thresh=self.box_thresh or kwargs.get("box_thresh", 0.6),
                unclip_ratio=self.unclip_ratio or kwargs.get("unclip_ratio", 2.0),
                max_candidates=kwargs.get("max_candidates", 1000),
                use_dilation=kwargs.get("use_dilation", False),
                score_mode=kwargs.get("score_mode", "fast"),
                box_type=kwargs.get("box_type", "quad"),
            )

        else:
            raise Exception()

    @register("DetLabelEncode")
    def foo(self, *args, **kwargs):
        return None, None

    @register("KeepKeys")
    def foo(self, *args, **kwargs):
        return None, None
