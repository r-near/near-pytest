
# near-pytest

A pytest-native framework for testing NEAR smart contracts in Python.

[![PyPI version](https://img.shields.io/badge/pypi-0.1.0-blue.svg)](https://pypi.org/project/near-pytest/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/badge/python-3.11+-blue)](https://pypi.org/project/near-pytest/)
[![Built with Pytest](https://img.shields.io/badge/built%20with-pytest-brightgreen.svg)](https://docs.pytest.org/)

✨ [Features](#features) &nbsp;•&nbsp;
📥 [Installation](#installation) &nbsp;•&nbsp;
🚀 [Getting Started](#getting-started) &nbsp;•&nbsp;
📊 [Examples](#examples) &nbsp;•&nbsp;
📘 [API Reference](#api-reference)


## Overview

`near-pytest` enables intuitive testing of NEAR smart contracts directly from Python. It provides a pytest-native approach that automatically handles compilation, sandbox initialization, account creation, contract deployment, and state management - allowing you to focus on writing tests that truly validate your contract's behavior.

## Features

🚀 **Zero-config setup** - Everything works out-of-the-box: automatic sandbox management, contract compilation, and account creation

⚡ **Lightning-fast tests** - State snapshots between tests eliminate repeated setup operations, making test suites run orders of magnitude faster than traditional approaches

🧩 **Intuitive API** - Simple, Pythonic interfaces for interacting with contracts and accounts

🔄 **State snapshots** - Create a full blockchain state once, then reset to this state between tests in milliseconds instead of seconds

🛠️ **Complete toolchain integration** - Seamless integration with [NEAR compiler](https://github.com/r-near/nearc), [Python SDK](https://github.com/r-near/near-sdk-py), and [sandbox](https://github.com/near/near-sandbox)

🧪 **Pytest native** - Leverages the full power of pytest for smart contract testing

🔍 **Rich logging** - Detailed logs for troubleshooting and debugging

🧠 **Smart caching** - Automatically caches compiled contracts for faster subsequent runs

## Installation

```bash
uv add near-pytest
```

### Prerequisites

- Python 3.11 or higher
- For contract compilation: `nearc` package
- The framework automatically handles downloading and installing the NEAR sandbox binary

## Getting Started

### 1. Create a test file

```python
from near_pytest.testing import NearTestCase


class TestMyContract(NearTestCase):
    @classmethod
    def setup_class(cls):
        # Call parent setup method first
        super().setup_class()
        
        # Compile the contract
        wasm_path = cls.compile_contract("path/to/contract.py", single_file=True)
        
        # Create account for contract
        cls.contract_account = cls.create_account("mycontract")
        
        # Deploy contract
        cls.contract = cls.deploy_contract(
            cls.contract_account, 
            wasm_path, 
            init_args={"param1": "value1"}
        )
        
        # Create test accounts
        cls.alice = cls.create_account("alice")
        cls.bob = cls.create_account("bob")
        
        # Save initial state for future resets
        cls.save_state()

    def setup_method(self):
        # Reset to initial state before each test method
        self.reset_state()

    def test_my_function(self):
        # Call contract method
        result = self.contract.call("my_function", {"param": "value"})
        assert result == "expected_result"
        
    def test_as_alice(self):
        # Call as another account
        result = self.contract.call_as(self.alice, "my_function", {"param": "value"})
        assert result == "expected_result"
```

### 2. Run your tests

```bash
pytest test_my_contract.py -v
```

## Examples

### Counter Contract Example

```python
from near_pytest.testing import NearTestCase
from pathlib import Path

class TestCounter(NearTestCase):
    @classmethod
    def setup_class(cls):
        super().setup_class()
        
        # Compile the contract
        current_dir = Path(__file__).parent
        contract_path = current_dir / "counter_contract" / "__init__.py"
        wasm_path = cls.compile_contract(contract_path, single_file=True)
        
        # Create and deploy contract
        cls.counter = cls.create_account("counter")
        cls.counter_contract = cls.deploy_contract(
            cls.counter, wasm_path, init_args={"starting_count": 0}
        )
        
        # Create users
        cls.alice = cls.create_account("alice")
        
        # Save state for reset
        cls.save_state()
        
    def setup_method(self):
        # Reset before each test
        self.reset_state()
        
    def test_increment(self):
        # Each test starts with a fresh state
        result = self.counter_contract.call("increment", {})
        assert int(result) == 1
        
        # State persists within the test
        result = self.counter_contract.call("increment", {})
        assert int(result) == 2
        
    def test_get_count(self):
        # This test starts fresh with count=0
        result = self.counter_contract.view("get_count", {})
        assert int(result) == 0
```

## Key Concepts

### 1. NearTestCase

The main base class for your tests, providing helper methods for contract compilation, account creation, and state management.

### 2. Smart Contract Compilation

`near-pytest` automatically handles compilation of your Python smart contracts to WASM using the NEAR SDK for Python.

```python
wasm_path = cls.compile_contract("path/to/contract.py", single_file=True)
```

The compilation process includes:
- Automatic caching of compiled contracts (based on content hash)
- Support for single-file contracts or multi-file projects
- Seamless integration with the `nearc` compiler

### 3. Sandbox Management

The framework automatically:
- Downloads the appropriate NEAR sandbox binary for your platform
- Manages sandbox lifecycle (start/stop)
- Provides methods for state manipulation

### 4. Account Management

Create test accounts with a single line:

```python
cls.alice = cls.create_account("alice")
```

Each account is automatically:
- Created with a unique identifier
- Funded with NEAR tokens
- Associated with a key pair

### 5. Contract Deployment

Deploy contracts to accounts and initialize them:

```python
cls.contract = cls.deploy_contract(cls.account, wasm_path, init_args={"param": "value"})
```

### 6. State Management

Save and restore state for fast test execution:

```python
# Save initial state once
cls.save_state()

# Reset to initial state before each test
self.reset_state()
```

This state management is what makes near-pytest tests run significantly faster than traditional approaches that need to re-deploy the contract and accounts for each test.

## API Reference

### NearTestCase

Base class for NEAR contract tests.

#### Class Methods

- `setup_class()`: Set up shared resources for the test class
- `compile_contract(contract_path, single_file=False)`: Compile a contract to WASM
- `create_account(name, initial_balance=None)`: Create a new test account
- `deploy_contract(account, wasm_path, init_args=None)`: Deploy a contract
- `save_state()`: Save the current state for later reset

#### Instance Methods

- `reset_state()`: Reset to the previously saved state

### Account

A simplified account model for testing.

#### Methods

- `call_contract(contract_id, method_name, args=None, amount=0, gas=None)`: Call a contract method
- `view_contract(contract_id, method_name, args=None)`: Call a view method
- `deploy_contract(wasm_file)`: Deploy a contract to this account

### Contract

A simplified contract model for testing.

#### Methods

- `call(method_name, args=None, amount=0, gas=None)`: Call as the contract account
- `call_as(account, method_name, args=None, amount=0, gas=None)`: Call as another account
- `view(method_name, args=None)`: Call a view method

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Environment Variables

You can customize the behavior of near-pytest using these environment variables:

- `NEAR_PYTEST_LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `NEAR_SANDBOX_HOME`: Specify a custom home directory for the sandbox

## Architecture

near-pytest consists of several core components:

- **SandboxManager**: Handles the NEAR sandbox process lifecycle
- **NearClient**: Manages communication with the NEAR RPC interface 
- **Account/Contract**: Simplified models for interacting with the blockchain
- **NearTestCase**: Base class that ties everything together for testing

## Troubleshooting

### Common Issues

1. **Sandbox doesn't start**
   - Check if port 3030 is available
   - Ensure you have proper permissions to execute downloaded binaries

2. **Contract compilation fails**
   - Verify that the nearc package is installed
   - Check Python version compatibility (3.11+ required)

3. **Slow test execution**
   - Ensure you're using `save_state()` and `reset_state()` pattern
   - Verify if cache directory (~/.near-pytest/cache) exists and is writeable