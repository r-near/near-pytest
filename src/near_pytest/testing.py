from pathlib import Path
from typing import Dict, Any, Optional, Union, ClassVar
import pytest

from .sandbox import SandboxManager
from .client import NearClient
from .models import Account, Contract


class NearTestCase:
    """A simplified base class for NEAR smart contract tests"""

    # Class-level shared resources with proper type annotations
    _sandbox: ClassVar[Optional[SandboxManager]] = None
    _client: ClassVar[Optional[NearClient]] = None
    _initial_state: ClassVar[Optional[list]] = None

    # Account references that will be dynamically created
    master: ClassVar[Optional[Account]] = None

    @classmethod
    def setup_class(cls):
        """Set up shared resources for the test class"""
        # Start the sandbox if not running
        cls._sandbox = SandboxManager.get_instance()
        if cls._sandbox:
            cls._sandbox.start()

            # Create the client
            cls._client = NearClient(
                cls._sandbox.rpc_endpoint(),
                "test.near",
                cls._sandbox.get_validator_key(),
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
        if cls._client is None:
            raise RuntimeError(
                "Client not initialized. Make sure setup_class was called."
            )

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
        if cls._client is None:
            raise RuntimeError(
                "Client not initialized. Make sure setup_class was called."
            )

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
        if cls._sandbox is None:
            raise RuntimeError(
                "Sandbox not initialized. Make sure setup_class was called."
            )

        cls._initial_state = cls._sandbox.dump_state()
        print(f"State saved with {len(cls._initial_state)} records")

    def reset_state(self):
        """Reset to the previously saved state"""
        if self.__class__._initial_state is None:
            pytest.warn(
                "No initial state saved. Call save_state() in setup_class first."
            )
            return False

        if self.__class__._client is None:
            raise RuntimeError(
                "Client not initialized. Make sure setup_class was called."
            )

        result = self.__class__._client._run_async(
            self.__class__._client._master_account.provider.json_rpc(
                "sandbox_patch_state", {"records": self.__class__._initial_state}
            )
        )

        success = result == {}
        if success:
            print("Successfully reset state to initial snapshot")
        else:
            print("Warning: Failed to reset state")

        return success
