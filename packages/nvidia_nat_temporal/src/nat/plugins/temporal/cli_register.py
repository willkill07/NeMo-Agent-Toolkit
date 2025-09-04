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
"""
CLI registration module for Temporal plugin.

This module provides the temporal CLI command for entry point registration.
"""

import logging

from .cli_plugin import temporal_command

logger = logging.getLogger(__name__)


def register_temporal_cli_command(cli_group):
    """
    Register the temporal CLI command with the main NAT CLI.

    This function adds the temporal command group to the main CLI
    if the temporal dependencies are available.

    Args:
        cli_group: The main CLI group to add the temporal command to
    """
    try:
        cli_group.add_command(temporal_command, name="temporal")
        logger.info("Registered temporal CLI command successfully")

    except Exception as e:
        logger.error("Unexpected error registering temporal CLI command: %s", e)
