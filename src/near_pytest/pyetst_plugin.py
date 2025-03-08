# near_pytest/pytest_plugin.py
"""
Pytest plugin for near-pytest.
"""

import pytest
from pathlib import Path

from .core.sandbox_manager import SandboxManager
from .core.contract_manager import ContractManager

# Initialize the sandbox manager if needed
_sandbox_manager = None
_contract_manager = None

def pytest_addoption(parser):
    """Add near-pytest options to pytest."""
    group = parser.getgroup("near-pytest")
    group.addoption(
        "--near-home",
        action="store",
        dest="near_home",
        default=None,
        help="Path to NEAR home directory for the sandbox",
    )
    group.addoption(
        "--near-port",
        action="store",
        dest="near_port",
        default=3030,
        type=int,
        help="Port for the NEAR sandbox RPC server",
    )
    group.addoption(
        "--near-reset",
        action="store_true",
        dest="near_reset",
        default=False,
        help="Reset the NEAR sandbox before running tests",
    )

@pytest.fixture(scope="session")
def near_sandbox(request):
    """
    Fixture that provides access to the NEAR sandbox.
    
    This is a session-scoped fixture, so the sandbox is started once
    for the entire test session.
    """
    global _sandbox_manager
    
    # Get options
    near_home = request.config.getoption("near_home")
    near_port = request.config.getoption("near_port")
    near_reset = request.config.getoption("near_reset")
    
    # Create the sandbox manager if it doesn't exist
    if _sandbox_manager is None:
        _sandbox_manager = SandboxManager.get_instance(
            home_dir=near_home,
            port=near_port,
        )
        _sandbox_manager.start()
    
    # Reset if requested
    if near_reset:
        _sandbox_manager.reset_state()
    
    # Return the manager
    return _sandbox_manager

@pytest.fixture(scope="session")
def near_contract_manager(near_sandbox):
    """
    Fixture that provides access to the NEAR contract manager.
    
    This is a session-scoped fixture, so the contract manager is created once
    for the entire test session.
    """
    global _contract_manager
    
    # Create the contract manager if it doesn't exist
    if _contract_manager is None:
        _contract_manager = ContractManager(near_sandbox)
    
    # Return the manager
    return _contract_manager

@pytest.fixture
def compile_contract(near_contract_manager):
    """
    Fixture that provides a function to compile NEAR contracts.
    
    This is a function-scoped fixture, so a new function is created for each test.
    """
    def _compile(contract_path):
        return near_contract_manager.compile_contract(contract_path)
    
    return _compile