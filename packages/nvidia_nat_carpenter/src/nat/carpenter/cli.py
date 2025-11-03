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
"""CLI commands for Carpenter integration."""

import asyncio
import logging
from pathlib import Path

import click

logger = logging.getLogger(__name__)


@click.group(name="carpenter", invoke_without_command=False, help="Carpenter integration commands.")
def carpenter_command():
    """Carpenter integration commands for NAT."""
    pass


@carpenter_command.command(name="run", help="Run a Carpenter workflow via NAT")
@click.option(
    "--config_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    required=True,
    help="Path to the Carpenter configuration file (YAML format)",
)
@click.option(
    "--request",
    type=str,
    default=None,
    help="JSON string containing the request parameters for the workflow",
)
@click.option(
    "--llm",
    type=str,
    default=None,
    help="Override the LLM to use for the workflow",
)
@click.option(
    "--max_turns",
    type=int,
    default=None,
    help="Maximum number of execution turns",
)
@click.option(
    "--disable_requires_confirmation/--no-disable_requires_confirmation",
    default=True,
    help="Disable requires_confirmation for non-interactive execution",
)
def run_command(
    config_file: Path,
    request: str | None,
    llm: str | None,
    max_turns: int | None,
    disable_requires_confirmation: bool,
):
    """Run a Carpenter workflow through NAT.

    This command creates a temporary NAT workflow with a CarpenterFunction
    as the entrypoint and executes the specified Carpenter configuration.

    Example:
        nat carpenter run --config_file carpenter_config.yml --request '{"input": "test"}'
    """
    import json

    # Parse request if provided
    request_dict = {}
    if request:
        try:
            request_dict = json.loads(request)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in --request parameter: {e}")
            raise click.ClickException(f"Invalid JSON in --request parameter: {e}")

    logger.info(f"Running Carpenter workflow from: {config_file}")

    # Create a dynamic NAT configuration with CarpenterFunction
    nat_config = {
        "functions": {
            "carpenter_entrypoint": {
                "name": "carpenter",
                "config_file": str(config_file),
            }
        }
    }

    # Add optional parameters
    if llm:
        nat_config["functions"]["carpenter_entrypoint"]["llm"] = llm
    if max_turns:
        nat_config["functions"]["carpenter_entrypoint"]["max_turns"] = max_turns
    nat_config["functions"]["carpenter_entrypoint"]["disable_requires_confirmation"] = disable_requires_confirmation

    logger.debug(f"Generated NAT config: {nat_config}")

    # Run the workflow
    asyncio.run(_run_carpenter_workflow(nat_config, request_dict))


async def _run_carpenter_workflow(nat_config: dict, request: dict):
    """Execute the Carpenter workflow via NAT.

    Args:
        nat_config: NAT configuration dictionary
        request: Request parameters for the workflow
    """
    from nat.builder.workflow_builder import WorkflowBuilder
    from nat.carpenter.function import CarpenterFunctionConfig
    from nat.data_models.config import Config

    # Create the CarpenterFunctionConfig object from the dict
    carpenter_config = CarpenterFunctionConfig(**nat_config["functions"]["carpenter_entrypoint"])

    # Create proper Config object with instantiated config
    builder_config = Config(workflow=carpenter_config)

    async with WorkflowBuilder.from_config(config=builder_config) as builder:
        # Get the function
        carpenter_fn = builder.get_workflow()

        if not carpenter_fn:
            raise ValueError("Failed to create Carpenter function")

        logger.info("Executing Carpenter workflow...")

        # Execute the workflow
        # The carpenter function expects a parameter named 'request'
        result = await carpenter_fn.ainvoke({"request": request if request else {}})

        logger.info("Workflow execution completed")

        # Print results
        print("\n" + "=" * 80)
        print("CARPENTER WORKFLOW RESULTS")
        print("=" * 80)

        if isinstance(result, dict):
            import json
            print(json.dumps(result, indent=2, default=str))
        else:
            print(result)

        print("=" * 80 + "\n")

        return result


def register_cli():
    """Register the Carpenter CLI commands with NAT.

    This function is called by NAT's plugin system to add the carpenter
    command group to the main CLI.
    """
    return carpenter_command
