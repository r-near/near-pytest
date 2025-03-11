# near_pytest/compiler.py
import os
import hashlib
import importlib.util
import subprocess
from pathlib import Path

# Import logger
from .utils import logger


class CompilerError(Exception):
    """Error related to contract compilation"""

    pass


def compile_contract(contract_path, single_file=False):
    """Compile a NEAR smart contract"""
    contract_path = Path(contract_path).resolve()

    # Check if it's already a WASM file
    if contract_path.suffix == ".wasm":
        logger.info(f"File is already compiled WASM: {contract_path}")
        return contract_path

    # Create cache directory
    cache_dir = Path.home() / ".near-pytest" / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Calculate hash of source
    contract_hash = _get_contract_hash(contract_path)
    logger.debug(f"Contract hash: {contract_hash}")

    # Check for cached version
    wasm_filename = f"{contract_path.stem}-{contract_hash}.wasm"
    cached_wasm_path = cache_dir / wasm_filename

    if cached_wasm_path.exists():
        logger.success(f"Using cached compiled contract: {cached_wasm_path}")
        return cached_wasm_path

    # We need to compile
    logger.info(f"Compiling contract: {contract_path}")

    try:
        # Try to import nearc
        if importlib.util.find_spec("nearc") is not None:
            import nearc
            from nearc.builder import compile_contract as nearc_compile

            output_path = cache_dir / wasm_filename
            assets_dir = Path(nearc.__file__).parent
            venv_path = _get_venv_path()

            logger.debug("Using nearc Python module for compilation")
            logger.debug(f"Output path: {output_path}")
            logger.debug(f"Assets directory: {assets_dir}")
            logger.debug(f"Virtual environment path: {venv_path}")

            success = nearc_compile(
                contract_path=contract_path,
                output_path=output_path,
                venv_path=venv_path,
                assets_dir=assets_dir,
                rebuild=False,
                single_file=single_file,
            )

            if not success or not output_path.exists():
                logger.error(f"Failed to compile contract: {contract_path}")
                raise CompilerError(f"Failed to compile contract: {contract_path}")

            logger.success(f"Contract compiled to: {output_path}")
            return output_path
        else:
            # Fall back to command
            logger.debug("nearc Python module not found, falling back to command line")
            output_path = cache_dir / wasm_filename

            logger.info(
                f"Compiling with command: nearc {contract_path} -o {output_path}"
            )
            result = subprocess.run(
                ["uvx", "nearc", str(contract_path), "-o", str(output_path)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            if not output_path.exists():
                stderr = result.stderr.strip()
                logger.error(f"Failed to compile contract: {stderr}")
                raise CompilerError(f"Failed to compile contract: {stderr}")

            logger.success(f"Contract compiled to: {output_path}")
            return output_path

    except Exception as e:
        logger.error(f"Compilation error: {str(e)}")
        raise CompilerError(f"Failed to compile contract: {str(e)}")


def _get_contract_hash(contract_path):
    """Calculate hash of contract source"""
    # If it's a directory, hash all Python files
    if contract_path.is_dir():
        logger.debug(f"Calculating hash for directory: {contract_path}")
        hasher = hashlib.sha256()
        for root, _, files in os.walk(contract_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    logger.debug(f"Including file in hash: {file_path}")
                    with open(file_path, "rb") as f:
                        hasher.update(f.read())
        return hasher.hexdigest()[:16]
    else:
        # It's a single file
        logger.debug(f"Calculating hash for file: {contract_path}")
        with open(contract_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:16]


def _get_venv_path():
    """Get virtual environment path"""
    import sys

    # Try to detect the virtual environment
    if hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        # We're in a virtual environment
        logger.debug(f"Detected virtual environment: {sys.prefix}")
        return Path(sys.prefix)

    # Check common venv paths
    for venv_name in [".venv", "venv", ".env", "env"]:
        venv_path = Path.cwd() / venv_name
        if venv_path.exists() and (venv_path / "bin").exists():
            logger.debug(f"Found virtual environment: {venv_path}")
            return venv_path

    # Default to current Python executable's parent
    logger.debug(
        f"Using Python executable parent as venv path: {Path(sys.executable).parent.parent}"
    )
    return Path(sys.executable).parent.parent
