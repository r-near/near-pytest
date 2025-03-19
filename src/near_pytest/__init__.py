"""
near-pytest: A pytest-native approach for testing NEAR smart contracts in Python.
"""

# Import main components to expose them at the package level
from .testing import NearTestCase
from .client import NearClient
from .models import Account, Contract, ContractCallError
from .sandbox import SandboxManager
from .compiler import compile_contract
from . import fixtures

__version__ = "0.1.0"

__all__ = [
    "NearTestCase",
    "NearClient",
    "Account",
    "Contract",
    "ContractCallError",
    "SandboxManager",
    "compile_contract",
    "fixtures",
]
