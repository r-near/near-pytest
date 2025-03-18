"""
Example test for a Counter contract using the modular fixtures approach.

This example demonstrates how to use the modular fixtures to test a
simple counter contract with clean, readable tests.
"""

import pytest
from pathlib import Path

# Import the modular testing components
from near_pytest.fixtures import (  # noqa: F401
    compile_contract,
    sandbox,
    create_account,
    sandbox_alice,
    sandbox_bob,
    temp_account,
)


@pytest.fixture(scope="session")
def counter_wasm():
    """Compile the counter contract once for the test session."""
    current_dir = Path(__file__).parent
    contract_path = current_dir / "counter_contract" / "__init__.py"
    return compile_contract(contract_path, single_file=True)


@pytest.fixture(scope="session")
def shared_counter(sandbox, counter_wasm):  # noqa: F811
    """
    Deploy a counter contract that's shared between tests.

    This fixture demonstrates how to create a contract that persists
    across multiple tests with state changes visible to all tests.
    """
    # Create a dedicated account for this contract
    counter_account = sandbox.create_account("counter-shared")

    # Deploy and initialize the contract in one step
    contract = sandbox.deploy(
        wasm_path=counter_wasm, account=counter_account, init_args={"starting_count": 0}
    )

    return contract


@pytest.fixture
def fresh_counter(sandbox, counter_wasm, temp_account):  # noqa: F811
    """
    Deploy a fresh counter contract for each test.

    This fixture demonstrates how to create a clean contract instance
    for each test to ensure test isolation.
    """
    # Deploy and initialize the contract in one step
    contract = sandbox.deploy(
        wasm_path=counter_wasm, account=temp_account, init_args={"starting_count": 0}
    )

    return contract


def test_increment_shared(shared_counter, sandbox_alice):  # noqa: F811
    """Test incrementing the shared counter as Alice."""
    # Get initial count
    initial_count = int(shared_counter.call("get_count").as_view())

    # Increment as Alice
    result = shared_counter.call("increment").as_transaction(sandbox_alice)

    # Assert the result is as expected
    assert int(result) == initial_count + 1

    # Verify state change persisted
    new_count = int(shared_counter.call("get_count").as_view())
    assert new_count == initial_count + 1


def test_decrement_shared(shared_counter, sandbox_bob):  # noqa: F811
    """Test decrementing the shared counter as Bob."""
    # Get initial count (which includes changes from previous tests)
    initial_count = int(shared_counter.call("get_count").as_view())

    # Decrement as Bob
    result = shared_counter.call("decrement").as_transaction(sandbox_bob)

    # Assert the result is as expected
    assert int(result) == initial_count - 1


def test_increment_fresh(fresh_counter, sandbox_alice):  # noqa: F811
    """
    Test incrementing a fresh counter.

    This test demonstrates using a fresh contract instance
    to ensure test isolation.
    """
    # This always starts with count=0 because we use a fresh contract
    result = fresh_counter.call("increment").as_transaction(sandbox_alice)
    assert int(result) == 1

    # Increment again
    result = fresh_counter.call("increment").as_transaction(sandbox_alice)
    assert int(result) == 2


def test_multiple_accounts(fresh_counter, create_account):  # noqa: F811
    """
    Test using multiple dynamically created accounts.

    This test demonstrates creating accounts on demand.
    """
    # Create two random accounts
    user1 = create_account()
    user2 = create_account()

    # User 1 increments
    fresh_counter.call("increment").as_transaction(user1)

    # User 2 increments twice
    fresh_counter.call("increment").as_transaction(user2)
    fresh_counter.call("increment").as_transaction(user2)

    # Check final count
    count = fresh_counter.call("get_count").as_view()
    assert int(count) == 3


def test_reset(fresh_counter, sandbox_bob):  # noqa: F811
    """Test resetting the counter."""
    # Increment a few times
    fresh_counter.call("increment").as_transaction(sandbox_bob)
    fresh_counter.call("increment").as_transaction(sandbox_bob)

    # Reset to 5
    fresh_counter.call("reset", value=5).as_transaction(sandbox_bob)

    # Verify reset worked
    count = fresh_counter.call("get_count").as_view()
    assert int(count) == 5


def test_state_persistence(sandbox, counter_wasm):  # noqa: F811
    """
    Test saving and restoring sandbox state.

    This test demonstrates how to save and restore sandbox state
    for more complex testing scenarios.
    """
    # Create account and deploy contract
    account = sandbox.create_random_account("state-test")
    contract = sandbox.deploy(
        wasm_path=counter_wasm, account=account, init_args={"starting_count": 10}
    )

    # Save initial state
    initial_state = sandbox.save_state()

    # Make some changes
    contract.call("increment").as_transaction(account)
    contract.call("increment").as_transaction(account)

    # Verify count is now 12
    count = contract.call("get_count").as_view()
    assert int(count) == 12

    # Reset to initial state
    sandbox.reset_state(initial_state)

    # Verify count is back to 10
    count = contract.call("get_count").as_view()
    assert int(count) == 10
