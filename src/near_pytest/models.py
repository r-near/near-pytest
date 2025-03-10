# near_pytest/models.py
from typing import Dict, Any, Optional, TYPE_CHECKING
from py_near.constants import DEFAULT_ATTACHED_GAS
import base64

# Prevent circular imports while still enabling type checking
if TYPE_CHECKING:
    from .client import NearClient


class Account:
    """A simplified account model"""

    def __init__(self, client: "NearClient", account_id: str):
        self.client = client
        self.account_id = account_id

    def call_contract(
        self,
        contract_id: str,
        method_name: str,
        args: Optional[Dict[str, Any]] = None,
        amount: int = 0,
        gas: Optional[int] = DEFAULT_ATTACHED_GAS,
    ) -> Any:
        """Call a contract method"""
        result = self.client.call_function(
            self.account_id, contract_id, method_name, args, amount, gas
        )

        status = result.status
        if "SuccessValue" in status:
            return base64.b64decode(status["SuccessValue"]).decode("utf-8")
        else:
            raise Exception(f"Error calling function: {result}")

    def view_contract(
        self, contract_id: str, method_name: str, args: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Call a view method on a contract"""
        return self.client.view_function(contract_id, method_name, args)

    def deploy_contract(self, wasm_file) -> Any:
        """Deploy a contract to this account"""
        return self.client.deploy_contract(self.account_id, wasm_file)


class Contract:
    """A simplified contract model"""

    def __init__(self, client: "NearClient", contract_account_id: str):
        self.client = client
        self.account_id = contract_account_id

    def call(
        self,
        method_name: str,
        args: Optional[Dict[str, Any]] = None,
        amount: int = 0,
        gas: Optional[int] = DEFAULT_ATTACHED_GAS,
    ) -> Any:
        """Call the contract as itself"""
        result = self.client.call_function(
            self.account_id, self.account_id, method_name, args, amount, gas
        )

        status = result.status
        if "SuccessValue" in status:
            return base64.b64decode(status["SuccessValue"]).decode("utf-8")
        else:
            raise Exception(f"Error calling function: {result}")

    def call_as(
        self,
        account: Account,
        method_name: str,
        args: Optional[Dict[str, Any]] = None,
        amount: int = 0,
        gas: Optional[int] = DEFAULT_ATTACHED_GAS,
    ) -> Any:
        """Call the contract as a different account"""
        result = self.client.call_function(
            account.account_id, self.account_id, method_name, args, amount, gas
        )

        status = result.status
        if "SuccessValue" in status:
            return base64.b64decode(status["SuccessValue"]).decode("utf-8")
        else:
            raise Exception(f"Error calling function: {result}")

    def view(self, method_name: str, args: Optional[Dict[str, Any]] = None) -> Any:
        """Call a view method on the contract"""
        return self.client.view_function(self.account_id, method_name, args)
