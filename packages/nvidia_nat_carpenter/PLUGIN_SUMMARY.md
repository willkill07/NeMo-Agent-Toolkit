# NAT Carpenter Plugin - Implementation Summary

## Overview

This plugin provides seamless integration between NeMo Agent Toolkit (NAT) and Carpenter, enabling NAT workflows to execute Carpenter agents and tools.

## Components Implemented

### 1. CarpenterFunction (`src/nat/carpenter/function.py`)

**Purpose**: A NAT function that executes Carpenter workflows end-to-end.

**Key Features**:
- Loads Carpenter configuration files
- Initializes Carpenter registry and agents
- Executes workflows with configurable parameters
- Returns structured results

**Configuration Parameters**:
```python
class CarpenterFunctionConfig(FunctionBaseConfig, name="carpenter"):
    config_file: str                          # Required: Path to Carpenter config
    llm: str | None = None                    # Optional: Override LLM
    max_turns: int | None = None              # Optional: Max execution turns
    disable_requires_confirmation: bool = True # For non-interactive execution
```

**Usage in NAT Workflow**:
```yaml
functions:
  my_carpenter_agent:
    name: carpenter
    config_file: path/to/carpenter_config.yml
    llm: llama31_70b
    max_turns: 50
```

### 2. CLI Command (`src/nat/carpenter/cli.py`)

**Purpose**: Direct CLI access to run Carpenter workflows via NAT.

**Command Structure**:
```bash
nat carpenter run --config_file <path> [OPTIONS]
```

**Available Options**:
- `--config_file`: Path to Carpenter configuration (required)
- `--request`: JSON string with request parameters (optional)
- `--llm`: Override the LLM (optional)
- `--max_turns`: Maximum execution turns (optional)
- `--disable_requires_confirmation`: Control confirmation prompts (default: true)

**Example Usage**:
```bash
# Basic execution
nat carpenter run --config_file carpenter_config.yml

# With parameters
nat carpenter run \
  --config_file carpenter_config.yml \
  --request '{"query": "What is the weather?"}' \
  --llm llama31_70b \
  --max_turns 50
```

### 3. Registration System (`src/nat/carpenter/register.py`)

Automatically registers the CarpenterFunction with NAT's type registry when the plugin is loaded.

### 4. Entry Points (`pyproject.toml`)

Two entry points enable automatic plugin discovery:

```toml
[project.entry-points.'nat.components']
nvidia-nat-carpenter = "nat.carpenter.register"

[project.entry-points.'nat.cli']
nvidia-nat-carpenter = "nat.carpenter.cli:register_cli"
```

## File Structure

```
packages/nvidia_nat_carpenter/
├── src/nat/carpenter/
│   ├── __init__.py          # Package initialization
│   ├── function.py          # CarpenterFunction implementation
│   ├── cli.py               # CLI commands
│   └── register.py          # Component registration
├── src/nat/meta/
│   └── pypi.md              # PyPI package description
├── tests/
│   ├── __init__.py
│   └── test_import.py       # Basic import tests
├── examples/
│   ├── simple_carpenter_config.yml  # Example Carpenter config
│   └── nat_with_carpenter.yml       # Example NAT config
├── pyproject.toml           # Package configuration
├── LICENSE.md
├── LICENSE-3rd-party.txt
├── README.md                # User documentation
└── INSTALLATION.md          # Installation guide
```

## Integration Points

### With NAT Core

1. **Function Registration**: The `CarpenterFunction` is registered via the `@register_function` decorator
2. **Type System**: Uses NAT's `FunctionBaseConfig` for configuration
3. **Builder Pattern**: Integrates with NAT's `Builder` for async execution
4. **CLI Integration**: Extends NAT CLI through entry points

### With Carpenter

1. **Configuration Loading**: Uses Carpenter's `read_config_file` and `CarpenterConfig`
2. **Registry System**: Loads tools/agents via Carpenter's `Registry`
3. **Execution**: Uses Carpenter's `execute()` function with `Recorder` and `Interface`
4. **Results Collection**: Leverages `collect_agent_results()` for output processing

### Modified NAT Core Files

**`src/nat/cli/entrypoint.py`**: Added dynamic CLI plugin loading functionality to discover and load commands from entry points.

## Installation

```bash
# From NeMo-Agent-Toolkit root
pip install -e packages/nvidia_nat_carpenter

# Or using uv
uv pip install -e packages/nvidia_nat_carpenter
```

## Testing

Basic tests are provided in `tests/test_import.py`:
- Import verification
- Configuration validation
- CLI command structure checks

Run tests:
```bash
pytest packages/nvidia_nat_carpenter/tests/
```

## Dependencies

### Core Dependencies
- `nvidia-nat ~= 1.4`: NAT framework
- `chipnemo-carpenter >= 1.1.12`: Carpenter execution engine
- `click >= 8.1.8`: CLI framework
- `pydantic >= 2.0`: Configuration validation
- `pyyaml >= 6.0`: YAML parsing

### Runtime Requirements
- Python >= 3.11, < 3.14

## Usage Patterns

### Pattern 1: Direct CLI Execution
```bash
nat carpenter run --config_file my_config.yml
```

### Pattern 2: NAT Workflow Integration
```yaml
# nat_workflow.yml
functions:
  carpenter_step:
    name: carpenter
    config_file: carpenter_config.yml
```

```bash
nat run --config_file nat_workflow.yml
```

### Pattern 3: Programmatic Usage
```python
from nat.builder.builder import Builder
from nat.builder.config import BuilderConfig

config = BuilderConfig(
    functions={
        "carpenter_agent": {
            "name": "carpenter",
            "config_file": "carpenter_config.yml"
        }
    }
)

async with Builder.from_config(config) as builder:
    fn = await builder.get_function("carpenter_agent")
    result = await fn({"query": "test"})
```

## Extension Points

The plugin can be extended by:

1. **Custom Carpenter Configs**: Any valid Carpenter configuration works
2. **NAT Pipeline Integration**: Use as part of larger NAT workflows
3. **Custom CLI Commands**: Add more carpenter-related commands via the CLI module
4. **Result Processing**: Post-process Carpenter results in NAT functions

## Known Limitations

1. **Interactive Execution**: By default, `disable_requires_confirmation=True` for non-interactive use
2. **Async/Sync Bridge**: Carpenter's sync API is wrapped in async for NAT compatibility
3. **Error Propagation**: Carpenter errors are caught and converted to NAT exceptions

## Future Enhancements

Potential improvements:
- Streaming support for long-running workflows
- Better progress reporting
- Integration with NAT's observability features
- Support for Carpenter's multi-agent configurations
- Cached Carpenter registry for faster execution
