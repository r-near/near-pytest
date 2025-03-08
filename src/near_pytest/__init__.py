# near_pytest/__init__.py
"""
near-pytest: A pytest-native approach for testing NEAR smart contracts in Python.
"""

from .testing.test_case import NearTestCase
from .core.contract_proxy import ContractProxy
from .core.account import NearAccount
from .core.contract_manager import ContractManager
from .core.sandbox_manager import SandboxManager

__version__ = "0.1.0"

# Convenience functions for use in tests
def compile_contract(contract_path):
    """Compile a contract and return the path to the WASM file."""
    return NearTestCase.compile_contract(contract_path)

__all__ = [
    "NearTestCase",
    "ContractProxy",
    "NearAccount",
    "ContractManager",
    "SandboxManager",
    "compile_contract",
]