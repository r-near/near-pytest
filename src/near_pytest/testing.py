from pathlib import Path
from typing import Dict, Any, Optional, Union, ClassVar

from .sandbox import SandboxManager
from .client import NearClient
from .models import Account, Contract
from .utils import logger


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
        print()
        logger.info(f"Setting up {cls.__name__} test class")

        # Create a new sandbox instance for this test class
        cls._sandbox = SandboxManager()
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
            logger.debug(f"Master account reference created: {cls.master.account_id}")

    @classmethod
    def teardown_class(cls):
        """Tear down shared resources for the test class"""
        if cls._sandbox:
            cls._sandbox.stop()
            cls._sandbox = None

    @classmethod
    def compile_contract(
        cls, contract_path: Union[str, Path], single_file: bool = False
    ) -> Path:
        """Compile a contract"""
        from .compiler import compile_contract

        logger.info(f"Compiling contract: {contract_path}")
        result = compile_contract(contract_path, single_file)
        logger.success(f"Contract compiled: {result}")
        return result

    @classmethod
    def create_account(
        cls, name: str, initial_balance: Optional[int] = None
    ) -> Account:
        """Create a new test account"""
        if cls._client is None:
            logger.error("Client not initialized. Make sure setup_class was called.")
            raise RuntimeError(
                "Client not initialized. Make sure setup_class was called."
            )

        logger.info(f"Creating account '{name}'")
        account_id = cls._client.create_account(name, initial_balance)
        account = Account(cls._client, account_id)

        # Store the account as a class attribute
        setattr(cls, name, account)
        logger.success(f"Account created: {account_id}")

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
            logger.error("Client not initialized. Make sure setup_class was called.")
            raise RuntimeError(
                "Client not initialized. Make sure setup_class was called."
            )

        # Deploy the contract
        logger.info(f"Deploying contract to {account.account_id}")
        logger.debug(f"WASM path: {wasm_path}")
        account.deploy_contract(wasm_path)

        # Call the init method if args provided
        if init_args:
            logger.debug(f"Initializing contract with args: {init_args}")
            account.call_contract(account.account_id, "new", init_args)

        # Create and return a contract proxy
        contract = Contract(cls._client, account.account_id)

        # Try to create a sensible attribute name for the contract
        account_base_name = account.account_id.split("-")[0]
        if not hasattr(cls, f"{account_base_name}_contract"):
            setattr(cls, f"{account_base_name}_contract", contract)
            logger.debug(f"Contract reference created: {account_base_name}_contract")

        logger.success(f"Contract deployed to {account.account_id}")
        return contract

    @classmethod
    def save_state(cls):
        """Save the current state for later reset"""
        if cls._sandbox is None:
            logger.error("Sandbox not initialized. Make sure setup_class was called.")
            raise RuntimeError(
                "Sandbox not initialized. Make sure setup_class was called."
            )

        logger.info("Saving current state for later reset")
        cls._initial_state = cls._sandbox.dump_state()
        logger.success(f"State saved with {len(cls._initial_state)} records")

    def reset_state(self):
        """Reset to the previously saved state"""
        print()  # Spacer for pytest
        if self.__class__._initial_state is None:
            logger.warning(
                "No initial state saved. Call save_state() in setup_class first."
            )
            return False

        if self.__class__._client is None:
            logger.error("Client not initialized. Make sure setup_class was called.")
            raise RuntimeError(
                "Client not initialized. Make sure setup_class was called."
            )

        logger.info("Resetting state to initial snapshot")
        result = self.__class__._client._run_async(
            self.__class__._client._master_account.provider.json_rpc(
                "sandbox_patch_state", {"records": self.__class__._initial_state}
            )
        )

        if result == {}:
            success = True
        else:
            success = False

        if success:
            logger.success("Successfully reset state to initial snapshot")
        else:
            logger.warning("Failed to reset state")

        return success
