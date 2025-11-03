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
"""Basic import tests for the NAT Carpenter plugin."""


def test_import_function():
    """Test that the function module can be imported."""
    from nat.carpenter import function

    assert function is not None
    assert hasattr(function, "CarpenterFunctionConfig")
    assert hasattr(function, "carpenter_function")


def test_import_cli():
    """Test that the CLI module can be imported."""
    from nat.carpenter import cli

    assert cli is not None
    assert hasattr(cli, "carpenter_command")
    assert hasattr(cli, "register_cli")


def test_import_register():
    """Test that the register module can be imported."""
    from nat.carpenter import register

    assert register is not None


def test_config_registration():
    """Test that CarpenterFunctionConfig is properly defined."""
    from nat.carpenter.function import CarpenterFunctionConfig

    # Test basic config creation
    config = CarpenterFunctionConfig(config_file="test.yml")
    assert config.config_file == "test.yml"
    assert config.disable_requires_confirmation is True


def test_cli_command_structure():
    """Test that the CLI command is properly structured."""
    from nat.carpenter.cli import carpenter_command

    assert carpenter_command is not None
    assert carpenter_command.name == "carpenter"

    # Check that the run subcommand exists
    commands = {cmd.name: cmd for cmd in carpenter_command.commands.values()}
    assert "run" in commands
