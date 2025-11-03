# NAT Carpenter Plugin - Verification Checklist

## Installation Verification

After installing the plugin, verify these items:

### 1. Package Installation
```bash
# Check package is installed
pip list | grep nvidia-nat-carpenter

# Expected output:
# nvidia-nat-carpenter    <version>
```

### 2. Entry Points Registration
```bash
# Check NAT component entry point
python -c "import importlib.metadata; eps = list(importlib.metadata.entry_points(group='nat.components')); print([ep.name for ep in eps if 'carpenter' in ep.name])"

# Expected output should include: nvidia-nat-carpenter

# Check CLI entry point
python -c "import importlib.metadata; eps = list(importlib.metadata.entry_points(group='nat.cli')); print([ep.name for ep in eps if 'carpenter' in ep.name])"

# Expected output should include: nvidia-nat-carpenter
```

### 3. CLI Command Available
```bash
# Check carpenter command exists
nat --help | grep carpenter

# Expected output:
#   carpenter  Carpenter integration commands.

# Check run subcommand
nat carpenter --help

# Expected output should show the 'run' command
```

### 4. Function Registration
```python
from nat.cli.type_registry import GlobalTypeRegistry
from nat.runtime.loader import PluginTypes, discover_and_register_plugins

# Discover plugins
discover_and_register_plugins(PluginTypes.COMPONENT)

# Get registry
registry = GlobalTypeRegistry.get()

# Check for carpenter function
functions = registry.get_registered_functions()
carpenter_funcs = [f for f in functions if f.local_name == "carpenter"]

print(f"Found {len(carpenter_funcs)} carpenter function(s)")
# Expected: Found 1 carpenter function(s)
```

### 5. Import Tests
```python
# Test imports work
from nat.carpenter.function import CarpenterFunctionConfig, carpenter_function
from nat.carpenter.cli import carpenter_command, register_cli
from nat.carpenter import register

print("All imports successful!")
```

### 6. Configuration Validation
```python
from nat.carpenter.function import CarpenterFunctionConfig

# Test basic config
config = CarpenterFunctionConfig(config_file="test.yml")
assert config.config_file == "test.yml"
assert config.disable_requires_confirmation is True

# Test with all options
config_full = CarpenterFunctionConfig(
    config_file="test.yml",
    llm="llama31_70b",
    max_turns=50,
    disable_requires_confirmation=False
)
assert config_full.llm == "llama31_70b"
assert config_full.max_turns == 50

print("Configuration validation successful!")
```

## Functional Testing

### 7. CLI Execution (Basic)
```bash
# This will fail if carpenter config doesn't exist, but should show proper error handling
nat carpenter run --config_file nonexistent.yml 2>&1 | head -n 5

# Should show error about file not found (not import errors or crashes)
```

### 8. NAT Workflow Integration (If you have a valid Carpenter config)
```bash
# Create a test NAT config
cat > test_nat_carpenter.yml << 'EOF'
functions:
  carpenter_test:
    name: carpenter
    config_file: path/to/valid/carpenter_config.yml
EOF

# Validate the config
nat validate --config_file test_nat_carpenter.yml

# Expected: Should validate successfully (may warn about missing carpenter config)
```

## Troubleshooting Commands

If any checks fail, try these:

### Reinstall Plugin
```bash
pip uninstall nvidia-nat-carpenter -y
pip install -e packages/nvidia_nat_carpenter
```

### Clear Python Cache
```bash
find packages/nvidia_nat_carpenter -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
```

### Check Dependencies
```bash
pip list | grep -E "(nvidia-nat|carpenter|click|pydantic|pyyaml)"
```

