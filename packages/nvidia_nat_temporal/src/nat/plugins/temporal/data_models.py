# SPDX-FileCopyrightText: Copyright (c) 2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pydantic import BaseModel
from pydantic import Field

from nat.data_models.function import FunctionBaseConfig


class TemporalFunctionConfig(FunctionBaseConfig, name="temporal"):
    """
    Configuration for the temporal function that allows running a child Temporal workflow
    that executes another agent/workflow loaded from a config file.
    """

    config_file: str = Field(
        description="Path to the configuration file for the workflow to run as a child temporal workflow")
    host: str = Field(default="localhost", description="Temporal server host")
    port: int = Field(default=7233, description="Temporal server port")
    workflow_id: str | None = Field(
        default=None,
        description="Unique identifier for the temporal workflow. If not provided, a UUID will be generated")
    task_queue: str = Field(default="nat-workflow-queue",
                            description="Name of the temporal task queue to use for workflow execution")
    temporal_namespace: str = Field(default="default", description="Temporal namespace to use for workflow execution")
    execution_timeout: int = Field(default=3600,
                                   description="Maximum execution time for the workflow in seconds (default: 1 hour)")
    description: str = Field(default="Temporal function that runs another agent as a child workflow",
                             description="Description of this temporal function")


class TemporalActivityConfig(BaseModel):
    """
    Configuration for temporal activities that run NAT workflows.
    """

    config_file: str = Field(description="Path to the NAT configuration file")
    input_data: str = Field(description="Input data to pass to the workflow")
    task_queue: str = Field(default="nat-workflow-queue", description="Name of the temporal task queue")
    execution_timeout: int = Field(default=3600,
                                   description="Maximum execution time for the workflow in seconds (default: 1 hour)")
