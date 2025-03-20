from typing import Dict, Any, Optional, TYPE_CHECKING, List, Union, Tuple, TypeVar
from py_near.constants import DEFAULT_ATTACHED_GAS
from py_near.models import TransactionResult
from .utils.logger import logger
import base64
import json

# Prevent circular imports while still enabling type checking
if TYPE_CHECKING:
    from .client import NearClient

T = TypeVar("T")


class ContractResponse:
    """Wrapper for contract call responses that adds additional functionality like JSON parsing.

    This class encapsulates the response processing logic and provides a clean API for
    interacting with contract call results.

    Attributes:
        value: The decoded string value from the contract call
        transaction_result: The full transaction result if available
    """

    @classmethod
    def from_result(
        cls, result: Union[str, int, TransactionResult], log_prefix: str = "Contract"
    ) -> "ContractResponse":
        """Create a ContractResponse from a raw result.

        Args:
            result: Either a string result or a TransactionResult
            log_prefix: Prefix for log messages

        Returns:
            A new ContractResponse instance

        Raises:
            ContractCallError: If the contract call failed
        """
        if isinstance(result, str) or isinstance(result, int):
            return cls(result)

        # Process logs
        logs: List[str] = []
        for ro in result.receipt_outcome:
            logs.extend(ro.logs)
        if logs:
            logger.info(f"{log_prefix} Logs:")
            logger.info("\n".join(logs))

        status = result.status
        if "SuccessValue" in status:
            parsed_value = base64.b64decode(status["SuccessValue"]).decode("utf-8")
            return cls(parsed_value, result)
        else:
            raise ContractCallError("Error calling function", result)

    def __init__(
        self,
        value: Union[str, int],
        transaction_result: Optional[TransactionResult] = None,
    ):
        """Initialize a ContractResponse.

        Args:
            value: The string value from the contract call
            transaction_result: The full transaction result if available
        """
        self.value = value
        self.transaction_result = transaction_result

    def __str__(self) -> str:
        """String representation of the response.

        Returns:
            The string value from the contract call
        """
        return str(self.value)

    @property
    def text(self) -> str:
        """Get the response content as a string.

        Returns:
            The string value from the contract call
        """
        return str(self.value)

    def json(self) -> Any:
        """Parse the response value as JSON.

        Returns:
            The parsed JSON object.

        Raises:
            json.JSONDecodeError: If the response is not valid JSON.
        """
        return json.loads(str(self.value))


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
    ) -> Union[ContractResponse, Tuple[ContractResponse, Optional[TransactionResult]]]:
        """Call a contract method.

        Args:
            contract_id: The contract account ID
            method_name: The contract method to call
            args: Arguments to pass to the method
            amount: Amount of NEAR tokens to attach (in yoctoNEAR)
            gas: Amount of gas to attach
            return_full_result: Whether to return both the parsed value and full result

        Returns:
            Either the parsed result as a ContractResponse, or a tuple of (parsed_result, full_result)

        Raises:
            ContractCallError: If the contract call fails
        """
        result = self.client.call_function(
            self.account_id, contract_id, method_name, args, amount, gas
        )

        response = ContractResponse.from_result(result, log_prefix="Account")
        return (
            (response, response.transaction_result) if return_full_result else response
        )

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
    ) -> Union[ContractResponse, Tuple[ContractResponse, Optional[TransactionResult]]]:
        """Call the contract as itself.

        Args:
            method_name: The contract method to call
            args: Arguments to pass to the method
            amount: Amount of NEAR tokens to attach (in yoctoNEAR)
            gas: Amount of gas to attach
            return_full_result: Whether to return both the parsed value and full result

        Returns:
            Either the parsed result as a ContractResponse, or a tuple of (parsed_result, full_result)

        Raises:
            ContractCallError: If the contract call fails
        """
        result = self.client.call_function(
            self.account_id, self.account_id, method_name, args, amount, gas
        )

        response = ContractResponse.from_result(result)
        return (
            (response, response.transaction_result) if return_full_result else response
        )

    def call_as(
        self,
        account: Account,
        method_name: str,
        args: Optional[Dict[str, Any]] = None,
        amount: int = 0,
        gas: Optional[int] = DEFAULT_ATTACHED_GAS,
        return_full_result: bool = False,
    ) -> Union[ContractResponse, Tuple[ContractResponse, Optional[TransactionResult]]]:
        """Call the contract as a different account.

        Args:
            account: The account to call the contract as
            method_name: The contract method to call
            args: Arguments to pass to the method
            amount: Amount of NEAR tokens to attach (in yoctoNEAR)
            gas: Amount of gas to attach
            return_full_result: Whether to return both the parsed value and full result

        Returns:
            Either the parsed result as a ContractResponse, or a tuple of (parsed_result, full_result)

        Raises:
            ContractCallError: If the contract call fails
        """
        result = self.client.call_function(
            account.account_id, self.account_id, method_name, args, amount, gas
        )

        response = ContractResponse.from_result(result)
        return (
            (response, response.transaction_result) if return_full_result else response
        )

    def view(
        self, method_name: str, args: Optional[Dict[str, Any]] = None
    ) -> ContractResponse:
        """Call a view method on the contract.

        Args:
            method_name: The view method to call
            args: Arguments to pass to the method

        Returns:
            The result of the view method call
        """
        result = self.client.view_function(self.account_id, method_name, args)
        return ContractResponse.from_result(result)
