from typing import Dict, Any, Optional

from .account import NearAccount


class ContractProxy:
    """Provides a convenient interface for interacting with deployed contracts."""

    def __init__(self, contract_account: NearAccount):
        """
        Initialize a ContractProxy.

        Args:
            contract_account: The account where the contract is deployed
        """
        self._account = contract_account

    @property
    def account_id(self) -> str:
        """Get the account ID where the contract is deployed."""
        return self._account.account_id

    def call(
        self,
        method_name: str,
        args: Optional[Dict[str, Any]] = None,
        amount: int = 0,
        gas: int = 0,
    ) -> Any:
        """
        Call a contract method using the contract account.

        Args:
            method_name: Name of the method to call
            args: Arguments to pass to the method
            amount: Amount of NEAR to attach (in yoctoNEAR)
            gas: Gas to attach (in gas units)

        Returns:
            Result of the method call
        """
        return self._account.call(self.account_id, method_name, args, amount, gas)

    def call_as(
        self,
        account: NearAccount,
        method_name: str,
        args: Optional[Dict[str, Any]] = None,
        amount: int = 0,
        gas: int = 0,
    ) -> Any:
        """
        Call a contract method as a different account.

        Args:
            account: Account to call from
            method_name: Name of the method to call
            args: Arguments to pass to the method
            amount: Amount of NEAR to attach (in yoctoNEAR)
            gas: Gas to attach (in gas units)

        Returns:
            Result of the method call
        """
        return account.call(self.account_id, method_name, args, amount, gas)

    def view(self, method_name: str, args: Optional[Dict[str, Any]] = None) -> Any:
        """
        Call a view method on the contract.

        Args:
            method_name: Name of the method to call
            args: Arguments to pass to the method

        Returns:
            Result of the view method call
        """
        return self._account.view(self.account_id, method_name, args)
