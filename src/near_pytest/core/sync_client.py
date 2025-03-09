import asyncio
import uuid
from pathlib import Path
from typing import Optional, Dict
from py_near.account import Account
from nacl.signing import SigningKey
from py_near.providers import JsonProvider
from py_near.constants import DEFAULT_ATTACHED_GAS
from py_near.dapps.core import NEAR
import base58
from py_near.models import ViewFunctionResult


class SyncNearClient:
    """Synchronous wrapper around py-near's async API."""

    def __del__(self):
        """Clean up resources when the object is deleted."""
        if hasattr(self, "_loop") and self._loop is not None:
            if self._loop.is_running():
                self._loop.stop()
            if not self._loop.is_closed():
                self._loop.close()

    def __init__(
        self,
        rpc_endpoint: str,
        master_account_id: Optional[str] = None,
        master_private_key: Optional[bytes] = None,
    ):
        """
        Initialize the synchronous client.

        Args:
            rpc_endpoint: RPC endpoint URL for the NEAR node
            master_account_id: Master account ID (default: test.near for sandbox)
            master_private_key: Private key for the master account
        """
        self.endpoint = rpc_endpoint
        self.master_account_id = master_account_id or "test.near"
        self.master_private_key = master_private_key

        # Account cache
        self._accounts: Dict[str, Account] = {}

        # Create a persistent event loop for async operations
        self._loop = asyncio.new_event_loop()

        # Initialize the master account
        self._master_account = self._create_py_near_account(
            self.master_account_id, self.master_private_key
        )

    def _create_py_near_account(
        self, account_id: str, private_key: Optional[bytes] = None
    ) -> Account:
        """Create a py-near Account object and initialize it."""

        # Generate a key pair if not provided
        if private_key is None:
            private_key = bytes(SigningKey.generate())

        # Create the account
        account = Account(account_id, private_key, rpc_addr=self.endpoint)

        # Initialize the account - use our safe_run_async method
        self.safe_run_async(account.startup())

        return account

    def get_account(self, account_id) -> Account:
        """
        Get an account by ID, creating it if it doesn't exist.

        Args:
            account_id: Account ID to get or create

        Returns:
            py_near.account.Account: The account object
        """
        # Check if the account is already in our cache
        if account_id not in self._accounts:
            print(f"Account {account_id} not found in cache, creating...")
            # The account doesn't exist
            # We'll create it as a subaccount of the master account
            if account_id.endswith(f".{self.master_account_id}"):
                # It's already properly formatted as a subaccount
                name = account_id.split(".")[0]
            else:
                # Format as a proper subaccount name
                name = account_id
                account_id = f"{name}.{self.master_account_id}"

            # Create the account
            self.create_account(name)

        return self._accounts[account_id]

    def create_account(self, name, initial_balance=None):
        """
        Create a new account.

        Args:
            name: Account name (without the .test.near suffix)
            initial_balance: Initial balance in yoctoNEAR

        Returns:
            account_id: The full account ID of the created account
        """
        # Generate a unique account ID
        unique_id = str(uuid.uuid4())[:8]
        account_id = f"{name}-{unique_id}.{self.master_account_id}"
        print("Creating account (inside create_account method):", account_id)

        # Generate a new signing key
        key_pair = SigningKey.generate()

        # To get the expanded secret key (64 bytes), we can access the _signing_key attribute
        # This is the expanded form that contains both the seed and the 'prefix' that's derived from it
        expanded_secret_key = key_pair._signing_key

        # Format the keys as strings with the ed25519: prefix
        public_key_str = "ed25519:" + base58.b58encode(
            bytes(key_pair.verify_key)
        ).decode("utf-8")
        expanded_private_key_str = "ed25519:" + base58.b58encode(
            expanded_secret_key
        ).decode("utf-8")

        # Print the keys
        print("Public key:", public_key_str)
        print("Expanded private key (64 bytes):", expanded_private_key_str)

        # Set default initial balance if not provided
        if initial_balance is None:
            initial_balance = 10 * NEAR  # 10 NEAR

        # Call create_account on the master account
        master = self._master_account
        result = self.safe_run_async(
            master.create_account(account_id, public_key_str, initial_balance)
        )
        print(result)

        # Create and cache the new account
        self._accounts[account_id] = self._create_py_near_account(
            account_id, expanded_private_key_str
        )
        print("Account created:", account_id)

        return account_id

    def view_account(self, account_id: str) -> dict:
        """Get account information."""
        result = self.safe_run_async(
            JsonProvider(self.endpoint).get_account(account_id)
        )
        return result

    def get_balance(self, account_id: str) -> str:
        """Get account balance in yoctoNEAR."""
        account = self.get_account(account_id)
        balance = self.safe_run_async(account.get_balance())
        return balance

    def call_function(
        self,
        sender_id: str,
        contract_id: str,
        method_name: str,
        args: Optional[Dict] = {},
        gas: int = DEFAULT_ATTACHED_GAS,
        amount: int = 0,
        nowait: bool = False,
        included: bool = False,
    ):
        """
        Call a contract function.

        Args:
            sender_id: Account ID to send from
            contract_id: Contract account ID
            method_name: Method name to call
            args: Arguments for the method
            amount: Amount to attach in yoctoNEAR
            gas: Gas to attach

        Returns:
            Result of the function call
        """
        if args is None:
            args = {}

        if gas is None:
            gas = DEFAULT_ATTACHED_GAS

        # Get the sender account
        sender = self.get_account(sender_id)

        print(f"Calling function {method_name} on contract {contract_id}")
        print(f"{args=}")
        print(f"{amount=}")
        print(f"{gas=}")
        print(f"{nowait=}")

        # Call the function
        result = self.safe_run_async(
            sender.function_call(
                contract_id=contract_id,
                method_name=method_name,
                args=args,
                gas=gas,
                amount=amount,
                nowait=nowait,
                included=included,
            )
        )

        # Extract and return the result
        return self._extract_result(result)

    def view_function(self, contract_id, method_name, args=None) -> ViewFunctionResult:
        """
        Call a view function.

        Args:
            contract_id: Contract account ID
            method_name: Method name to call
            args: Arguments for the method

        Returns:
            Result of the view function call
        """
        if args is None:
            args = {}

        # View functions can be called from any account
        master = self._master_account

        result = self.safe_run_async(
            master.view_function(contract_id, method_name, args)
        )

        return result

    def deploy_contract(self, account_id, wasm_binary):
        """
        Deploy a contract to an account.

        Args:
            account_id: Account ID to deploy to
            wasm_binary: WASM binary as bytes or path to WASM file

        Returns:
            Result of the deployment
        """
        # If wasm_binary is a path, read it
        if isinstance(wasm_binary, (str, Path)):
            with open(wasm_binary, "rb") as f:
                wasm_binary = f.read()

        # Get the account
        account = self.get_account(account_id)
        print("Deploying contract to account:", account_id)
        print("Py-Near Account Obj: ", account)

        # Deploy the contract
        result = self.safe_run_async(account.deploy_contract(wasm_binary))

        return self._extract_result(result)

    def send_tokens(self, sender_id, receiver_id, amount):
        """
        Send NEAR tokens from one account to another.

        Args:
            sender_id: Sender account ID
            receiver_id: Receiver account ID
            amount: Amount to send in yoctoNEAR

        Returns:
            Result of the transfer
        """
        try:
            # Get the sender account
            sender = self.get_account(sender_id)

            # Send the tokens
            result = self.safe_run_async(sender.send_money(receiver_id, amount))

            return self._extract_result(result)

        except Exception as e:
            raise Exception(f"Failed to send tokens: {str(e)}")

    def _extract_result(self, transaction_result):
        """Extract the result from a transaction result."""
        # This depends on the structure of py-near's transaction result
        # For now, we'll return the whole result
        return transaction_result

    def safe_run_async(self, coroutine):
        """
        Safely run an async coroutine, handling event loop issues.

        This uses a persistent event loop to avoid "Event loop is closed" errors.
        """
        try:
            # Check if we're already in an event loop
            try:
                current_loop = asyncio.get_running_loop()
                # If we get here, we're already in an event loop
                # Create a future in this loop
                future = asyncio.run_coroutine_threadsafe(coroutine, current_loop)
                return future.result()
            except RuntimeError:
                # No running event loop, use our persistent one
                return self._loop.run_until_complete(coroutine)
        except Exception as e:
            if "Event loop is closed" in str(e):
                # If our loop got closed, create a new one
                self._loop = asyncio.new_event_loop()
                return self._loop.run_until_complete(coroutine)
            raise
