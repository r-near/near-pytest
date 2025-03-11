from typing import Dict, Any, Optional, TYPE_CHECKING, List, Union, Tuple, cast
from py_near.constants import DEFAULT_ATTACHED_GAS
from py_near.models import TransactionResult
from .utils.logger import logger
import base64

# Prevent circular imports while still enabling type checking
if TYPE_CHECKING:
    from .client import NearClient


class ContractCallError(Exception):
    """Error raised when a contract call fails"""

    def __init__(
        self, message: str, transaction_result: Optional[TransactionResult] = None
    ):
        self.transaction_result = transaction_result
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        if not self.transaction_result:
            return self.message

        tx = self.transaction_result
        error_info = {
            "message": self.message,
            "transaction_hash": tx.transaction.hash,
            "signer": tx.transaction.signer_id,
            "receiver": tx.transaction.receiver_id,
        }

        # Extract method call and arguments from transaction actions
        for action in tx.transaction.actions:
            if action.transactions_type == "FunctionCall":
                error_info["method_name"] = action.method_name
                error_info["args"] = action.args
                error_info["gas"] = action.gas
                error_info["deposit"] = action.deposit
                break

        # Add logs
        error_info["logs"] = tx.logs

        # Transaction status details
        if "Failure" in tx.status:
            error_info["failure_details"] = tx.status["Failure"]

        # Extract detailed error from transaction outcome
        if tx.transaction_outcome.error:
            error_info["transaction_error"] = str(tx.transaction_outcome.error)

        # Extract any receipt errors
        if tx.receipt_outcome:
            receipt_errors = []
            for i, ro in enumerate(tx.receipt_outcome):
                if ro.error:
                    receipt_errors.append(
                        {"receipt_id": ro.receipt_id, "error": str(ro.error)}
                    )

            if receipt_errors:
                error_info["receipt_errors"] = receipt_errors

        import json

        return json.dumps(error_info, indent=2, default=str)


