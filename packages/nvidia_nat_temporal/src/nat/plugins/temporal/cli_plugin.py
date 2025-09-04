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

import click

logger = logging.getLogger(__name__)


@click.group(name="temporal")
@click.pass_context
def temporal_command(_ctx: click.Context):
    """Temporal integration commands for NeMo Agent toolkit."""
    pass


@temporal_command.command(name="worker")
@click.option("--task-queue", default="nat-workflow-queue", help="Temporal task queue name to listen on")
@click.option("--namespace", default="default", help="Temporal namespace to connect to")
@click.option("--temporal-address", default="localhost:7233", help="Temporal server address")
@click.pass_context
def worker_command(_ctx: click.Context, task_queue: str, namespace: str, temporal_address: str):
    """Start a worker that can execute NAT workflows as activities."""

    async def run_worker():
        from temporalio.client import Client
        from temporalio.worker import UnsandboxedWorkflowRunner
        from temporalio.worker import Worker

        from nat.plugins.temporal.temporal_activities import run_nat_workflow_as_activity
        from nat.plugins.temporal.temporal_workflow_function import NATWorkflow

        logger.info("Starting Temporal worker for NAT workflows")
        logger.info("Task queue: %s", task_queue)
        logger.info("Namespace: %s", namespace)
        logger.info("Temporal address: %s", temporal_address)

        # Create temporal client
        client = await Client.connect(target_host=temporal_address, namespace=namespace)

        worker = Worker(
            client,
            task_queue=task_queue,
            workflows=[NATWorkflow],
            activities=[run_nat_workflow_as_activity],
            workflow_runner=UnsandboxedWorkflowRunner(),
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
@click.option("--config_file",
              type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=str),
              required=True,
              help="Path to the NAT configuration file")
@click.option("--input", required=True, help="Input data to pass to the workflow")
@click.option("--task-queue", default="nat-workflow-queue", help="Temporal task queue name")
@click.option("--namespace", default="default", help="Temporal namespace")
@click.option("--temporal-address", default="localhost:7233", help="Temporal server address")
@click.option("--workflow-id", help="Unique workflow ID (auto-generated if not provided)")
@click.option("--timeout", type=int, default=3600, help="Workflow execution timeout in seconds")
@click.pass_context
def run_command(_ctx: click.Context,
                config_file: str,
                input: str,
                task_queue: str,
                namespace: str,
                temporal_address: str,
                workflow_id: str,
                timeout: int):
    """Run a NAT workflow as a Temporal workflow."""

    async def run_workflow():
        import uuid
        from datetime import timedelta

        from temporalio.client import Client

        from .temporal_workflow_function import NATWorkflow

        logger.info("Starting NAT workflow via Temporal")
        logger.info("Config file: %s", config_file)
        logger.info("Task queue: %s", task_queue)
        logger.info("Namespace: %s", namespace)

        # Create temporal client
        client = await Client.connect(target_host=temporal_address, namespace=namespace)

        try:
            # Generate workflow ID if not provided
            actual_workflow_id = workflow_id or f"nat-temporal-workflow-{uuid.uuid4()}"

            logger.info("Starting workflow with ID: %s", actual_workflow_id)

            # Start the workflow
            handle = await client.start_workflow(
                NATWorkflow.run,
                arg={
                    "config_file": str(config_file), "input": input
                },
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
@click.option("--config_file",
              type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=str),
              required=True,
              help="Path to the NAT configuration file")
@click.option("--input", required=True, help="Input data to pass to the workflow")
@click.pass_context
def activity_command(_ctx: click.Context, config_file: str, input: str):
    """Run a NAT workflow directly as a Temporal activity"""

    async def run_activity():
        from .temporal_activities import run_nat_workflow_as_activity

        logger.info("Running NAT workflow as activity")
        logger.info("Config file: %s", config_file)

        try:
            # Run the activity directly (outside of temporal context for testing)
            result = await run_nat_workflow_as_activity(config_file, input)

            logger.info("Activity completed successfully")
            click.echo("Activity Result:")
            click.echo(result)

        except Exception as e:
            logger.error("Activity execution failed: %s", e)
            raise click.ClickException(f"Activity execution failed: {str(e)}")

    # Run the activity
    asyncio.run(run_activity())
