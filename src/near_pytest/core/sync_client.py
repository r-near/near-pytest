import asyncio
import uuid
from pathlib import Path
from typing import Optional


class SyncNearClient:
    """Synchronous wrapper around py-near's async API."""

    def __del__(self):
        """Clean up resources when the object is deleted."""
        if hasattr(self, "_loop") and self._loop is not None:
            if self._loop.is_running():
                self._loop.stop()
            if not self._loop.is_closed():
                self._loop.close()

    def __init__(self, rpc_endpoint, master_account_id=None, master_private_key=None):
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
        self._accounts = {}

        # Create a persistent event loop for async operations
        self._loop = asyncio.new_event_loop()

        # Initialize the master account
        self._master_account = self._create_py_near_account(
            self.master_account_id, self.master_private_key
        )

    def _create_py_near_account(
        self, account_id: str, private_key: Optional[bytes] = None
    ):
        """Create a py-near Account object and initialize it."""
        try:
            # Import py-near
            from py_near.account import Account
            from nacl.public import PrivateKey

            # Generate a key pair if not provided
            if private_key is None:
                private_key = bytes(PrivateKey.generate())

            # Create the account
            account = Account(account_id, private_key, rpc_addr=self.endpoint)

            # Initialize the account - use our safe_run_async method
            self.safe_run_async(account.startup())

            return account
        except ImportError:
            raise ImportError(
                "py-near is not installed. Please install it with 'pip install py-near'"
            )

    def get_account(self, account_id):
        """Get an account by ID, creating it if necessary."""
        if account_id not in self._accounts:
            # For simplicity, we assume the account exists
            # In a real implementation, we'd check if it exists and create it if not
            self._accounts[account_id] = self._create_py_near_account(account_id)

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
        try:
            from py_near.dapps.core import NEAR
            from nacl.public import PrivateKey

            # Generate a unique account ID
            unique_id = str(uuid.uuid4())[:8]
            account_id = f"{name}-{unique_id}.{self.master_account_id}"

            # Generate a key pair
            key_pair = PrivateKey.generate()

            # Set default initial balance if not provided
            if initial_balance is None:
                initial_balance = 10 * NEAR  # 10 NEAR

            # Call create_account on the master account
            master = self._master_account
            result = self.safe_run_async(
                master.create_account(
                    account_id, bytes(key_pair.public_key), initial_balance
                )
            )

            # Create and cache the new account
            self._accounts[account_id] = self._create_py_near_account(
                account_id, bytes(key_pair)
            )

            return account_id

        except Exception as e:
            raise Exception(f"Failed to create account: {str(e)}")

    def view_account(self, account_id):
        """Get account information."""
        master = self._master_account
        result = self.safe_run_async(master.view_account(account_id))
        return result

    def get_balance(self, account_id):
        """Get account balance in yoctoNEAR."""
        account = self.get_account(account_id)
        balance = self.safe_run_async(account.get_balance())
        return balance

    def call_function(
        self, sender_id, contract_id, method_name, args=None, amount=0, gas=None
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
        try:
            from py_near.constants import DEFAULT_ATTACHED_GAS

            if args is None:
                args = {}

            if gas is None:
                gas = DEFAULT_ATTACHED_GAS

            # Get the sender account
            sender = self.get_account(sender_id)

            # Call the function
            result = self.safe_run_async(
                sender.call_function(
                    contract_id, method_name, args, amount=amount, gas=gas
                )
            )

            # Extract and return the result
            return self._extract_result(result)

        except Exception as e:
            raise Exception(f"Failed to call function: {str(e)}")

    def view_function(self, contract_id, method_name, args=None):
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
        try:
            # If wasm_binary is a path, read it
            if isinstance(wasm_binary, (str, Path)):
                with open(wasm_binary, "rb") as f:
                    wasm_binary = f.read()

            # Get the account
            account = self.get_account(account_id)

            # Deploy the contract
            result = self.safe_run_async(account.deploy_contract(wasm_binary))

            return self._extract_result(result)

        except Exception as e:
            raise Exception(f"Failed to deploy contract: {str(e)}")

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
