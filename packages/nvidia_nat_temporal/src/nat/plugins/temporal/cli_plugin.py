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

import asyncio
import logging
from datetime import timedelta
from pathlib import Path

import click
from temporalio.client import Client
from temporalio.worker import Worker

from .temporal_activities import run_nat_workflow_activity
from .temporal_function import NATWorkflow

logger = logging.getLogger(__name__)


@click.group(name="temporal")
@click.pass_context
def temporal_command(ctx: click.Context):
    """Temporal integration commands for NeMo Agent toolkit."""
    pass


@temporal_command.command(name="worker")
@click.option("--task-queue", default="nat-workflow-queue", help="Temporal task queue name to listen on")
@click.option("--namespace", default="default", help="Temporal namespace to connect to")
@click.option("--temporal-address", default="localhost:7233", help="Temporal server address")
@click.pass_context
def worker_command(ctx: click.Context, task_queue: str, namespace: str, temporal_address: str):
    """Start a worker that can execute NAT workflows as activities."""

    async def run_worker():
        logger.info("Starting Temporal worker for NAT workflows")
        logger.info("Task queue: %s", task_queue)
        logger.info("Namespace: %s", namespace)
        logger.info("Temporal address: %s", temporal_address)

        # Create temporal client
        client = await Client.connect(target_host=temporal_address, namespace=namespace)

        # Create worker with modified sandbox configuration
        from temporalio.worker.workflow_sandbox import SandboxedWorkflowRunner
        from temporalio.worker.workflow_sandbox import SandboxRestrictions

        # Get default restrictions to use as a base
        default_runner = SandboxedWorkflowRunner()
        default_restrictions = default_runner._restrictions

        # Add NAT-specific modules to the passthrough list
        nat_passthrough_modules = {
            "httpx",
            "httpx.*",
            "urllib.request",
            "urllib.parse",
            "urllib.error",
            "requests",
            "requests.*",
            "nat",
            "nat.*",
            "openai",
            "openai.*",
            "anthropic",
            "anthropic.*",
            "google.generativeai",
            "google.generativeai.*",
            "pandas",
            "pandas.*",
            "numpy",
            "numpy.*",
            "pydantic",
            "pydantic.*",
        }

        # Create new restrictions with additional passthrough modules
        modified_restrictions = SandboxRestrictions(
            passthrough_modules=default_restrictions.passthrough_modules | nat_passthrough_modules,
            invalid_modules=default_restrictions.invalid_modules,
            invalid_module_members=default_restrictions.invalid_module_members,
        )

        # Create custom workflow runner with modified restrictions
        custom_workflow_runner = SandboxedWorkflowRunner(restrictions=modified_restrictions)

        worker = Worker(
            client,
            task_queue=task_queue,
            workflows=[NATWorkflow],
            activities=[run_nat_workflow_activity],
            workflow_runner=custom_workflow_runner,
        )

        logger.info("Temporal worker started. Listening for tasks...")

        try:
            # Run the worker
            await worker.run()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down worker")
        finally:
            del client
            logger.info("Temporal worker stopped")

    # Run the worker
    asyncio.run(run_worker())


@temporal_command.command(name="run")
@click.option("--config-file",
              type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
              required=True,
              help="Path to the NAT configuration file")
@click.option("--input", required=True, help="Input data to pass to the workflow")
@click.option("--task-queue", default="nat-workflow-queue", help="Temporal task queue name")
@click.option("--namespace", default="default", help="Temporal namespace")
@click.option("--temporal-address", default="localhost:7233", help="Temporal server address")
@click.option("--workflow-id", help="Unique workflow ID (auto-generated if not provided)")
@click.option("--timeout", type=int, default=3600, help="Workflow execution timeout in seconds")
@click.pass_context
def run_command(ctx: click.Context,
                config_file: Path,
                input: str,
                task_queue: str,
                namespace: str,
                temporal_address: str,
                workflow_id: str,
                timeout: int):
    """Run a NAT workflow as a Temporal workflow."""

    async def run_workflow():
        logger.info("Starting NAT workflow via Temporal")
        logger.info("Config file: %s", config_file)
        logger.info("Task queue: %s", task_queue)
        logger.info("Namespace: %s", namespace)

        # Create temporal client
        client = await Client.connect(target_host=temporal_address, namespace=namespace)

        try:
            # Generate workflow ID if not provided
            import uuid
            actual_workflow_id = workflow_id or f"nat-workflow-{uuid.uuid4()}"

            logger.info("Starting workflow with ID: %s", actual_workflow_id)

            # Start the workflow
            handle = await client.start_workflow(
                NATWorkflow.run,
                args=[str(config_file), input],
                id=actual_workflow_id,
                task_queue=task_queue,
                execution_timeout=timedelta(seconds=timeout),
            )

            logger.info("Workflow started. Waiting for completion...")

            # Wait for result
            result = await handle.result()

            logger.info("Workflow completed successfully")
            click.echo("Workflow Result:")
            click.echo(result)

        except Exception as e:
            logger.error("Workflow execution failed: %s", e)
            raise click.ClickException(f"Workflow execution failed: {str(e)}")
        finally:
            del client

    # Run the workflow
    asyncio.run(run_workflow())


@temporal_command.command(name="activity")
@click.option("--config-file",
              type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
              required=True,
              help="Path to the NAT configuration file")
@click.option("--input", required=True, help="Input data to pass to the workflow")
@click.pass_context
def activity_command(ctx: click.Context, config_file: Path, str_input: str):
    """Run a NAT workflow directly as a Temporal activity"""

    async def run_activity():
        logger.info("Running NAT workflow as activity")
        logger.info("Config file: %s", config_file)

        try:
            # Run the activity directly (outside of temporal context for testing)
            result = await run_nat_workflow_activity(str(config_file), str_input)

            logger.info("Activity completed successfully")
            click.echo("Activity Result:")
            click.echo(result)

        except Exception as e:
            logger.error("Activity execution failed: %s", e)
            raise click.ClickException(f"Activity execution failed: {str(e)}")

    # Run the activity
    asyncio.run(run_activity())
