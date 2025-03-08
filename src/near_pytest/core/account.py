# near_pytest/core/account.py
import json
import base64
import uuid
from typing import Dict, Any, Optional, Union, List

# Note: We're assuming near-py or similar is used for RPC interactions
# This class defines the interface without implementing the RPC calls directly

class NearAccount:
    """Represents an account on the NEAR blockchain."""
    
    def __init__(self, account_id: str, rpc_client, keystore=None):
        """
        Initialize a NearAccount.
        
        Args:
            account_id: The NEAR account ID
            rpc_client: Client for making RPC calls
            keystore: Optional keystore for managing account keys
        """
        self._account_id = account_id
        self._rpc_client = rpc_client
        self._keystore = keystore
    
    @property
    def account_id(self) -> str:
        """Get the account ID."""
        return self._account_id
    
    def create_subaccount(self, name: str, initial_balance: Optional[int] = None) -> "NearAccount":
        """
        Create a sub-account with the specified name.
        
        Args:
            name: Base name for the subaccount (will be prefixed with account_id)
            initial_balance: Initial balance in yoctoNEAR
            
        Returns:
            A new NearAccount instance for the created subaccount
        """
        # Make account ID unique to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        full_name = f"{name}-{unique_id}.{self._account_id}"
        
        # Create the account using RPC
        if initial_balance is None:
            # Default to a reasonable amount for testing
            initial_balance = 10 * 10**24  # 10 NEAR
        
        # Create account transaction
        result = self._rpc_client.call_function(
            self._account_id,
            "create_account",
            {
                "new_account_id": full_name,
                "new_public_key": self._keystore.create_key(full_name) if self._keystore else None,
                "amount": str(initial_balance)
            }
        )
        
        # Return a new NearAccount instance for the created account
        return NearAccount(full_name, self._rpc_client, self._keystore)
    
    def balance(self) -> int:
        """
        Get the account balance in yoctoNEAR.
        
        Returns:
            Account balance in yoctoNEAR
        """
        # Get account balance using RPC
        result = self._rpc_client.view_account(self._account_id)
        return int(result.get('amount', '0'))
    
    def call(
        self, 
        contract_id: str, 
        method_name: str, 
        args: Optional[Dict[str, Any]] = None, 
        amount: int = 0,
        gas: int = None
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
        if args is None:
            args = {}
        
        if gas is None:
            # Default gas
            gas = 30 * 10**12  # 30 TGas
        
        # Call the contract using RPC
        result = self._rpc_client.call_function(
            self._account_id,
            contract_id,
            method_name,
            args,
            amount=amount,
            gas=gas
        )
        
        # Parse and return the result
        return self._parse_call_result(result)
    
    def view(self, contract_id: str, method_name: str, args: Optional[Dict[str, Any]] = None) -> Any:
        """
        Call a view method on a contract.
        
        Args:
            contract_id: Target contract account ID
            method_name: Name of the method to call
            args: Arguments to pass to the method
            
        Returns:
            Result of the view method call
        """
        if args is None:
            args = {}
        
        # Call the view method using RPC
        result = self._rpc_client.view_function(
            contract_id,
            method_name,
            args
        )
        
        # Parse and return the result
        return self._parse_view_result(result)
    
    def transfer(self, receiver_id: str, amount: int) -> Dict[str, Any]:
        """
        Transfer NEAR tokens to another account.
        
        Args:
            receiver_id: Target account ID
            amount: Amount to transfer in yoctoNEAR
            
        Returns:
            Transaction result
        """
        # Transfer tokens using RPC
        result = self._rpc_client.send_tokens(
            self._account_id,
            receiver_id,
            amount
        )
        
        return result
    
    def deploy_contract(self, wasm_file: Union[str, bytes]) -> Dict[str, Any]:
        """
        Deploy a contract to this account.
        
        Args:
            wasm_file: Path to WASM file or WASM binary
            
        Returns:
            Deployment result
        """
        # Read WASM file if path is provided
        if isinstance(wasm_file, str):
            with open(wasm_file, 'rb') as f:
                wasm_binary = f.read()
        else:
            wasm_binary = wasm_file
        
        # Deploy contract using RPC
        result = self._rpc_client.deploy_contract(
            self._account_id,
            wasm_binary
        )
        
        return result
    
    def _parse_call_result(self, result: Dict[str, Any]) -> Any:
        """Parse the result of a contract call."""
        if 'result' not in result:
            return None
        
        try:
            # Try to decode as JSON
            return json.loads(result['result'])
        except (json.JSONDecodeError, TypeError):
            # Return as-is if not valid JSON
            return result['result']
    
    def _parse_view_result(self, result: Dict[str, Any]) -> Any:
        """Parse the result of a view method call."""
        if 'result' not in result:
            return None
        
        try:
            # Try to decode as JSON
            return json.loads(result['result'])
        except (json.JSONDecodeError, TypeError):
            # Return as-is if not valid JSON
            return result['result']