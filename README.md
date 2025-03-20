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

🤝 **Two testing styles** - Choose between class-based tests or modular fixtures-based tests according to your preference

🔄 **State snapshots** - Create a full blockchain state once, then reset to this state between tests in milliseconds instead of seconds

🛠️ **Complete toolchain integration** - Seamless integration with [NEAR compiler](https://github.com/r-near/nearc), [Python SDK](https://github.com/r-near/near-sdk-py), and [sandbox](https://github.com/near/near-sandbox)

🧪 **Pytest native** - Leverages the full power of pytest for smart contract testing

🔍 **Rich logging** - Detailed logs for troubleshooting and debugging

🧠 **Smart caching** - Automatically caches compiled contracts for faster subsequent runs

✨ **Requests-like Response API** - Familiar interface for handling contract responses with `.json()` method and `.text` property

## Installation

```bash
uv add near-pytest
```

### Prerequisites

- Python 3.11 or higher
- For contract compilation: `nearc` package
- The framework automatically handles downloading and installing the NEAR sandbox binary

## Getting Started

You can choose between two testing approaches:

1. **Modular Fixtures Approach** - More pytest-native, with composable fixtures 
2. **Class-based Approach** - Traditional approach with test classes inheriting from `NearTestCase`

### Modular Fixtures Approach

```python
import pytest
from near_pytest.compiler import compile_contract

@pytest.fixture(scope="session")
def counter_wasm():
    """Compile the counter contract."""
    return compile_contract("path/to/contract.py", single_file=True)

@pytest.fixture
def counter_contract(sandbox, counter_wasm):
    """Deploy a fresh counter contract for each test."""
    account = sandbox.create_random_account("counter")
    return sandbox.deploy(
        wasm_path=counter_wasm,
        account=account,
        init_args={"starting_count": 0}
    )

def test_increment(counter_contract, localnet_alice_account):
    """Test incrementing the counter."""
    # Call contract method using method chaining
    result = counter_contract.call("increment").as_transaction(localnet_alice_account)
    assert int(result) == 1
    
    # View state
    count = counter_contract.call("get_count").as_view()
    assert int(count) == 1
```

### Class-based Approach

```python
from near_pytest.testing import NearTestCase

class TestCounter(NearTestCase):
    @classmethod
    def setup_class(cls):
        # Call parent setup method first
        super().setup_class()
        
        # Compile the contract
        wasm_path = cls.compile_contract("path/to/contract.py", single_file=True)
        
        # Create account for contract
        cls.counter = cls.create_account("counter")
        
        # Deploy contract
        cls.counter_contract = cls.deploy_contract(
            cls.counter, 
            wasm_path, 
            init_args={"starting_count": 0}
        )
        
        # Create test accounts
        cls.alice = cls.create_account("alice")
        cls.bob = cls.create_account("bob")
        
        # Save initial state for future resets
        cls.save_state()

    def setup_method(self):
        # Reset to initial state before each test method
        self.reset_state()

    def test_increment(self):
        # Call contract method
        result = self.counter_contract.call("increment", {})
        assert int(result.text) == 1
```

## Examples

### Counter Contract Example (Fixtures Approach)

```python
from near_pytest.modular import sandbox, compile_contract, sandbox_alice

@pytest.fixture(scope="session")
def counter_wasm():
    """Compile the counter contract."""
    return compile_contract("counter_contract/__init__.py", single_file=True)

@pytest.fixture
def fresh_counter(sandbox, counter_wasm, temp_account):
    """Deploy a fresh counter contract for each test."""
    return sandbox.deploy(
        wasm_path=counter_wasm,
        account=temp_account,
        init_args={"starting_count": 0}
    )

def test_increment_fresh(fresh_counter, sandbox_alice):
    """Test incrementing a fresh counter."""
    # This always starts with count=0
    result = fresh_counter.call("increment").as_transaction(sandbox_alice)
    assert int(result) == 1
    
    # Increment again
    result = fresh_counter.call("increment").as_transaction(sandbox_alice)
    assert int(result) == 2
```

### JSON Response Example

```python
def test_json_response(self):
    # Call a method that returns JSON data
    response = self.contract.call("get_user_data", {"user_id": "alice"})
    
    # Parse the JSON response
    data = response.json()
    
    # Assert on the parsed data
    assert data["name"] == "Alice"
    assert data["score"] == 100
    assert "created_at" in data
```

## Key Concepts

### 1. Testing Styles

`near-pytest` supports two testing styles:

#### Modular Fixtures (Recommended)
- More pytest-native approach with composable fixtures
- Better test isolation with fixtures per test
- Method chaining for contract calls with clear semantics
- Easier to use with parallel testing (pytest-xdist)

#### Class-based (NearTestCase)
- Traditional approach with a base class
- All test methods share setup
- State management with `save_state` and `reset_state`

### 2. Smart Contract Compilation

`near-pytest` automatically handles compilation of your Python smart contracts to WASM using the NEAR SDK for Python.

```python
# Fixtures approach
wasm_path = compile_contract("path/to/contract.py", single_file=True)

# Class-based approach
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

Create test accounts easily:

```python
# Fixtures approach
account = sandbox.create_account("alice")
random_account = sandbox.create_random_account()

# Class-based approach
cls.alice = cls.create_account("alice")
```

### 5. Contract Deployment

Deploy contracts to accounts and initialize them:

```python
# Fixtures approach
contract = sandbox.deploy(
    wasm_path=wasm_path,
    account=account,
    init_args={"param": "value"}
)

# Class-based approach
cls.contract = cls.deploy_contract(cls.account, wasm_path, init_args={"param": "value"})
```

### 6. Contract Calls

Call contract methods:

```python
# Fixtures approach (with method chaining)
result = contract.call("increment").as_transaction(account)
view_result = contract.call("get_count").as_view()

# Class-based approach
result = contract.call("increment", {})
view_result = contract.view("get_count", {})
```

### 7. State Management

Save and restore state for fast test execution:

```python
# Fixtures approach
state = sandbox.save_state()
sandbox.reset_state(state)

# Class-based approach
cls.save_state()
self.reset_state()
```

### 7. ContractResponse

Contract call responses are wrapped in a `ContractResponse` object that provides a familiar interface similar to Python's `requests` library:

```python
# Get the raw text response
text_content = response.text

# Parse JSON response
json_data = response.json()

# String representation
str_value = str(response)  # Same as response.text
```

## API Reference

### Modular Fixtures

#### Provided Fixtures

- `sandbox`: Main entry point for interacting with the NEAR sandbox
- `sandbox_alice`, `sandbox_bob`: Pre-created accounts for tests
- `temp_account`: Creates a fresh random account for each test
- `create_account`: Factory fixture to create accounts on demand
- `near_client`: Direct access to the NEAR client for RPC operations

#### SandboxProxy Methods

- `create_account(name)`: Create a new account with the given name
- `create_random_account(prefix="test")`: Create a new account with a random name
- `deploy(wasm_path, account, init_args=None, init_method="new")`: Deploy a contract
- `save_state()`: Save current blockchain state
- `reset_state(state)`: Reset to a previously saved state

#### EnhancedContract Methods

- `call(method_name, **kwargs)`: Create a contract call with method chaining
- `account_id`: Property to get the contract account ID

#### ContractCall Methods

- `as_transaction(account, amount=0, gas=None)`: Execute as a transaction
- `as_view()`: Execute as a view call

#### Helper Functions

- `compile_contract(contract_path, single_file=False)`: Helper function to compile a contract to WASM

### Using nearc Directly

If you prefer to use the NEAR compiler (nearc) directly for more control over the compilation process:

```python
import nearc

# Compile your contract with custom options
wasm_path = nearc.builder.compile_contract(
    contract_path="path/to/contract.py", 
    output_path="path/to/output.wasm",
    single_file=True
)
```

### Network Distinction

Our fixtures use a naming convention to distinguish between different networks:

- `sandbox` - The main fixture that provides access to the NEAR sandbox node
- `localnet_alice`, `localnet_bob`, `localnet_temp_account` - Account fixtures that operate on the local network

This distinction allows for future expansion to other networks like testnet or mainnet while maintaining a clear separation of concerns.

### NearTestCase Methods

- `setup_class(cls)`: Set up shared resources for the test class
- `compile_contract(contract_path, single_file=False)`: Compile a contract to WASM
- `create_account(name, initial_balance=None)`: Create a new test account
- `deploy_contract(account, wasm_path, init_args=None)`: Deploy a contract
- `save_state()`: Save the current state for later reset
- `reset_state()`: Reset to the previously saved state

### Account Methods

- `call_contract(contract_id, method_name, args=None, amount=0, gas=None)`: Call a contract method
- `view_contract(contract_id, method_name, args=None)`: Call a view method
- `deploy_contract(wasm_file)`: Deploy a contract to this account

### Contract Methods

- `call(method_name, args=None, amount=0, gas=None)`: Call as the contract account
- `call_as(account, method_name, args=None, amount=0, gas=None)`: Call as another account
- `view(method_name, args=None)`: Call a view method

### ContractResponse

A wrapper for contract call responses that provides a familiar interface for handling response data.

#### Properties

- `text`: Get the raw text response as a string
- `transaction_result`: Access the underlying transaction result (if available)

#### Methods

- `json()`: Parse the response as JSON and return the resulting Python object

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
- **ContractResponse**: Wraps contract call responses with a user-friendly API
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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.