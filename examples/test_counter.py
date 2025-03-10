# examples/test_counter.py
from near_pytest import NearTestCase
from pathlib import Path


class TestCounter(NearTestCase):
    @classmethod
    def setup_class(cls):
        """Set up test class with all accounts and contracts."""
        # Call parent setup method
        super().setup_class()

        # Compile the contract
        current_dir = Path(__file__).parent
        contract_path = current_dir / "counter_contract" / "__init__.py"
        wasm_path = cls.compile_contract(contract_path)

        # Create account for contract
        cls.create_account("counter")

        # Deploy contract
        cls.counter_contract = cls.deploy_contract(
            cls.counter, wasm_path, init_args={"starting_count": 0}
        )

        # Create user accounts
        cls.create_account("alice")
        cls.create_account("bob")

        # Explicitly save state for later reset
        cls.save_state()

    def setup_method(self):
        """Set up for each test method."""
        # Reset the state to what it was after setup_class
        self.reset_state()

    def test_increment(self):
        # Call contract method
        result = self.counter_contract.call("increment", {})
        assert int(result) == 1

        # Call again to verify state persistence within a test
        result = self.counter_contract.call("increment", {})
        assert int(result) == 2

    def test_increment_as_alice(self):
        # Each test starts with fresh state because of reset_state() in setup_method
        result = self.counter_contract.call_as(self.alice, "increment", {})
        assert int(result) == 1

    def test_get_count(self):
        # Call view method
        result = self.counter_contract.view("get_count", {})
        assert int(result) == 0

        # Call increment then view again
        self.counter_contract.call("increment", {})
        result = self.counter_contract.view("get_count", {})
        assert int(result) == 1
