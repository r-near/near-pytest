# near_pytest/core/sandbox_manager.py
import os
import atexit
import signal
import subprocess
import time
import requests
from pathlib import Path
import tempfile
import shutil
from ..utils.binary import ensure_sandbox_binary
from ..utils.exceptions import SandboxError


class SandboxManager:
    """Singleton manager for the NEAR sandbox process."""

    _instance = None

    @classmethod
    def get_instance(cls, home_dir=None, port=None):
        """Get or create the singleton instance with optional configuration."""
        if cls._instance is None:
            cls._instance = SandboxManager(home_dir, port)
        return cls._instance

    def __init__(self, home_dir=None, port=None):
        """Initialize the sandbox manager with optional configuration."""
        if home_dir is None:
            self._temp_dir = tempfile.mkdtemp(prefix="near_sandbox_")
            self._home_dir = Path(self._temp_dir)
        else:
            self._temp_dir = None
            self._home_dir = Path(home_dir)

        self._port = 3030 if port is None else port
        self._process = None
        self._binary_path = None

        # Register cleanup handler
        atexit.register(self.stop)

    def __del__(self):
        """Ensure the sandbox is stopped when the object is deleted."""
        self.stop()

    def start(self):
        """Start the sandbox process if not already running."""
        if self.is_running():
            return

        # Ensure sandbox binary is available
        self._binary_path = ensure_sandbox_binary()

        # Create home directory if it doesn't exist
        self._home_dir.mkdir(parents=True, exist_ok=True)

        # Initialize the sandbox if needed
        validator_key_path = self._home_dir / "validator_key.json"
        if not validator_key_path.exists():
            print("Initializing sandbox...")
            self._run_command(["init", "--chain-id", "localnet"])

        # Start the sandbox
        print(f"Starting sandbox on port {self._port}...")
        self._process = subprocess.Popen(
            [
                self._binary_path,
                "--home",
                str(self._home_dir),
                "run",
                "--rpc-addr",
                f"0.0.0.0:{self._port}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid,
        )

        # Wait for sandbox to start
        self._wait_for_start()

    def stop(self):
        """Stop the sandbox process and clean up."""
        if self._process is not None:
            try:
                os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)
                self._process.wait(timeout=5)
            except (subprocess.TimeoutExpired, ProcessLookupError):
                # Force kill if graceful shutdown fails
                try:
                    os.killpg(os.getpgid(self._process.pid), signal.SIGKILL)
                except ProcessLookupError:
                    pass

            self._process = None

        # Clean up temporary directory if we created one
        if self._temp_dir is not None and os.path.exists(self._temp_dir):
            shutil.rmtree(self._temp_dir, ignore_errors=True)

    def reset_state(self):
        """Reset the sandbox state to genesis."""
        # Stop the sandbox
        self.stop()

        # Clean up the data directory
        data_dir = self._home_dir / "data"
        if data_dir.exists():
            shutil.rmtree(data_dir)

        # Restart the sandbox
        self.start()

    def rpc_endpoint(self):
        """Get the RPC endpoint URL."""
        return f"http://localhost:{self._port}"

    def is_running(self):
        """Check if the sandbox is running."""
        if self._process is None:
            return False

        # Check if process is still running
        if self._process.poll() is not None:
            self._process = None
            return False

        # Try to connect to the RPC endpoint
        try:
            response = requests.post(
                self.rpc_endpoint(),
                json={
                    "jsonrpc": "2.0",
                    "id": "status",
                    "method": "status",
                    "params": [],
                },
                timeout=1,
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def get_validator_key(self):
        """Get the validator key from the sandbox."""
        validator_key_path = self._home_dir / "validator_key.json"
        if not validator_key_path.exists():
            raise SandboxError(
                "Validator key not found. Make sure the sandbox is initialized."
            )

        import json

        with open(validator_key_path, "r") as f:
            key_data = json.load(f)
            if "secret_key" in key_data:
                return key_data["secret_key"]
            else:
                raise SandboxError("Invalid validator key format")

    def _run_command(self, args):
        """Run a sandbox command."""
        if self._binary_path is None:
            self._binary_path = ensure_sandbox_binary()

        cmd = [self._binary_path, "--home", str(self._home_dir)] + args
        try:
            subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
            )
        except subprocess.CalledProcessError as e:
            raise SandboxError(f"Sandbox command failed: {e.stderr.decode()}") from e

    def _wait_for_start(self, timeout=30, interval=0.5):
        """Wait for the sandbox to start accepting requests."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_running():
                return
            time.sleep(interval)

        # If we get here, the sandbox didn't start in time
        self.stop()
        raise SandboxError(f"Sandbox failed to start within {timeout} seconds")
