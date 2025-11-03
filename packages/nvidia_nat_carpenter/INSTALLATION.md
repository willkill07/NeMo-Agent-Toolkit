# Installation Guide for NAT Carpenter Plugin

## Prerequisites

Before installing the NAT Carpenter plugin, ensure you have:

1. Python 3.11 or Python 3.12
2. NVIDIA NAT installed
3. Carpenter (chipnemo-carpenter) installed

## Installation Steps

### 1. Install Dependencies

If you haven't already, install NAT and Carpenter:

```bash
# Install NAT (from the repository root)
cd /path/to/NeMo-Agent-Toolkit
pip install -e .

# Install Carpenter (adjust path as needed)
cd /path/to/carpenter
pip install -e .
```

### 2. Install the NAT Carpenter Plugin

From the NeMo-Agent-Toolkit repository root:

```bash
# Using pip
pip install -e packages/nvidia_nat_carpenter

# Or using uv (recommended)
uv pip install -e packages/nvidia_nat_carpenter
```

### 3. Verify Installation

Check that the plugin is registered:

```bash
# This should show the carpenter command
nat --help

# You should see:
#   carpenter  Carpenter integration commands.
```

Test the import:

```python
from nat.carpenter.function import CarpenterFunctionConfig, carpenter_function
from nat.carpenter.cli import carpenter_command
print("NAT Carpenter plugin installed successfully!")
```

### 4. Run Tests (Optional)

Verify the plugin works correctly:

```bash
cd packages/nvidia_nat_carpenter
pytest tests/
```

## Troubleshooting

### Import Errors

If you see import errors related to `carpenter`:

```
ImportError: No module named 'carpenter'
```

Make sure Carpenter is installed:

```bash
pip list | grep carpenter
```

### CLI Command Not Found

If `nat carpenter` doesn't work:

1. Verify the plugin is installed:
   ```bash
   pip list | grep nvidia-nat-carpenter
   ```

2. Check entry points are registered:
   ```bash
   python -c "import importlib.metadata; print(list(importlib.metadata.entry_points(group='nat.cli')))"
   ```

3. Reinstall the plugin:
   ```bash
   pip install -e packages/nvidia_nat_carpenter --force-reinstall
   ```

### Function Not Registering

If the CarpenterFunction isn't available in NAT workflows:

1. Ensure the plugin is installed
2. Check that NAT's plugin discovery is working:
   ```python
   from nat.cli.type_registry import GlobalTypeRegistry
   from nat.runtime.loader import PluginTypes, discover_and_register_plugins
   
   discover_and_register_plugins(PluginTypes.COMPONENT)
   registry = GlobalTypeRegistry.get()
   
   # Check if carpenter function is registered
   print(registry.get_registered_functions())
   ```

## Uninstallation

To remove the plugin:

```bash
pip uninstall nvidia-nat-carpenter
```

## Next Steps

After installation, see:
- [README.md](README.md) for usage examples
- [examples/](examples/) for sample configurations
- NAT documentation for more information on workflows

