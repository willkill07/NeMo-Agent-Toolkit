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

from nat.plugins.temporal.data_models import TemporalFunctionConfig


def test_temporal_function_config():
    """Test that TemporalFunctionConfig can be instantiated with required fields."""
    config = TemporalFunctionConfig(config_file="/path/to/config.yml")

    assert config.config_file == "/path/to/config.yml"
    assert config.task_queue == "nat-workflow-queue"
    assert config.temporal_namespace == "default"
    assert config.workflow_execution_timeout == 3600
    assert config.workflow_id is None


def test_temporal_function_config_with_optional_fields():
    """Test TemporalFunctionConfig with all optional fields set."""
    config = TemporalFunctionConfig(config_file="/path/to/config.yml",
                                    workflow_id="custom-workflow-id",
                                    task_queue="custom-queue",
                                    temporal_namespace="custom-namespace",
                                    workflow_execution_timeout=7200,
                                    description="Custom description")

    assert config.config_file == "/path/to/config.yml"
    assert config.workflow_id == "custom-workflow-id"
    assert config.task_queue == "custom-queue"
    assert config.temporal_namespace == "custom-namespace"
    assert config.workflow_execution_timeout == 7200
    assert config.description == "Custom description"
