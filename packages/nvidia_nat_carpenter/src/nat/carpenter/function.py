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
"""Carpenter Function implementation for NAT."""

import logging
from pathlib import Path
from typing import Any

from pydantic import Field

from nat.builder.builder import Builder
from nat.cli.register_workflow import register_function
from nat.data_models.function import FunctionBaseConfig

logger = logging.getLogger(__name__)


class CarpenterFunctionConfig(FunctionBaseConfig, name="carpenter"):
    """Configuration for the Carpenter function.

    This function executes a Carpenter workflow end-to-end based on the provided
    configuration file.
    """

    config_file: str = Field(..., description="Path to the Carpenter configuration file (YAML format)")

    llm: str | None = Field(default=None, description="Override the default LLM used by Carpenter agents")

    max_turns: int | None = Field(default=None,
                                  description="Maximum number of execution turns for the Carpenter workflow")

    disable_requires_confirmation: bool = Field(
        default=True, description="Disable requires_confirmation for tools/agents (for non-interactive execution)")


@register_function(config_type=CarpenterFunctionConfig)
async def carpenter_function(config: CarpenterFunctionConfig, builder: Builder):
    """Execute a Carpenter workflow end-to-end

    This function loads a Carpenter configuration file, initializes the registry,
    creates the necessary interfaces, and executes the specified agent/tool.

    Args:
        config: Configuration containing the path to the Carpenter config file
        builder: NAT builder instance

    Returns:
        A function that accepts input and returns the Carpenter workflow results
    """

    # Import carpenter dependencies
    try:
        import carpenter
        from carpenter.base.config_utils import load_registry_from_config
        from carpenter.base.config_utils import read_config_file
        from carpenter.base.interface import FullInterface
        from carpenter.base.interface import LlmInterface
        from carpenter.base.recorder_callbacks import print_node_results
        from carpenter.base.utils import disable_requires_confirmation
    except ImportError as e:
        logger.error("Failed to import carpenter. Make sure chipnemo-carpenter is installed.")
        raise ImportError("Carpenter is not installed. Install it with: pip install chipnemo-carpenter") from e

    # Read and validate the configuration file
    config_path = Path(config.config_file)
    if not config_path.exists():
        raise FileNotFoundError(f"Carpenter config file not found: {config.config_file}")

    logger.info(f"Loading Carpenter configuration from: {config.config_file}")

    # Read the config file - Carpenter's read_config_file adds metadata fields
    config_data = read_config_file(str(config_path))

    # Note: We skip strict Pydantic validation here because read_config_file adds
    # extra metadata fields (like config_dir) that aren't in CarpenterConfig schema.
    # Carpenter will do its own validation when loading the registry.

    # Load the registry from config - this validates the config internally
    logger.info("Initializing Carpenter registry...")
    load_registry_from_config(config_data)

    # Get the tool/agent name from exec config
    exec_config = config_data.get("exec")
    if not exec_config or not exec_config.get("tool"):
        raise ValueError("Carpenter config must specify exec.tool")

    tool_name = exec_config["tool"]
    logger.info(f"Target Carpenter tool/agent: {tool_name}")

    # Apply configuration overrides
    exec_args = {}
    if config.llm:
        exec_args["llm"] = config.llm
        logger.info(f"Using LLM override: {config.llm}")
    elif exec_config.get("llm"):
        exec_args["llm"] = exec_config["llm"]

    if config.max_turns:
        exec_args["max_turns"] = config.max_turns
    elif exec_config.get("max_turns"):
        exec_args["max_turns"] = exec_config["max_turns"]

    # Disable requires_confirmation if needed
    if config.disable_requires_confirmation:
        disable_requires_confirmation(tool_name)

    async def inner(request: dict[str, Any] | str) -> dict[str, Any]:
        """Execute the Carpenter workflow with the given request.

        Args:
            request: Input request (either a dict or string)

        Returns:
            Dictionary containing the workflow results
        """
        # Convert string input to dict if needed
        if isinstance(request, str):
            request = {"input": request}

        logger.info(f"Executing Carpenter workflow with request: {request}")

        # Get the tool from registry using bracket notation (Registry uses __class_getitem__)
        tool_class = carpenter.Registry[tool_name]
        if not tool_class:
            raise ValueError(f"Carpenter tool/agent '{tool_name}' not found in registry")

        # Create the tool instance
        tool = tool_class()

        # Create interface
        interface = FullInterface()
        interface.set_user_info()
        interface.add_callback(print_node_results)
        interface.set_llm_interface(LlmInterface())

        # Set LLM if specified
        if "llm" in exec_args:
            interface.llm_interface.set_llm(exec_args["llm"])

        # Create recorder
        recorder = tool.new_recorder(request)

        # Execute the workflow
        max_turns = exec_args.get("max_turns", 100)
        logger.info(f"Starting execution (max_turns={max_turns})...")

        carpenter.execute(recorder=recorder, interface=interface, max_turns=max_turns)

        logger.info("Carpenter workflow execution completed")

        # Extract results from the recorder
        # The final_response contains the tool's output as a dictionary
        final_response = recorder.final_response if recorder.final_response else {}

        return {
            "final_response": final_response,
            "tool": tool_name,
            "success": recorder.final_response is not None,
            "error": getattr(recorder, "error_response", None)
        }

    yield inner
