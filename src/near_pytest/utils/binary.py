import os
import platform
import shutil
import requests
import tarfile
from pathlib import Path
import tempfile

# Import logger
from ..utils import logger

# Default sandbox version
DEFAULT_VERSION = "2.4.0"


class BinaryError(Exception):
    pass


def get_platform_id():
    """Get the platform identifier for downloading the right binary."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "darwin":
        system = "Darwin"
    elif system == "linux":
        system = "Linux"
    else:
        raise BinaryError(f"Unsupported platform: {system}")

    if machine in ["x86_64", "amd64"]:
        arch = "x86_64"
    elif machine in ["arm64", "aarch64"]:
        arch = "arm64"
    else:
        raise BinaryError(f"Unsupported architecture: {machine}")

    return system, arch


def get_binary_dir():
    """Get the directory where binaries are stored."""
    # Use ~/.near-pytest directory
    home_dir = Path.home()
    binary_dir = home_dir / ".near-pytest" / "bin"
    binary_dir.mkdir(parents=True, exist_ok=True)
    return binary_dir.absolute()


def get_binary_url(version=DEFAULT_VERSION):
    """Get the URL for downloading the sandbox binary."""
    system, arch = get_platform_id()
    base_url = "https://s3-us-west-1.amazonaws.com/build.nearprotocol.com/nearcore"
    return f"{base_url}/{system}-{arch}/{version}/near-sandbox.tar.gz"


def download_binary(version=DEFAULT_VERSION):
    """Download the sandbox binary for the current platform."""
    logger.info("Downloading NEAR sandbox binary")
    binary_dir = get_binary_dir()
    system, arch = get_platform_id()
    binary_name = "near-sandbox"
    if system == "windows":
        binary_name += ".exe"

    binary_path = binary_dir / f"{binary_name}-{version}"
    logger.debug(f"Target binary path: {binary_path}")

    # Skip if already exists
    if binary_path.exists():
        logger.info("Binary already exists, skipping download")
        return binary_path

    # Download the binary
    url = get_binary_url(version)
    logger.info(f"Downloading from {url}")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        tar_path = temp_path / "near-sandbox.tar.gz"

        try:
            # Download the tar.gz file with requests
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise an exception for HTTP errors

            with open(tar_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.debug(f"Download completed to {tar_path}")

            # Extract directly to the binary directory with strip=1 (similar to tar.x({ strip: 1 }) in TS)
            # This removes the top-level directory (Linux-x86_64) during extraction
            with tarfile.open(tar_path, mode="r:gz") as tar:
                # Get all members
                members = tar.getmembers()
                logger.debug(f"Archive members: {[m.name for m in members]}")

                # Strip the first directory component for each member
                for member in members:
                    parts = member.name.split("/", 1)
                    if len(parts) > 1:
                        member.name = parts[1]

                # Extract only the binary file, not directories
                binary_members = [m for m in members if m.name == binary_name]
                if not binary_members:
                    raise BinaryError(f"Binary '{binary_name}' not found in archive")

                # Extract directly to the binary path with the versioned name
                for member in binary_members:
                    with tar.extractfile(member) as source:
                        with open(binary_path, "wb") as target:
                            target.write(source.read())

            # Make it executable
            os.chmod(binary_path, 0o755)
            logger.success(f"Binary installed to {binary_path}")

            return binary_path

        except Exception as e:
            # Clean up partial download
            if binary_path.exists():
                binary_path.unlink()
            raise BinaryError(f"Failed to download sandbox binary: {str(e)}") from e


def ensure_sandbox_binary(version=DEFAULT_VERSION):
    """Ensure the sandbox binary is available and return its path."""
    logger.debug("Ensuring sandbox binary...")
    binary_name = "near-sandbox"
    if platform.system().lower() == "windows":
        binary_name += ".exe"

    # Check if it's in PATH
    path_binary = shutil.which(binary_name)
    if path_binary:
        logger.info(f"Found sandbox binary in PATH: {path_binary}")
        return path_binary

    # Otherwise download it
    return download_binary(version)
