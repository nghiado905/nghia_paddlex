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

import os
from typing import Any, Dict, List

from fastapi import FastAPI

from ...infra import utils as serving_utils
from ...infra.config import AppConfig
from ...infra.models import ResultResponse
from ...schemas.m_3d_bev_detection import INFER_ENDPOINT, InferRequest, InferResult
from .._app import create_app, primary_operation


def create_pipeline_app(pipeline: Any, app_config: AppConfig) -> FastAPI:
    app, ctx = create_app(
        pipeline=pipeline, app_config=app_config, app_aiohttp_session=True
    )

    @primary_operation(
        app,
        INFER_ENDPOINT,
        "infer",
    )
    async def _infer(request: InferRequest) -> ResultResponse[InferResult]:
        pipeline = ctx.pipeline
        aiohttp_session = ctx.aiohttp_session

        file_bytes = await serving_utils.get_raw_bytes_async(
            request.tar, aiohttp_session
        )
        tar_path = await serving_utils.call_async(
            serving_utils.write_to_temp_file,
            file_bytes,
            suffix=".tar",
        )

        try:
            result = (
                await pipeline.infer(
                    tar_path,
                )
            )[0]
        finally:
            await serving_utils.call_async(os.unlink, tar_path)

        objects: List[Dict[str, Any]] = []
        for box, label, score in zip(
            result["boxes_3d"], result["labels_3d"], result["scores_3d"]
        ):
            objects.append(
                dict(
                    bbox=box,
                    categoryId=label,
                    score=score,
                )
            )

        return ResultResponse[InferResult](
            logId=serving_utils.generate_log_id(),
            result=InferResult(detectedObjects=objects),
        )

    return app
