# near_pytest/utils/binary.py
import os
import platform
import shutil
import urllib.request
import tarfile
from pathlib import Path
import tempfile
from .exceptions import BinaryError

# Default sandbox version
DEFAULT_VERSION = "2.4.0"


def get_platform_id():
    """Get the platform identifier for downloading the right binary."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "darwin":
        system = "darwin"  # macOS
    elif system == "windows":
        system = "windows"
    elif system == "linux":
        system = "linux"
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
    return binary_dir


def get_binary_url(version=DEFAULT_VERSION):
    """Get the URL for downloading the sandbox binary."""
    system, arch = get_platform_id()
    base_url = "https://s3-us-west-1.amazonaws.com/build.nearprotocol.com/nearcore"
    return f"{base_url}/{system}-{arch}/{version}/near-sandbox.tar.gz"


def download_binary(version=DEFAULT_VERSION):
    """Download the sandbox binary for the current platform."""
    binary_dir = get_binary_dir()
    system, arch = get_platform_id()
    binary_name = "near-sandbox"
    if system == "windows":
        binary_name += ".exe"

    binary_path = binary_dir / f"{binary_name}-{version}"

    # Skip if already exists
    if binary_path.exists():
        return binary_path

    # Download the binary
    url = get_binary_url(version)
    print(f"Downloading NEAR sandbox binary from {url}")

    with tempfile.TemporaryDirectory() as temp_dir:
        tar_path = Path(temp_dir) / "near-sandbox.tar.gz"

        try:
            # Download the tar.gz file
            urllib.request.urlretrieve(url, tar_path)

            # Extract the binary
            with tarfile.open(tar_path) as tar:
                tar.extractall(path=temp_dir)

            # Find the extracted binary
            extracted_binary = None
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if file.startswith("near-sandbox"):
                        extracted_binary = Path(root) / file
                        break
                if extracted_binary:
                    break

            if not extracted_binary:
                raise BinaryError(
                    "Could not find near-sandbox binary in the downloaded archive"
                )

            # Make it executable
            os.chmod(extracted_binary, 0o755)

            # Move to final location
            shutil.copy2(extracted_binary, binary_path)
            os.chmod(binary_path, 0o755)

            return binary_path

        except Exception as e:
            # Clean up partial download
            if binary_path.exists():
                binary_path.unlink()
            raise BinaryError(f"Failed to download sandbox binary: {str(e)}") from e


def ensure_sandbox_binary(version=DEFAULT_VERSION):
    """Ensure the sandbox binary is available and return its path."""
    # First check if it's in PATH
    binary_name = "near-sandbox"
    if platform.system().lower() == "windows":
        binary_name += ".exe"

    # Check if it's in PATH
    path_binary = shutil.which(binary_name)
    if path_binary:
        return path_binary

    # Otherwise download it
    return download_binary(version)
