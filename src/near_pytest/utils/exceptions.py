# near_pytest/utils/exceptions.py


class NearPytestError(Exception):
    """Base exception for all near-pytest errors."""

    pass


class SandboxError(NearPytestError):
    """Error related to sandbox operations."""

    pass


class BinaryError(NearPytestError):
    """Error related to binary download or execution."""

    pass


class ContractError(NearPytestError):
    """Error related to contract compilation or deployment."""

    pass


class AccountError(NearPytestError):
    """Error related to account operations."""

    pass


class TransactionError(NearPytestError):
    """Error related to transaction execution."""

    pass
