# near_pytest/sandbox.py
import os
import atexit
import signal
import subprocess
import time
import requests
import json
from pathlib import Path
import tempfile
import shutil
import socket

# Import logger
from .utils import logger


class SandboxError(Exception):
    """Error related to sandbox operations"""

    pass


class SandboxManager:
    """Manages the NEAR sandbox process"""

    _instance = None

    @classmethod
    def get_instance(cls, home_dir=None, port=None):
        """Get or create the singleton instance"""
        if cls._instance is None:
            cls._instance = SandboxManager(home_dir, port)
        return cls._instance

    def __init__(self, home_dir=None, port=None):
        """Initialize the sandbox manager"""
        # Generate unique port if not specified
        self._port = port or self._get_available_port()
        # Generate unique home directory if not specified
        self._home_dir = (
            Path(home_dir)
            if home_dir
            else Path(tempfile.mkdtemp(prefix=f"near_sandbox_{self._port}_"))
        )
        self._process = None
        self._binary_path = None

        # Register cleanup
        atexit.register(self.stop)

    def _get_available_port(self):
        # Find an available port dynamically
        with socket.socket() as s:
            s.bind(("", 0))
            return s.getsockname()[1]

    def start(self):
        """Start the sandbox process"""
        if self.is_running():
            logger.debug("Sandbox already running")
            return

        # Ensure binary is available
        from .utils.binary import ensure_sandbox_binary

        self._binary_path = ensure_sandbox_binary()

        # Create home directory
        self._home_dir.mkdir(parents=True, exist_ok=True)

        # Initialize if needed
        validator_key_path = self._home_dir / "validator_key.json"
        if not validator_key_path.exists():
            logger.info("Initializing sandbox...")
            self._run_command(["init", "--chain-id", "localnet"])

        # Start the sandbox
        logger.info(f"Starting sandbox on port {self._port}...")
        self._process = subprocess.Popen(
            [
                self._binary_path,
                "--home",
                str(self._home_dir),
                "run",
                "--rpc-addr",
                f"0.0.0.0:{self._port}",
                "--network-addr",
                f"0.0.0.0:{self._get_available_port()}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid,
        )

        # Wait for sandbox to start
        self._wait_for_start()

    def stop(self):
        """Stop the sandbox process"""
        if self._process is not None:
            logger.info("Stopping sandbox...")
            try:
                os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)
                self._process.wait(timeout=5)
                logger.success("Sandbox stopped")
            except (subprocess.TimeoutExpired, ProcessLookupError):
                logger.warning("Sandbox didn't stop gracefully, forcing shutdown...")
                try:
                    os.killpg(os.getpgid(self._process.pid), signal.SIGKILL)
                except ProcessLookupError:
                    pass

            self._process = None

    def dump_state(self) -> list:
        """Dump the current state"""
        logger.info("Dumping sandbox state...")
        self._run_command(["view-state", "dump-state"])
        state_file = self._home_dir / "output.json"
        with open(state_file, "r") as f:
            state = json.load(f)["records"]
            logger.debug(f"Dumped {len(state)} state records")
            return state

    def reset_state(self):
        """Reset to genesis state by restarting"""
        logger.info("Resetting sandbox to genesis state...")
        self.stop()

        # Clean up data directory
        data_dir = self._home_dir / "data"
        if data_dir.exists():
            shutil.rmtree(data_dir)

        # Restart
        self.start()
        logger.success("Sandbox reset to genesis state")

    def rpc_endpoint(self) -> str:
        """Get the RPC endpoint URL"""
        return f"http://localhost:{self._port}"

    def is_running(self) -> bool:
        """Check if sandbox is running"""
        if self._process is None:
            return False

        # Check if process is still running
        if self._process.poll() is not None:
            self._process = None
            return False

        # Try connecting to RPC
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

    def get_validator_key(self) -> str:
        """Get the validator key"""
        key_path = self._home_dir / "validator_key.json"
        if not key_path.exists():
            raise SandboxError("Validator key not found")

        with open(key_path, "r") as f:
            key_data = json.load(f)
            if "secret_key" in key_data:
                return key_data["secret_key"]
            else:
                raise SandboxError("Invalid validator key format")

    def _run_command(self, args: list):
        """Run a sandbox command"""
        cmd = [self._binary_path, "--home", str(self._home_dir)] + args
        logger.debug(f"Running command: {' '.join(str(x) for x in cmd)}")
        try:
            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
            )
            logger.debug(f"Command output: {result.stdout.decode()[:200]}...")
            return result
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode()
            logger.error(f"Sandbox command failed: {error_msg}")
            raise SandboxError(f"Sandbox command failed: {error_msg}")

    def _wait_for_start(self, timeout=30, interval=0.5):
        """Wait for sandbox to start"""
        logger.info(f"Waiting for sandbox to start (timeout: {timeout}s)...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_running():
                logger.success("Sandbox started successfully")
                return
            time.sleep(interval)

        self.stop()
        raise SandboxError(f"Sandbox failed to start within {timeout} seconds")
