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

import cv2
import numpy as np
from PIL import Image
from .....utils import logging


def check_image_size(input_):
    """check image size"""
    if not (
        isinstance(input_, (list, tuple))
        and len(input_) == 2
        and isinstance(input_[0], int)
        and isinstance(input_[1], int)
    ):
        raise TypeError(f"{input_} cannot represent a valid image size.")


def resize(im, target_size, interp, backend="cv2"):
    """resize image to target size"""
    w, h = target_size
    if backend.lower() == "pil":
        resize_function = _pil_resize
    else:
        resize_function = _cv2_resize
        if backend.lower() != "cv2":
            logging.warning(
                f"Unknown backend {backend}. Defaulting to cv2 for resizing."
            )
    im = resize_function(im, (w, h), interp)
    return im


def _cv2_resize(src, size, resample):
    return cv2.resize(src, size, interpolation=resample)


def _pil_resize(src, size, resample):
    if isinstance(src, np.ndarray):
        pil_img = Image.fromarray(src)
    else:
        pil_img = src
    pil_img = pil_img.resize(size, resample)
    return np.asarray(pil_img)


def flip_h(im):
    """flip image horizontally"""
    if len(im.shape) == 3:
        im = im[:, ::-1, :]
    elif len(im.shape) == 2:
        im = im[:, ::-1]
    return im


def flip_v(im):
    """flip image vertically"""
    if len(im.shape) == 3:
        im = im[::-1, :, :]
    elif len(im.shape) == 2:
        im = im[::-1, :]
    return im


def slice(im, coords):
    """slice the image"""
    x1, y1, x2, y2 = coords
    im = im[y1:y2, x1:x2, ...]
    return im


def pad(im, pad, val):
    """padding image by value"""
    if isinstance(pad, int):
        pad = [pad] * 4
    if len(pad) != 4:
        raise ValueError
    chns = 1 if im.ndim == 2 else im.shape[2]
    im = cv2.copyMakeBorder(im, *pad, cv2.BORDER_CONSTANT, value=(val,) * chns)
    return im
