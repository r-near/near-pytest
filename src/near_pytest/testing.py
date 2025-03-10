# near_pytest/testing.py
from pathlib import Path
from typing import Dict, Any, Optional, Union
import pytest

from .sandbox import SandboxManager
from near_pytest.client import NearClient
from .models import Account, Contract


class NearTestCase:
    """A simplified base class for NEAR smart contract tests"""

    # Class-level shared resources
    _sandbox = None
    _client = None
    _initial_state = None

    @classmethod
    def setup_class(cls):
        """Set up shared resources for the test class"""
        # Start the sandbox if not running
        cls._sandbox = SandboxManager.get_instance()
        cls._sandbox.start()

        # Create the client
        cls._client = NearClient(
            cls._sandbox.rpc_endpoint(), "test.near", cls._sandbox.get_validator_key()
        )

        # Create a reference to the master account
        cls.master = Account(cls._client, "test.near")

    @classmethod
    def compile_contract(cls, contract_path: Union[str, Path]) -> Path:
        """Compile a contract"""
        from .compiler import compile_contract

        return compile_contract(contract_path)

    @classmethod
    def create_account(
        cls, name: str, initial_balance: Optional[int] = None
    ) -> Account:
        """Create a new test account"""
        account_id = cls._client.create_account(name, initial_balance)
        account = Account(cls._client, account_id)

        # Store the account as a class attribute
        setattr(cls, name, account)

        return account

    @classmethod
    def deploy_contract(
        cls,
        account: Account,
        wasm_path: Union[str, Path],
        init_args: Optional[Dict[str, Any]] = None,
    ) -> Contract:
        """Deploy a contract to an account"""
        # Deploy the contract
        account.deploy_contract(wasm_path)

        # Call the init method if args provided
        if init_args:
            account.call_contract(account.account_id, "new", init_args)

        # Create and return a contract proxy
        contract = Contract(cls._client, account.account_id)

        # Try to create a sensible attribute name for the contract
        account_base_name = account.account_id.split("-")[0]
        if not hasattr(cls, f"{account_base_name}_contract"):
            setattr(cls, f"{account_base_name}_contract", contract)

        return contract

    @classmethod
    def save_state(cls):
        """Save the current state for later reset"""
        cls._initial_state = cls._sandbox.dump_state()
        print(f"State saved with {len(cls._initial_state)} records")

    def reset_state(self):
        """Reset to the previously saved state"""
        if self.__class__._initial_state is None:
            pytest.warn(
                "No initial state saved. Call save_state() in setup_class first."
            )
            return False

        result = self._client._run_async(
            self._client._master_account.provider.json_rpc(
                "sandbox_patch_state", params={"records": self.__class__._initial_state}
            )
        )

        success = result == {}
        if success:
            print("Successfully reset state to initial snapshot")
        else:
            print("Warning: Failed to reset state")

        return success
