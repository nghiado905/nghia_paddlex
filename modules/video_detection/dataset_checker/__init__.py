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

from pathlib import Path

from ...base import BaseDatasetChecker
from .dataset_src import check, deep_analyse
from ..model_list import MODELS


class VideoDetDatasetChecker(BaseDatasetChecker):
    """Dataset Checker for Image Classification Model"""

    entities = MODELS
    sample_num = 10

    def convert_dataset(self, src_dataset_dir: str) -> str:
        """convert the dataset from other type to specified type

        Args:
            src_dataset_dir (str): the root directory of dataset.

        Returns:
            str: the root directory of converted dataset.
        """
        return src_dataset_dir

    def split_dataset(self, src_dataset_dir: str) -> str:
        """repartition the train and validation dataset

        Args:
            src_dataset_dir (str): the root directory of dataset.

        Returns:
            str: the root directory of splited dataset.
        """
        return src_dataset_dir

    def check_dataset(self, dataset_dir: str, sample_num: int = sample_num) -> dict:
        """check if the dataset meets the specifications and get dataset summary

        Args:
            dataset_dir (str): the root directory of dataset.
            sample_num (int): the number to be sampled.
        Returns:
            dict: dataset summary.
        """
        return check(dataset_dir, self.output)

    def analyse(self, dataset_dir: str) -> dict:
        """deep analyse dataset

        Args:
            dataset_dir (str): the root directory of dataset.

        Returns:
            dict: the deep analysis results.
        """
        return deep_analyse(dataset_dir, self.output)

    def get_show_type(self) -> str:
        """get the show type of dataset

        Returns:
            str: show type
        """
        return "video"

    def get_dataset_type(self) -> str:
        """return the dataset type

        Returns:
            str: dataset type
        """
        return "VideoDetDataset"
