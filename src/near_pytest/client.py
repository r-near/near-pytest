# near_pytest/client.py
import asyncio
from typing import Any, Dict, Optional, Union
from pathlib import Path
import uuid

from py_near.account import Account
from py_near.constants import DEFAULT_ATTACHED_GAS
from nacl.signing import SigningKey
import base58


class NearClient:
    """A simplified client that manages both sandbox and account operations"""

    def __init__(self, rpc_endpoint: str, master_account_id: str, master_key: str):
        self.rpc_endpoint = rpc_endpoint
        self.master_account_id = master_account_id
        self.master_key = master_key
        self._accounts: Dict[str, Account] = {}  # Cache of accounts

        # Initialize the event loop once
        self._loop = asyncio.new_event_loop()

        # Initialize master account
        self._master_account = self._get_or_create_account(
            master_account_id, master_key
        )

    def __del__(self):
        """Clean up resources"""
        if hasattr(self, "_loop") and self._loop and not self._loop.is_closed():
            self._loop.close()

    def _run_async(self, coro):
        """Simplified method to run async code synchronously"""
        return self._loop.run_until_complete(coro)

    def _get_or_create_account(
        self, account_id: str, private_key: Optional[str] = None
    ) -> Account:
        """Get or create a py-near Account"""
        if account_id in self._accounts:
            return self._accounts[account_id]

        # Generate a key pair if not provided
        if private_key is None:
            key_pair = SigningKey.generate()
            expanded_key = key_pair._signing_key
            private_key = "ed25519:" + base58.b58encode(expanded_key).decode("utf-8")

        # Create and initialize the account
        account = Account(account_id, private_key, rpc_addr=self.rpc_endpoint)
        self._run_async(account.startup())
        self._accounts[account_id] = account

        return account

    # Core operations

    def create_account(self, name: str, initial_balance: Optional[int] = None) -> str:
        """Create a new account as a subaccount of the master account"""
        unique_id = str(uuid.uuid4())[:8]
        account_id = f"{name}-{unique_id}.{self.master_account_id}"

        # Generate new key pair
        key_pair = SigningKey.generate()
        public_key = "ed25519:" + base58.b58encode(bytes(key_pair.verify_key)).decode(
            "utf-8"
        )
        expanded_key = key_pair._signing_key
        private_key = "ed25519:" + base58.b58encode(expanded_key).decode("utf-8")

        # Create the account using master account
        self._run_async(
            self._master_account.create_account(
                account_id,
                public_key,
                initial_balance or 10_000_000_000_000_000_000_000_000,
            )
        )

        # Initialize and cache the account
        self._get_or_create_account(account_id, private_key)

        return account_id

    def call_function(
        self,
        sender_id: str,
        contract_id: str,
        method_name: str,
        args: Optional[Dict] = None,
        amount: int = 0,
        gas: int = DEFAULT_ATTACHED_GAS,
    ) -> Any:
        """Call a contract function"""
        sender = self._get_or_create_account(sender_id)
        if gas is None:
            gas = DEFAULT_ATTACHED_GAS
        result = self._run_async(
            sender.function_call(
                contract_id=contract_id,
                method_name=method_name,
                args=args or {},
                amount=amount,
                gas=gas,
            )
        )
        return result

    def view_function(
        self, contract_id: str, method_name: str, args: Optional[Dict] = None
    ) -> Any:
        """Call a view function"""
        result = self._run_async(
            self._master_account.view_function(contract_id, method_name, args or {})
        )
        return result.result

    def deploy_contract(
        self, account_id: str, wasm_file: Union[str, bytes, Path]
    ) -> Any:
        """Deploy a contract to an account"""
        account = self._get_or_create_account(account_id)

        # Read wasm file if path is provided
        if isinstance(wasm_file, (str, Path)):
            with open(wasm_file, "rb") as f:
                wasm_binary = f.read()
        else:
            wasm_binary = wasm_file

        result = self._run_async(account.deploy_contract(wasm_binary))
        return result
