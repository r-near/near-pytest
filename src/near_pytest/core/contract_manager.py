# near_pytest/core/contract_manager.py
import os
import subprocess
import hashlib
from pathlib import Path
import importlib.util
import sys
from typing import Union

from ..utils.exceptions import ContractError


class ContractManager:
    """Handles contract compilation and deployment."""

    def __init__(self, sandbox_manager):
        """Initialize with a reference to the SandboxManager."""
        self.sandbox_manager = sandbox_manager
        self._cache_dir = Path.home() / ".near-pytest" / "cache"
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._contract_hashes = {}  # Cache for contract hashes

    def compile_contract(self, contract_path: Union[str, Path]) -> Path:
        """
        Compile a contract and return the path to the WASM file.
        Only recompiles if the source has changed.
        """
        contract_path = Path(contract_path).resolve()

        # Check if it's already a WASM file
        if contract_path.suffix == ".wasm":
            return contract_path

        # Calculate hash of contract source
        contract_hash = self._get_contract_hash(contract_path)

        # Check if we have a cached compiled version
        wasm_filename = f"{contract_path.stem}-{contract_hash}.wasm"
        cached_wasm_path = self._cache_dir / wasm_filename

        if cached_wasm_path.exists():
            print(f"Using cached compiled contract: {cached_wasm_path}")
            return cached_wasm_path

        # We need to compile the contract
        print(f"Compiling contract: {contract_path}")

        # First check if nearc is installed and importable
        try:
            # Try to import nearc
            if importlib.util.find_spec("nearc") is None:
                raise ContractError(
                    "nearc package not found. Please install it with 'pip install nearc'"
                )

            import nearc
            from nearc.builder import compile_contract as nearc_compile

            # Use the imported function directly
            output_path = self._cache_dir / wasm_filename
            assets_dir = Path(nearc.__file__).parent
            venv_path = self._get_venv_path()

            # Use the imported compile_contract function
            success = nearc_compile(
                contract_path, output_path, venv_path, assets_dir, False
            )

            if not success or not output_path.exists():
                raise ContractError(f"Failed to compile contract: {contract_path}")

            return output_path

        except ImportError:
            # Fall back to running nearc as a command
            try:
                output_path = self._cache_dir / wasm_filename
                result = subprocess.run(
                    ["nearc", str(contract_path), "-o", str(output_path)],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )

                if not output_path.exists():
                    raise ContractError(f"Failed to compile contract: {result.stderr}")

                return output_path

            except subprocess.CalledProcessError as e:
                raise ContractError(f"Failed to compile contract: {e.stderr}") from e
            except FileNotFoundError:
                raise ContractError(
                    "nearc command not found. Please install it with 'pip install nearc'"
                )

    def _get_contract_hash(self, contract_path: Path) -> str:
        """
        Calculate a hash of the contract source code and its dependencies.
        This is used to determine if recompilation is needed.
        """
        if contract_path in self._contract_hashes:
            return self._contract_hashes[contract_path]

        # If it's a directory, hash all Python files in it
        if contract_path.is_dir():
            hasher = hashlib.sha256()
            for root, _, files in os.walk(contract_path):
                for file in files:
                    if file.endswith(".py"):
                        file_path = Path(root) / file
                        with open(file_path, "rb") as f:
                            hasher.update(f.read())
            hash_result = hasher.hexdigest()[:16]
        else:
            # It's a single file
            with open(contract_path, "rb") as f:
                hash_result = hashlib.sha256(f.read()).hexdigest()[:16]

        self._contract_hashes[contract_path] = hash_result
        return hash_result

    def _get_venv_path(self) -> Path:
        """Get the path to the virtual environment."""
        # Try to detect the virtual environment
        if hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        ):
            # We're in a virtual environment
            return Path(sys.prefix)

        # Check common venv paths relative to CWD
        for venv_name in [".venv", "venv", ".env", "env"]:
            venv_path = Path.cwd() / venv_name
            if venv_path.exists() and (venv_path / "bin").exists():
                return venv_path

        # Default to the current Python executable's parent
        return Path(sys.executable).parent.parent
