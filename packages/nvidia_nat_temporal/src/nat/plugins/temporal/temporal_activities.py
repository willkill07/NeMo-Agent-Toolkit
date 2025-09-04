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

from temporalio import activity

from nat.runtime.loader import load_workflow

logger = logging.getLogger(__name__)


@activity.defn
async def run_nat_workflow_activity(config_file: str, input_data: str) -> str:
    """
    Temporal activity that runs a NAT workflow from a configuration file.

    This activity loads a NAT workflow configuration and executes it with the provided input.
    It's designed to be run as a temporal activity within a temporal workflow.

    Args:
        config_file: Path to the NAT configuration file
        input_data: Input data to pass to the workflow

    Returns:
        The output from the workflow execution

    Raises:
        FileNotFoundError: If the config file doesn't exist
        RuntimeError: If workflow execution fails
    """
    logger.info("Starting NAT workflow activity from config: %s", config_file)

    # Send heartbeat to indicate activity is alive
    activity.heartbeat("Starting workflow execution")

    config_path = Path(config_file)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    try:
        # Load and run the workflow
        async with load_workflow(config_path) as session_manager:
            logger.info("Successfully loaded workflow from config: %s", config_file)

            # Send heartbeat to indicate workflow loaded
            activity.heartbeat("Workflow loaded, creating session")

            logger.debug("Created session, starting workflow execution")

            # Send heartbeat before starting execution
            activity.heartbeat("Starting workflow execution")

            # Use the workflow's run method to get a runner
            async with session_manager.workflow.run(input_data) as runner:
                # Send heartbeat during execution
                activity.heartbeat("Workflow running")

                if session_manager.workflow.has_single_output:
                    result = await runner.result(to_type=str)
                else:
                    # If the workflow only supports streaming, collect all outputs
                    results = []
                    async for chunk in runner.result_stream(to_type=str):
                        results.append(str(chunk))
                        # Send periodic heartbeats during streaming
                        activity.heartbeat(f"Processing output chunk: {len(results)}")
                    result = "\n".join(results)

            logger.info("NAT workflow activity completed successfully")

            # Final heartbeat before completion
            activity.heartbeat("Workflow completed successfully")

            return str(result)

    except Exception as e:
        logger.error("Error in NAT workflow activity: %s", e)
        # Send heartbeat with error status
        activity.heartbeat(f"Workflow failed: {str(e)}")
        raise RuntimeError(f"NAT workflow execution failed: {str(e)}") from e
