# NVIDIA NeMo Agent Toolkit - Temporal Integration

This package provides Temporal workflow integration for the NVIDIA NeMo Agent Toolkit (NAT). It allows you to run NAT workflows as Temporal activities and child workflows, enabling distributed and fault-tolerant execution of AI agent workflows.

## Features

- **Temporal Function**: A function plugin that runs NAT workflows as child Temporal workflows
- **Temporal Activities**: Activities that execute NAT workflows within Temporal workflows
- **CLI Integration**: Command-line tools for running NAT workflows through Temporal
- **Worker Support**: Temporal worker implementation for processing NAT workflow tasks

## Installation

```bash
pip install nvidia-nat-temporal
```

## Prerequisites

- NVIDIA NeMo Agent Toolkit (`nvidia-nat`)
- Temporal server running (local or remote)
- Python 3.11+

## Quick Start

### 1. Start a Temporal Worker

Start a worker that can execute NAT workflows:

```bash
nat temporal worker --task-queue my-queue --namespace default
```

### 2. Run a NAT Workflow as Temporal Workflow

Execute a NAT workflow through Temporal:

```bash
nat temporal run --config-file my-config.yml --input "Hello, world!" --task-queue my-queue
```

### 3. Use Temporal Function in NAT Workflows

Add a temporal function to your NAT configuration:

```yaml
functions:
  - name: "child_workflow"
    type: "temporal"
    config_file: "path/to/child-workflow-config.yml"
    task_queue: "nat-workflow-queue"
    temporal_namespace: "default"
    workflow_execution_timeout: 3600
```

## Configuration

### Temporal Function Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `config_file` | str | Required | Path to the NAT configuration file for the child workflow |
| `workflow_id` | str | Auto-generated | Unique identifier for the temporal workflow |
| `task_queue` | str | "nat-workflow-queue" | Temporal task queue name |
| `temporal_namespace` | str | "default" | Temporal namespace |
| `workflow_execution_timeout` | int | 3600 | Maximum execution time in seconds |
| `description` | str | Auto-generated | Function description |

## CLI Commands

### `nat temporal worker`

Start a Temporal worker for NAT workflows.

**Options:**
- `--task-queue`: Task queue name (default: "nat-workflow-queue")
- `--namespace`: Temporal namespace (default: "default")
- `--temporal-address`: Temporal server address (default: "localhost:7233")

### `nat temporal run`

Run a NAT workflow as a Temporal workflow.

**Options:**
- `--config-file`: Path to NAT configuration file (required)
- `--input`: Input data for the workflow (required)
- `--task-queue`: Task queue name (default: "nat-workflow-queue")
- `--namespace`: Temporal namespace (default: "default")
- `--temporal-address`: Temporal server address (default: "localhost:7233")
- `--workflow-id`: Custom workflow ID (auto-generated if not provided)
- `--timeout`: Execution timeout in seconds (default: 3600)

### `nat temporal activity`

Run a NAT workflow directly as an activity (for testing).

**Options:**
- `--config-file`: Path to NAT configuration file (required)
- `--input`: Input data for the workflow (required)

## Examples

### Example 1: Child Workflow Function

This is only showing the snippet of the configuration file required to run a function as a temporal workflow.
```yaml
functions:
  analyze_data:
    _type: temporal
    config_file: analysis-workflow.yml
    task_queue: analysis-queue
    description: "Analyzes data using a specialized workflow"
  
  generate_report:
    _type: temporal
    config_file: report-workflow.yml
    task_queue: reporting-queue
    description: "Generates reports using a specialized workflow"
```

### Example 2: Distributed Processing

```bash
# Terminal 1: Start analysis worker
nat temporal worker --task-queue analysis-queue

# Terminal 2: Start reporting worker  
nat temporal worker --task-queue reporting-queue

# Terminal 3: Run the coordinator workflow
nat temporal run --config-file parent-workflow.yml --input "Process dataset X"
```

## Architecture

The Temporal integration consists of several components:

1. **Temporal Function**: A NAT function that creates child Temporal workflows
2. **NAT Workflow**: A Temporal workflow definition that executes NAT configurations
3. **Temporal Activities**: Activities that load and run NAT workflows
4. **CLI Plugin**: Command-line interface for Temporal operations
5. **Worker**: Temporal worker that processes NAT workflow tasks

## Error Handling

The Temporal integration includes comprehensive error handling:

- File validation before workflow execution
- Temporal heartbeats during long-running workflows
- Proper cleanup of resources
- Detailed logging for debugging

## Development

### Running Tests

```bash
pytest packages/nvidia_nat_temporal/tests/
```

### Contributing

Please follow the standard NAT contribution guidelines when working on this package.

## License

This package is licensed under the Apache License 2.0. See the LICENSE file for details.