class Account:
    """A simplified account model for interacting with the NEAR blockchain.

    This class provides a high-level abstraction for account operations such as
    calling contracts, viewing contract state, and deploying contracts.

    Attributes:
        client: The NearClient instance used for RPC communication
        account_id: The NEAR account ID
    """

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
        return_full_result: bool = False,
    ) -> Union[str, Tuple[str, TransactionResult]]:
        """Call a contract method.

        Args:
            contract_id: The contract account ID
            method_name: The contract method to call
            args: Arguments to pass to the method
            amount: Amount of NEAR tokens to attach (in yoctoNEAR)
            gas: Amount of gas to attach
            return_full_result: Whether to return both the parsed value and full result

        Returns:
            Either the parsed result as a string, or a tuple of (parsed_result, full_result)

        Raises:
            ContractCallError: If the contract call fails
        """
        result = self.client.call_function(
            self.account_id, contract_id, method_name, args, amount, gas
        )

        return self._process_call_result(result, return_full_result)

    def view_contract(
        self, contract_id: str, method_name: str, args: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Call a view method on a contract.

        Args:
            contract_id: The contract account ID
            method_name: The view method to call
            args: Arguments to pass to the method

        Returns:
            The result of the view method call
        """
        return self.client.view_function(contract_id, method_name, args)

    def deploy_contract(self, wasm_file) -> Any:
        """Deploy a contract to this account.

        Args:
            wasm_file: Path to the WASM file or WASM binary data

        Returns:
            The result of the deployment operation
        """
        return self.client.deploy_contract(self.account_id, wasm_file)

    def _process_call_result(
        self, result: Union[str, TransactionResult], return_full_result: bool = False
    ) -> Union[str, Tuple[str, TransactionResult]]:
        """Process the result of a contract call.

        Args:
            result: The result from the client call
            return_full_result: Whether to return both parsed value and full result

        Returns:
            Either the parsed result as a string, or a tuple of (parsed_result, full_result)

        Raises:
            ContractCallError: If the contract call failed
        """
        if isinstance(result, str):
            return (
                (result, cast(TransactionResult, None))
                if return_full_result
                else result
            )

        # Print contract logs
        logs: List[str] = []
        for ro in result.receipt_outcome:
            logs.extend(ro.logs)
        if logs:
            logger.info("Contract Logs:")
            logger.info("\n".join(logs))

        status = result.status
        if "SuccessValue" in status:
            parsed_value = base64.b64decode(status["SuccessValue"]).decode("utf-8")
            return (parsed_value, result) if return_full_result else parsed_value
        else:
            raise ContractCallError("Error calling function", result)


class Contract:
    """A simplified contract model for interacting with NEAR smart contracts.

    This class provides a high-level abstraction for contract operations such as
    calling methods and viewing contract state.

    Attributes:
        client: The NearClient instance used for RPC communication
        account_id: The contract account ID
    """

    def __init__(self, client: "NearClient", contract_account_id: str):
        self.client = client
        self.account_id = contract_account_id

    def call(
        self,
        method_name: str,
        args: Optional[Dict[str, Any]] = None,
        amount: int = 0,
        gas: Optional[int] = DEFAULT_ATTACHED_GAS,
        return_full_result: bool = False,
    ) -> Union[str, Tuple[str, TransactionResult]]:
        """Call the contract as itself.

        Args:
            method_name: The contract method to call
            args: Arguments to pass to the method
            amount: Amount of NEAR tokens to attach (in yoctoNEAR)
            gas: Amount of gas to attach
            return_full_result: Whether to return both the parsed value and full result

        Returns:
            Either the parsed result as a string, or a tuple of (parsed_result, full_result)

        Raises:
            ContractCallError: If the contract call fails
        """
        result = self.client.call_function(
            self.account_id, self.account_id, method_name, args, amount, gas
        )

        return self._process_call_result(result, return_full_result)

    def call_as(
        self,
        account: Account,
        method_name: str,
        args: Optional[Dict[str, Any]] = None,
        amount: int = 0,
        gas: Optional[int] = DEFAULT_ATTACHED_GAS,
        return_full_result: bool = False,
    ) -> Union[str, Tuple[str, TransactionResult]]:
        """Call the contract as a different account.

        Args:
            account: The account to call the contract as
            method_name: The contract method to call
            args: Arguments to pass to the method
            amount: Amount of NEAR tokens to attach (in yoctoNEAR)
            gas: Amount of gas to attach
            return_full_result: Whether to return both the parsed value and full result

        Returns:
            Either the parsed result as a string, or a tuple of (parsed_result, full_result)

        Raises:
            ContractCallError: If the contract call fails
        """
        result = self.client.call_function(
            account.account_id, self.account_id, method_name, args, amount, gas
        )

        return self._process_call_result(result, return_full_result)

    def view(self, method_name: str, args: Optional[Dict[str, Any]] = None) -> Any:
        """Call a view method on the contract.

        Args:
            method_name: The view method to call
            args: Arguments to pass to the method

        Returns:
            The result of the view method call
        """
        return self.client.view_function(self.account_id, method_name, args)

    def _process_call_result(
        self, result: Union[str, TransactionResult], return_full_result: bool = False
    ) -> Union[str, Tuple[str, TransactionResult]]:
        """Process the result of a contract call.

        Args:
            result: The result from the client call
            return_full_result: Whether to return both parsed value and full result

        Returns:
            Either the parsed result as a string, or a tuple of (parsed_result, full_result)

        Raises:
            ContractCallError: If the contract call failed
        """
        if isinstance(result, str):
            return (
                (result, cast(TransactionResult, None))
                if return_full_result
                else result
            )

        # Print contract logs
        logger.info("Contract Logs:")
        logger.info("\n".join(result.logs))

        status = result.status
        if "SuccessValue" in status:
            parsed_value = base64.b64decode(status["SuccessValue"]).decode("utf-8")
            return (parsed_value, result) if return_full_result else parsed_value
        else:
            raise ContractCallError("Error calling function", result)
