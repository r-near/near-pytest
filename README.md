# near-pytest

A pytest-native approach for testing NEAR smart contracts in Python.

## Features

- Class-based test framework that integrates with pytest
- Automatic sandbox management (download, start, stop)
- Smart contract compilation with `nearc`
- Easy account creation and management
- State reset between tests
- Intuitive contract interaction API

## Installation

```bash
pip install near-pytest
```

## Requirements

- Python 3.9+
- nearc (for contract compilation)
  - Install with `pip install nearc`

## Quick Start

Here's a simple example of testing a counter contract:

```python
from near_pytest import NearTestCase
from pathlib import Path

class TestCounter(NearTestCase):
    @classmethod
    def setup_class(cls):
        # Call the parent setup method
        super().setup_class()
        
        # Compile the contract once for all tests
        current_dir = Path(__file__).parent
        contract_path = current_dir / "counter_contract" / "__init__.py"
        cls.counter_wasm = cls.compile_contract(contract_path)
    
    def setup_method(self):
        # Reset sandbox state before each test
        self.reset_sandbox()
        
        # Create account for contract
        self.contract_account = self.create_account("counter")
        
        # Deploy contract
        self.counter = self.deploy_contract(
            self.contract_account, 
            self.counter_wasm,
            init_args={"starting_count": 0}
        )
        
        # Create user accounts
        self.alice = self.create_account("alice")
        self.bob = self.create_account("bob")
    
    def test_increment(self):
        # Call contract method
        result = self.counter.call("increment", {})
        assert result == 1
        
        # Call again to verify state persistence within a test
        result = self.counter.call("increment", {})
        assert result == 2
    
    def test_increment_as_alice(self):
        # Each test starts with fresh state
        result = self.counter.call_as(self.alice, "increment", {})
        assert result == 1
    
    def test_get_count(self):
        # Call view method
        result = self.counter.view("get_count", {})
        assert result == 0
        
        # Call increment then view again
        self.counter.call("increment", {})
        result = self.counter.view("get_count", {})
        assert result == 1
```

## How It Works

1. The `NearTestCase` base class provides utilities for testing NEAR smart contracts.
2. The sandbox is started automatically when needed and shared across all tests.
3. Each test gets a fresh blockchain state to work with.
4. Contracts are compiled with `nearc` and cached for efficiency.
5. Test accounts are created with unique names to prevent conflicts.

## API Reference

### `NearTestCase`

Base class for NEAR contract test cases.

#### Class Methods

- `compile_contract(contract_path)`: Compile a contract and return the path to the WASM file.
- `get_root_account()`: Get the root account (with lots of funds).

#### Instance Methods

- `reset_sandbox()`: Reset the sandbox state.
- `create_account(name, initial_balance=None)`: Create a new account with the specified name.
- `deploy_contract(account, wasm_path, init_args=None)`: Deploy a contract to the specified account.

### `ContractProxy`

Provides a convenient interface for interacting with deployed contracts.

#### Methods

- `call(method_name, args=None, amount=0, gas=None)`: Call a contract method.
- `call_as(account, method_name, args=None, amount=0, gas=None)`: Call a contract method as a different account.
- `view(method_name, args=None)`: Call a view method on the contract.

### `NearAccount`

Represents an account on the NEAR blockchain.

#### Methods

- `create_subaccount(name, initial_balance=None)`: Create a sub-account.
- `balance()`: Get the account balance in yoctoNEAR.
- `call(contract_id, method_name, args=None, amount=0, gas=None)`: Call a contract method.
- `view(contract_id, method_name, args=None)`: Call a view method on a contract.
- `transfer(receiver_id, amount)`: Transfer NEAR tokens to another account.
- `deploy_contract(wasm_file)`: Deploy a contract to this account.

## Running Tests

To run tests with near-pytest, simply use pytest as usual:

```bash
pytest -xvs tests/
```

### pytest options

The plugin adds the following pytest options:

- `--near-home`: Path to NEAR home directory for the sandbox.
- `--near-port`: Port for the NEAR sandbox RPC server (default: 3030).
- `--near-reset`: Reset the NEAR sandbox before running tests.

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/near/near-pytest.git
cd near-pytest

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

## License

MIT