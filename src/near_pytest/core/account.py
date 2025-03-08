from pathlib import Path
from typing import Dict, Any, Optional, Union
from ..core.sync_client import SyncNearClient

from ..utils.exceptions import AccountError


class NearAccount:
    """Represents an account on the NEAR blockchain."""

    def __init__(self, account_id: str, rpc_client: SyncNearClient):
        """
        Initialize a NearAccount.

        Args:
            account_id: The NEAR account ID
            rpc_client: Client for making RPC calls
        """
        self._account_id = account_id
        self._rpc_client = rpc_client

    @property
    def account_id(self) -> str:
        """Get the account ID."""
        return self._account_id

    def create_subaccount(
        self, name: str, initial_balance: Optional[int] = None
    ) -> "NearAccount":
        """
        Create a sub-account with the specified name.

        Args:
            name: Base name for the subaccount (will be prefixed with account_id)
            initial_balance: Initial balance in yoctoNEAR

        Returns:
            A new NearAccount instance for the created subaccount
        """
        try:
            new_account_id = self._rpc_client.create_account(name, initial_balance)
            return NearAccount(new_account_id, self._rpc_client)
        except Exception as e:
            raise AccountError(f"Failed to create subaccount: {str(e)}") from e

    def balance(self) -> int:
        """
        Get the account balance in yoctoNEAR.

        Returns:
            Account balance in yoctoNEAR
        """
        try:
            return self._rpc_client.get_balance(self._account_id)
        except Exception as e:
            raise AccountError(f"Failed to get balance: {str(e)}") from e

    def call(
        self,
        contract_id: str,
        method_name: str,
        args: Optional[Dict[str, Any]] = None,
        amount: int = 0,
        gas: int = 0,
    ) -> Any:
        """
        Call a contract method.

        Args:
            contract_id: Target contract account ID
            method_name: Name of the method to call
            args: Arguments to pass to the method
            amount: Amount of NEAR to attach (in yoctoNEAR)
            gas: Gas to attach (in gas units)

        Returns:
            Result of the method call
        """
        try:
            return self._rpc_client.call_function(
                self._account_id, contract_id, method_name, args, amount, gas
            )
        except Exception as e:
            raise AccountError(f"Failed to call contract method: {str(e)}") from e

    def view(
        self, contract_id: str, method_name: str, args: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Call a view method on a contract.

        Args:
            contract_id: Target contract account ID
            method_name: Name of the method to call
            args: Arguments to pass to the method

        Returns:
            Result of the view method call
        """
        try:
            return self._rpc_client.view_function(contract_id, method_name, args)
        except Exception as e:
            raise AccountError(f"Failed to call view method: {str(e)}") from e

    def transfer(self, receiver_id: str, amount: int) -> Dict[str, Any]:
        """
        Transfer NEAR tokens to another account.

        Args:
            receiver_id: Target account ID
            amount: Amount to transfer in yoctoNEAR

        Returns:
            Transaction result
        """
        try:
            return self._rpc_client.send_tokens(self._account_id, receiver_id, amount)
        except Exception as e:
            raise AccountError(f"Failed to transfer tokens: {str(e)}") from e

    def deploy_contract(self, wasm_file: Union[str, bytes, Path]) -> Dict[str, Any]:
        """
        Deploy a contract to this account.

        Args:
            wasm_file: Path to WASM file or WASM binary

        Returns:
            Deployment result
        """
        try:
            return self._rpc_client.deploy_contract(self._account_id, wasm_file)
        except Exception as e:
            raise AccountError(f"Failed to deploy contract: {str(e)}") from e
