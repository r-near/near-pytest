# near_pytest/testing/test_case.py
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, Union

# Import the core components
from ..core.sandbox_manager import SandboxManager
from ..core.contract_manager import ContractManager
from ..core.account import NearAccount
from ..core.contract_proxy import ContractProxy
from ..core.sync_client import SyncNearClient
from ..utils.exceptions import SandboxError


class NearTestCase:
    """Base class for NEAR contract test cases."""

    # Class variables to share resources
    _sandbox_manager = None
    _contract_manager = None
    _rpc_client = None
    _root_account = None
    _initial_state = None  # State snapshot after setup_class

    @classmethod
    def setup_class(cls):
        """Set up the test class by initializing shared resources."""
        # This is called once before any tests in the class are run
        cls._sandbox_manager = cls.get_sandbox_manager()
        cls._contract_manager = cls.get_contract_manager()
        cls._rpc_client = cls._create_rpc_client()
        cls._root_account = cls._create_root_account()

    @classmethod
    def teardown_class(cls):
        """Clean up after all tests in the class have run."""
        # This is called once after all tests in the class have run
        # Currently the sandbox is kept running for efficiency
        # It will be cleaned up by the atexit handler when the process exits
        pass

    def setup_method(self):
        """Set up the test method."""
        # The user should override this and call reset_state() if desired
        pass

    def teardown_method(self):
        """Clean up after the test method."""
        # This is called after each test method
        pass

    @classmethod
    def get_sandbox_manager(cls) -> SandboxManager:
        """Get the singleton SandboxManager instance."""
        if cls._sandbox_manager is None:
            # Create and start the sandbox
            cls._sandbox_manager = SandboxManager.get_instance()
            cls._sandbox_manager.start()
        return cls._sandbox_manager

    @classmethod
    def get_contract_manager(cls) -> ContractManager:
        """Get the ContractManager instance."""
        if cls._contract_manager is None:
            # Create the contract manager
            cls._contract_manager = ContractManager(cls.get_sandbox_manager())
        return cls._contract_manager

    @classmethod
    def get_root_account(cls) -> NearAccount:
        """Get the root account (with lots of funds)."""
        if cls._root_account is None:
            # We need to initialize this once the RPC client is set up
            cls._root_account = cls._create_root_account()
        return cls._root_account

    @classmethod
    def compile_contract(cls, contract_path: Union[str, Path]) -> Path:
        """Compile a contract and return the path to the WASM file."""
        contract_manager = cls.get_contract_manager()
        return contract_manager.compile_contract(contract_path)

    def reset_state(self) -> bool:
        """Reset the sandbox state to the initial state captured with save_state()."""
        if self.__class__._initial_state is None:
            print(
                "Warning: No initial state saved. Call save_state() in setup_class first."
            )
            return False

        success = self._rpc_client.patch_state(self.__class__._initial_state)
        if success:
            print("Successfully reset state to initial snapshot")
        else:
            print("Warning: Failed to reset state")
        return success

    def reset_sandbox(self) -> None:
        """
        Completely reset the sandbox state (not just to the initial snapshot).
        This is more expensive than reset_state().
        """
        self.get_sandbox_manager().reset_state()
        # After reset, we need to reconnect the root account
        self.__class__._rpc_client = self._create_rpc_client()
        self.__class__._root_account = self._create_root_account()

    @classmethod
    def create_account(
        cls, name: str, initial_balance: Optional[int] = None
    ) -> NearAccount:
        """
        Create a new account with the specified name.

        Should be called during setup_class to create accounts shared across tests.

        Args:
            name: Base name for the account
            initial_balance: Initial balance in yoctoNEAR

        Returns:
            NearAccount: The created account
        """
        # Use the root account to create the new account
        root = cls.get_root_account()

        # Create the account
        account = root.create_subaccount(name, initial_balance)

        # Store as class attribute for convenience
        setattr(cls, name, account)

        return account

    @classmethod
    def deploy_contract(
        cls,
        account: NearAccount,
        wasm_path: Union[str, Path],
        init_args: Optional[Dict[str, Any]] = None,
    ) -> ContractProxy:
        """
        Deploy a contract to the specified account.

        Should be called during setup_class to deploy contracts shared across tests.

        Args:
            account: Account to deploy the contract to
            wasm_path: Path to the WASM file
            init_args: Arguments for contract initialization

        Returns:
            ContractProxy: A proxy for interacting with the contract
        """
        # Deploy the contract
        account.deploy_contract(wasm_path)

        # Call the init function if arguments are provided
        if init_args:
            account.call(account.account_id, "new", init_args)

        # Return a contract proxy
        contract = ContractProxy(account)

        # Try to derive a sensible attribute name for the contract proxy
        account_base_name = account.account_id.split(".")[0]
        if not hasattr(cls, account_base_name + "_contract"):
            setattr(cls, account_base_name + "_contract", contract)

        return contract

    @classmethod
    def save_state(cls):
        """
        Save the current state as the initial state for tests.
        Should be called at the end of setup_class after all accounts and contracts are set up.
        """
        cls._initial_state = cls.get_sandbox_manager().dump_state()
        print(f"State saved with {len(cls._initial_state)} records")

    @classmethod
    def _create_rpc_client(cls):
        """Create an RPC client for interacting with the sandbox."""
        sandbox_manager = cls.get_sandbox_manager()
        rpc_endpoint = sandbox_manager.rpc_endpoint()

        # For sandbox, we use test.near as the master account
        master_account_id = "test.near"

        # Get the validator key from the sandbox
        try:
            master_private_key = sandbox_manager.get_validator_key()
            print(f"Using validator key: {master_private_key[:8]}...")
        except Exception as e:
            raise SandboxError(f"Could not load validator key: {e}")

        return SyncNearClient(rpc_endpoint, master_account_id, master_private_key)

    @classmethod
    def _create_root_account(cls):
        """Create or connect to the root account in the sandbox."""
        rpc_client = cls._rpc_client
        return NearAccount("test.near", rpc_client)
