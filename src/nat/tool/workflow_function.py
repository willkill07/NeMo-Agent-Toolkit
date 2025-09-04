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

import logging
from pathlib import Path

from pydantic import Field

from nat.builder.builder import Builder
from nat.cli.register_workflow import register_function
from nat.data_models.function import FunctionBaseConfig
from nat.runtime.loader import load_workflow

logger = logging.getLogger(__name__)


class WorkflowFunctionConfig(FunctionBaseConfig, name="workflow"):
    """
    Configuration for the workflow function that allows running an entire agent/workflow
    as a tool call by loading it from a config file.
    """

    config_file: str = Field(description="Path to the configuration file for the workflow to run as a tool")
    description: str = Field(default="Workflow function that runs another agent as a tool",
                             description="Description of this workflow function")


@register_function(config_type=WorkflowFunctionConfig)
async def workflow_function(config: WorkflowFunctionConfig, builder: Builder):
    """
    Register a workflow function that can run another entire workflow/agent as a tool call.

    This function loads a workflow from a config file and exposes it as a callable function
    that can be used as a tool within other agents.
    """
    logger.info("Initializing workflow function from config file: %s", config.config_file)

    # Load the workflow from the specified config file
    config_path = Path(config.config_file)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config.config_file}")

    # Create a session manager for the workflow
    async with load_workflow(config_path) as session_manager:
        logger.info("Successfully loaded workflow from config file: %s", config.config_file)

        async def _workflow_function(input_data: str) -> str:
            """
            Execute the loaded workflow with the given input.

            Args:
                input_data: The input string to pass to the workflow

            Returns:
                The output from the workflow execution
            """
            logger.debug("Executing workflow function with input: %s", input_data)

            try:
                async with session_manager.workflow.run(input_data) as runner:
                    if session_manager.workflow.has_single_output:
                        result = await runner.result(to_type=str)
                    else:
                        # If the workflow only supports streaming, collect all outputs
                        results = []
                        async for chunk in runner.result_stream(to_type=str):
                            results.append(str(chunk))
                        result = "\n".join(results)

                logger.debug("Workflow function completed with result: %s", result)
                return str(result)

            except Exception as e:
                logger.error("Error executing workflow function: %s", e)
                raise RuntimeError(f"Workflow execution failed: {str(e)}") from e

        # Set the function description from config
        _workflow_function.__doc__ = config.description

        yield _workflow_function

    logger.info("Workflow function cleanup completed")
