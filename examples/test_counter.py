# examples/test_counter.py
from near_pytest import NearTestCase
from pathlib import Path


class TestCounter(NearTestCase):
    @classmethod
    def setup_class(cls):
        # Call the parent setup method
        super().setup_class()

        # Compile the contract once for all tests
        current_dir = Path(__file__).parent
        contract_path = current_dir / "counter_contract" / "__init__.py"
        cls.counter_wasm = cls.compile_contract(contract_path)

    def setup_method(self):
        # Reset sandbox state before each test
        self.reset_sandbox()

        # Create account for contract
        self.contract_account = self.create_account("counter")

        # Deploy contract
        self.counter = self.deploy_contract(
            self.contract_account, self.counter_wasm, init_args={"starting_count": 0}
        )

        # Create user accounts
        self.alice = self.create_account("alice")
        self.bob = self.create_account("bob")

    def test_increment(self):
        # Call contract method
        result = self.counter.call("increment", {})
        assert result == 1

        # Call again to verify state persistence within a test
        result = self.counter.call("increment", {})
        assert result == 2

    def test_increment_as_alice(self):
        # Each test starts with fresh state
        result = self.counter.call_as(self.alice, "increment", {})
        assert result == 1

    def test_get_count(self):
        # Call view method
        result = self.counter.view("get_count", {})
        assert result == 0

        # Call increment then view again
        self.counter.call("increment", {})
        result = self.counter.view("get_count", {})
        assert result == 1
