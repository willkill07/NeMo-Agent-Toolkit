# NVIDIA NAT Carpenter Plugin

This plugin provides integration between NeMo Agent Toolkit (NAT) and Carpenter, enabling NAT workflows to leverage Carpenter's agent execution capabilities.

## Features

- **CarpenterFunction**: A NAT function that can execute Carpenter workflows end-to-end
- **CLI Integration**: Run Carpenter workflows directly from NAT CLI using `nat carpenter run`

## Installation

To install the plugin, you need to have both NAT and Carpenter installed. From the repository root:

```bash
# Install NAT (if not already installed)
pip install -e .

# Install the Carpenter plugin
pip install -e packages/nvidia_nat_carpenter
```

Or using uv:

```bash
uv pip install -e packages/nvidia_nat_carpenter
```

## Usage

### Using CarpenterFunction in NAT Workflows

Create a NAT configuration file (`nat_config.yml`) with a Carpenter function:

```yaml
functions:
  carpenter_workflow:
    name: carpenter
    config_file: path/to/carpenter_config.yml
    llm: llama31_70b  # Optional: override LLM
    max_turns: 50     # Optional: set max execution turns
    disable_requires_confirmation: true  # For non-interactive execution
```

Then run it using NAT:

```bash
nat run --config_file nat_config.yml
```

### Using CLI

Run a Carpenter workflow directly:

```bash
nat carpenter run --config_file path/to/carpenter_config.yml
```

With additional options:

```bash
nat carpenter run \
  --config_file path/to/carpenter_config.yml \
  --request '{"input": "test query"}' \
  --llm llama31_70b \
  --max_turns 50
```

## Carpenter Configuration

Your Carpenter configuration file should follow the standard Carpenter format. Example:

```yaml
exec:
  tool: my_agent
  llm: llama31_70b
  max_turns: 100

carpenter_agents:
  - path/to/agents

carpenter_tools:
  - path/to/tools

tools:
  - name: my_agent
    description: "My agent description"
    tools:
      - some_tool
    system_prompt: "You are a helpful assistant"
```

## Requirements

- Python >= 3.11
- nvidia-nat ~= 1.4
- chipnemo-carpenter >= 1.1.12

## Development

To run tests:

```bash
pytest packages/nvidia_nat_carpenter/tests/
```

## License

Apache-2.0

## Support

For issues related to:
- NAT functionality: See [NAT documentation](https://docs.nvidia.com/nemo/agent-toolkit/latest/)
- Carpenter functionality: Refer to Carpenter documentation