### Verbose Import Test
```python
import sys
import logging

logging.basicConfig(level=logging.DEBUG)

print("Testing imports with verbose output...")

try:
    print("1. Importing function module...")
    from nat.carpenter import function
    print("   ✓ Success")
except Exception as e:
    print(f"   ✗ Failed: {e}")

try:
    print("2. Importing CLI module...")
    from nat.carpenter import cli
    print("   ✓ Success")
except Exception as e:
    print(f"   ✗ Failed: {e}")

try:
    print("3. Importing register module...")
    from nat.carpenter import register
    print("   ✓ Success")
except Exception as e:
    print(f"   ✗ Failed: {e}")

try:
    print("4. Loading entry points...")
    import importlib.metadata
    eps = list(importlib.metadata.entry_points(group='nat.components'))
    carpenter_eps = [ep for ep in eps if 'carpenter' in ep.name]
    print(f"   ✓ Found {len(carpenter_eps)} component entry point(s)")
    
    cli_eps = list(importlib.metadata.entry_points(group='nat.cli'))
    carpenter_cli_eps = [ep for ep in cli_eps if 'carpenter' in ep.name]
    print(f"   ✓ Found {len(carpenter_cli_eps)} CLI entry point(s)")
except Exception as e:
    print(f"   ✗ Failed: {e}")

print("\nAll checks complete!")
```

## Complete Verification Script

```python
#!/usr/bin/env python3
"""Complete verification script for NAT Carpenter plugin."""

def verify_installation():
    """Run all verification checks."""
    
    checks_passed = 0
    checks_total = 0
    
    # Check 1: Import function module
    checks_total += 1
    try:
        from nat.carpenter import function
        assert hasattr(function, "CarpenterFunctionConfig")
        assert hasattr(function, "carpenter_function")
        print("✓ Check 1: Function module imports successfully")
        checks_passed += 1
    except Exception as e:
        print(f"✗ Check 1 Failed: {e}")
    
    # Check 2: Import CLI module
    checks_total += 1
    try:
        from nat.carpenter import cli
        assert hasattr(cli, "carpenter_command")
        assert hasattr(cli, "register_cli")
        print("✓ Check 2: CLI module imports successfully")
        checks_passed += 1
    except Exception as e:
        print(f"✗ Check 2 Failed: {e}")
    
    # Check 3: Configuration validation
    checks_total += 1
    try:
        from nat.carpenter.function import CarpenterFunctionConfig
        config = CarpenterFunctionConfig(config_file="test.yml")
        assert config.config_file == "test.yml"
        print("✓ Check 3: Configuration works correctly")
        checks_passed += 1
    except Exception as e:
        print(f"✗ Check 3 Failed: {e}")
    
    # Check 4: Entry points
    checks_total += 1
    try:
        import importlib.metadata
        component_eps = list(importlib.metadata.entry_points(group='nat.components'))
        cli_eps = list(importlib.metadata.entry_points(group='nat.cli'))
        
        has_component = any('carpenter' in ep.name for ep in component_eps)
        has_cli = any('carpenter' in ep.name for ep in cli_eps)
        
        assert has_component, "Component entry point not found"
        assert has_cli, "CLI entry point not found"
        
        print("✓ Check 4: Entry points registered correctly")
        checks_passed += 1
    except Exception as e:
        print(f"✗ Check 4 Failed: {e}")
    
    # Summary
    print(f"\n{'='*50}")
    print(f"Verification Results: {checks_passed}/{checks_total} checks passed")
    print(f"{'='*50}")
    
    if checks_passed == checks_total:
        print("✓ All checks passed! Plugin is correctly installed.")
        return 0
    else:
        print("✗ Some checks failed. See above for details.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(verify_installation())
```

Save this as `verify_plugin.py` and run:
```bash
python verify_plugin.py
```

## Success Criteria

The plugin is correctly installed if:
- [ ] All imports work without errors
- [ ] `nat carpenter --help` shows the command
- [ ] Entry points are registered in both `nat.components` and `nat.cli`
- [ ] Configuration validation works
- [ ] The function is registered in NAT's type registry

If all checks pass, the plugin is ready to use!

