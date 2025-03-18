"""
Modular fixtures for near-pytest.

This module provides a pytest-native approach to NEAR smart contracts testing that
focuses on:
1. Simple, composable fixtures that follow pytest conventions
2. Method chaining for contract calls to improve test readability
3. Ergonomic functions with intuitive names
4. Clear separation of concerns with stateless functions

Getting started:
```python
# Import the fixtures you need
from near_pytest.fixtures import sandbox, localnet_alice_account

# Use the fixtures in your tests
def test_my_contract(sandbox, localnet_alice_account):
    # Your test code here
    pass
```
"""

import pytest
import random
import string
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, TypeVar, Tuple, Generator

from .sandbox import SandboxManager
from .client import NearClient
from .models import Account, Contract, ContractCallError, TransactionResult
from .compiler import compile_contract as compiler_func
from .utils import logger

# Type definitions
T = TypeVar("T")  # Generic type for return values


class ContractCall:
    """
    Wrapper around contract calls to enable method chaining.

    This class provides a fluent interface for calling contract methods,
    letting you decide at the end whether to execute as a transaction
    or as a view call.

    Example:
        contract.call("increment").as_transaction(alice)
        current_count = contract.call("get_count").as_view()
    """

    def __init__(
        self,
        contract: Contract,
        method_name: str,
        args: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.contract = contract
        self.method_name = method_name
        self.args = args or {}

    def as_transaction(
        self, account: Account, amount: int = 0, gas: Optional[int] = None
    ) -> Union[str, Tuple[str, TransactionResult]]:
        """Execute the call as a transaction from the given account."""
        try:
            return self.contract.call_as(
                account, self.method_name, self.args, amount, gas
            )
        except Exception as e:
            logger.error(f"Transaction failed: {self.method_name}({self.args})")
            raise ContractCallError(
                f"Failed to call {self.method_name}: {str(e)}", None
            ) from e

    def as_view(self) -> Any:
        """Execute the call as a view method."""
        try:
            return self.contract.view(self.method_name, self.args)
        except Exception as e:
            logger.error(f"View call failed: {self.method_name}({self.args})")
            raise ContractCallError(
                f"Failed to view {self.method_name}: {str(e)}", None
            ) from e


class EnhancedContract:
    """
    Wrapper around Contract with more ergonomic methods.

    This class enhances the base Contract class with a more intuitive API
    that supports method chaining and clearer semantics.
    """

    def __init__(self, contract: Contract) -> None:
        self._contract = contract

    @property
    def account_id(self) -> str:
        """Get the account ID of the contract."""
        return self._contract.account_id

    def call(self, method_name: str, **kwargs: Any) -> ContractCall:
        """
        Create a contract call that can be executed as transaction or view.

        Args:
            method_name: The name of the contract method to call
            **kwargs: Arguments to pass to the contract method

        Returns:
            A ContractCall object that can be executed as transaction or view
        """
        return ContractCall(self._contract, method_name, kwargs)


class SandboxProxy:
    """
    Proxy for sandbox operations with a simplified interface.

    This class provides a more intuitive API for interacting with the NEAR
    sandbox, including creating accounts and deploying contracts.
    """

    def __init__(self, client: NearClient, sandbox: SandboxManager) -> None:
        self.client = client
        self.sandbox = sandbox
        self.master_account_id: str = "test.near"
        self.network = "localnet"  # Identifies this as using the local network

    def create_account(self, name: str) -> Account:
        """
        Create a new account with the given name.

        Args:
            name: The name for the new account (will be suffixed with .test.near)

        Returns:
            An Account object for the newly created account
        """
        # Create the account and set up the keys
        account_id = self.client.create_account(name)
        logger.info(f"Created account: {account_id}")
        return Account(self.client, account_id)

    def create_random_account(self, prefix: str = "test") -> Account:
        """
        Create a new account with a random name.

        Args:
            prefix: Optional prefix for the random account name

        Returns:
            An Account object for the newly created account
        """
        # Generate random suffix
        suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        name = f"{prefix}-{suffix}"
        return self.create_account(name)

    def deploy(
        self,
        wasm_path: Union[str, Path],
        account: Account,
        init_args: Optional[Dict[str, Any]] = None,
        init_method: str = "new",
    ) -> EnhancedContract:
        """
        Deploy a contract to the given account and optionally initialize it.

        Args:
            wasm_path: Path to the compiled WASM file
            account: Account object to deploy to
            init_args: Optional arguments for contract initialization
            init_method: Name of the initialization method (default: "new")

        Returns:
            An EnhancedContract object for interacting with the deployed contract
        """
        # Deploy the contract
        logger.info(f"Deploying contract to {account.account_id}...")
        account.deploy_contract(wasm_path)

        # Create the contract wrapper
        contract = Contract(self.client, account.account_id)
        enhanced_contract = EnhancedContract(contract)

        # Initialize the contract if args are provided
        if init_args is not None:
            logger.info(f"Initializing contract with {init_method}({init_args})...")
            # Convert dict to kwargs for the call method
            call = enhanced_contract.call(init_method, **init_args)
            call.as_transaction(account)
            logger.success("Contract initialized successfully")

        logger.success(f"Contract deployed to {account.account_id}")
        return enhanced_contract

    def save_state(self) -> List[Dict[str, Any]]:
        """
        Save the current sandbox state for later resetting.

        Returns:
            The sandbox state object
        """
        logger.info("Saving sandbox state...")
        return self.sandbox.dump_state()

    def reset_state(self, state: List[Dict[str, Any]]) -> bool:
        """
        Reset the sandbox to a previously saved state.

        Args:
            state: The state object returned by save_state()

        Returns:
            True if successful, False otherwise
        """
        logger.info("Restoring sandbox state...")
        result = self.client._run_async(
            self.client._master_account.provider.json_rpc(
                "sandbox_patch_state", {"records": state}
            )
        )
        success = result == {}
        if success:
            logger.success("Sandbox state restored successfully")
        else:
            logger.error("Failed to restore sandbox state")
        return success


# Main fixtures for pytest


@pytest.fixture(scope="session")
def sandbox() -> Generator[SandboxProxy, None, None]:
    """
    Start a NEAR sandbox and return a proxy for interacting with it.

    This fixture manages the sandbox lifecycle and provides a simplified
    interface for interacting with it throughout the test session.
    """
    logger.info("Starting NEAR sandbox for test session...")
    sandbox_instance = SandboxManager()
    sandbox_instance.start()

    client = NearClient(
        sandbox_instance.rpc_endpoint(),
        "test.near",
        sandbox_instance.get_validator_key(),
    )

    proxy = SandboxProxy(client, sandbox_instance)
    logger.success("NEAR sandbox started successfully")

    yield proxy

    # Teardown
    logger.info("Stopping NEAR sandbox...")
    sandbox_instance.stop()
    logger.success("NEAR sandbox stopped")


@pytest.fixture
def near_client(sandbox: SandboxProxy) -> NearClient:
    """
    Get the NEAR client for direct RPC operations.

    This fixture provides access to the underlying NEAR client
    for cases where you need direct access to RPC methods.
    """
    return sandbox.client


@pytest.fixture(scope="session")
def localnet_alice_account(sandbox: SandboxProxy) -> Account:
    """
    Create a test account named 'alice' on the localnet.

    This fixture creates a reusable account named 'alice' that
    can be used across multiple tests.
    """
    return sandbox.create_account("alice")


@pytest.fixture(scope="session")
def localnet_bob_account(sandbox: SandboxProxy) -> Account:
    """
    Create a test account named 'bob' on the localnet.

    This fixture creates a reusable account named 'bob' that
    can be used across multiple tests.
    """
    return sandbox.create_account("bob")


@pytest.fixture
def localnet_temp_account(sandbox: SandboxProxy) -> Account:
    """
    Create a temporary account with a random name on the localnet.

    This fixture creates a new account with a random name for each test,
    ensuring test isolation when needed.
    """
    return sandbox.create_random_account()


# For backward compatibility
sandbox_alice = localnet_alice_account
sandbox_bob = localnet_bob_account
temp_account = localnet_temp_account


# Helper function (not a fixture)
def compile_contract(
    contract_path: Union[str, Path], single_file: bool = False
) -> Path:
    """
    Compile a contract and return the WASM path.

    This function is a thin wrapper around the compiler functionality
    from the compiler module, providing a simple interface for
    compiling contracts in tests.

    Args:
        contract_path: Path to the contract source
        single_file: Whether the contract is a single file

    Returns:
        Path to the compiled WASM file
    """
    logger.info(f"Compiling contract: {contract_path}")
    wasm_path = compiler_func(contract_path, single_file=single_file)
    logger.success(f"Contract compiled: {wasm_path}")
    return wasm_path
