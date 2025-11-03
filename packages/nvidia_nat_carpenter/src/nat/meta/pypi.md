# NVIDIA NAT Carpenter Plugin

This plugin provides integration between NeMo Agent Toolkit (NAT) and Carpenter, enabling NAT workflows to leverage Carpenter's agent execution capabilities.

## Features

- **CarpenterFunction**: A NAT function that can execute Carpenter workflows end-to-end
- **CLI Integration**: Run Carpenter workflows directly from NAT CLI using `nat carpenter run`

## Installation

```bash
pip install nvidia-nat-carpenter
```

## Usage

### Using CarpenterFunction in NAT Workflows

Create a NAT configuration file with a Carpenter function:

```yaml
functions:
  carpenter:
    name: carpenter
    config_file: path/to/carpenter_config.yml
```

### Using CLI

Run a Carpenter workflow directly:

```bash
nat carpenter run --config_file path/to/carpenter_config.yml
```

## Requirements

- Python 3.11 or 3.12
- nvidia-nat ~= 1.4
- chipnemo-carpenter >= 1.1.12
