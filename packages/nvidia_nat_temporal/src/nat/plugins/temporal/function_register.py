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
Function registration module for Temporal functions.

This module handles the registration of temporal functions with the NAT system,
separated from the workflow definitions to avoid Temporal sandbox issues.
"""

import logging

logger = logging.getLogger(__name__)


def register_temporal_functions():
    """
    Register temporal functions with the NAT function registry.

    This function is called during plugin initialization to register
    all temporal-related functions.
    """
    try:
        # Import here to avoid circular imports and sandbox issues
        from nat.cli.register_workflow import register_function

        from .data_models import TemporalFunctionConfig
        from .temporal_function import temporal_function

        # Register the temporal function
        register_function(config_type=TemporalFunctionConfig)(temporal_function)

        logger.info("Successfully registered temporal functions")

    except Exception as e:
        logger.error("Error registering temporal functions: %s", e)
        raise
