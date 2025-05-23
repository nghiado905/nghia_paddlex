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

import lazy_paddle as paddle


def get_device_type():
    device_str = paddle.get_device()
    return device_str.split(":")[0]


def get_paddle_version():
    version = paddle.__version__.split(".")
    # ref: https://github.com/PaddlePaddle/Paddle/blob/release/3.0-beta2/setup.py#L316
    assert len(version) == 3
    major_v, minor_v, patch_v = version
    return major_v, minor_v, patch_v
