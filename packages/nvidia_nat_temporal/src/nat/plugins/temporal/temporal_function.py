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
import uuid
from datetime import timedelta
from pathlib import Path

from temporalio import workflow
from temporalio.client import Client

from .data_models import TemporalFunctionConfig

logger = logging.getLogger(__name__)


@workflow.defn
class NATWorkflow:
    """
    Temporal workflow definition for running NAT workflows.
    """

    @workflow.run
    async def run(self, config_file: str, input_data: str) -> str:
        """
        Run a NAT workflow as a temporal workflow.

        Args:
            config_file: Path to the NAT configuration file
            input_data: Input data to pass to the workflow
        Returns:
            The output from the workflow execution
        """
        logger.info("Starting NAT workflow from config: %s", config_file)

        # Import the activity here to avoid circular imports
        from .temporal_activities import run_nat_workflow_activity
        # Run the NAT workflow as a temporal activity
        result = await workflow.execute_activity(
            run_nat_workflow_activity,
            args=[config_file, input_data],
            start_to_close_timeout=timedelta(hours=1),  # Maximum time for activity to complete
            heartbeat_timeout=timedelta(seconds=60),  # Send heartbeat every 60 seconds
        )

        logger.info("NAT workflow completed successfully")
        return result


async def temporal_function(config: TemporalFunctionConfig, _builder):
    """
    Create a temporal function that can run another entire workflow/agent as a child temporal workflow.

    This function creates a temporal client and starts a child workflow that executes
    the specified NAT configuration as an activity.

    Args:
        config: Temporal function configuration
        _builder: NAT builder instance (passed at runtime)
    """
    logger.info("Initializing temporal function from config file: %s", config.config_file)

    # Validate the config file exists
    if not Path(config.config_file).exists():
        raise FileNotFoundError(f"Config file not found: {config.config_file}")

    # Create temporal client
    temporal_client = await Client.connect(target_host=f"{config.host}:{config.port}",
                                           namespace=config.temporal_namespace)

    async def _temporal_function(input_data: str) -> str:
        """
        Execute the NAT workflow as a child temporal workflow.

        Args:
            input_data: The input string to pass to the workflow

        Returns:
            The output from the workflow execution
        """
        logger.debug("Executing temporal function with input: %s", input_data)

        try:
            # Generate workflow ID if not provided
            workflow_id = config.workflow_id or f"nat-workflow-{uuid.uuid4()}"

            # Start the child workflow
            handle = await temporal_client.start_workflow(
                NATWorkflow.run,
                args=[config.config_file, input_data],
                id=workflow_id,
                task_queue=config.task_queue,
                execution_timeout=timedelta(seconds=config.execution_timeout),
            )

            logger.info("Started temporal workflow with ID: %s", workflow_id)

            # Wait for the workflow to complete
            result = await handle.result()

            logger.debug("Temporal function completed with result: %s", result)
            return str(result)

        except Exception as e:
            logger.error("Error executing temporal function: %s", e)
            raise RuntimeError(f"Temporal workflow execution failed: {str(e)}") from e

    # Set the function description from config
    _temporal_function.__doc__ = config.description

    yield _temporal_function

    logger.info("Temporal function cleanup completed")
