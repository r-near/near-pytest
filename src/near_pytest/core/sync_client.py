# near_pytest/core/sync_client.py
import asyncio
import uuid
from pathlib import Path


class SyncNearClient:
    """Synchronous wrapper around py-near's async API."""

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

        # Initialize the master account
        self._master_account = self._create_py_near_account(
            self.master_account_id, self.master_private_key
        )

    def _create_py_near_account(self, account_id, private_key=None):
        """Create a py-near Account object and initialize it."""
        try:
            # Import py-near
            from py_near.account import Account

            # Generate a key pair if not provided
            if private_key is None:
                from nacl.public import PrivateKey

                private_key = PrivateKey.generate()

            # Create the account
            account = Account(
                account_id, bytes(private_key), provider_url=self.endpoint
            )

            # Initialize the account
            asyncio.run(account.startup())

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
            from nacl.public import PrivateKey
            from py_near.dapps.core import NEAR

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
            result = asyncio.run(
                master.create_account(
                    account_id, bytes(key_pair.public_key), initial_balance
                )
            )
            print(result)  # TODO: Remove

            # Create and cache the new account
            self._accounts[account_id] = self._create_py_near_account(
                account_id, key_pair.private_key
            )

            return account_id

        except Exception as e:
            raise Exception(f"Failed to create account: {str(e)}")

    def view_account(self, account_id):
        """Get account information."""
        master = self._master_account
        result = asyncio.run(master.view_account(account_id))
        return result

    def get_balance(self, account_id):
        """Get account balance in yoctoNEAR."""
        account = self.get_account(account_id)
        balance = asyncio.run(account.get_balance())
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
            result = asyncio.run(
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

        result = asyncio.run(master.view_function(contract_id, method_name, args))

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
            result = asyncio.run(account.deploy_contract(wasm_binary))

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
            result = asyncio.run(sender.send_money(receiver_id, amount))

            return self._extract_result(result)

        except Exception as e:
            raise Exception(f"Failed to send tokens: {str(e)}")

    def _extract_result(self, transaction_result):
        """Extract the result from a transaction result."""
        # This depends on the structure of py-near's transaction result
        # For now, we'll return the whole result
        return transaction_result
