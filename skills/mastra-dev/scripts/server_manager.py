"""Server manager for Mastra development server and Studio."""

from pathlib import Path
import subprocess
import signal
import time
import sys
import os


class ServerManager:
    """Manager for Mastra server and Studio operations."""

    def __init__(self, mastra_app: Path):
        """Initialize server manager.

        Args:
            mastra_app: Path to Mastra app directory
        """
        self.mastra_app = Path(mastra_app)
        self.monorepo_root = self.mastra_app.parent.parent
        self.logs_dir = self.mastra_app / 'logs'

    def start(self) -> None:
        """Start the Mastra development server.

        Raises:
            RuntimeError: If server fails to start
        """
        print("\n🚀 Starting Mastra server...")
        print(f"   Directory: {self.mastra_app}")
        print()

        # Check if already running
        if self._is_running():
            print("⚠️  Mastra server is already running!")
            print("   Use 'mastra-dev server status' to check status")
            print("   Use 'mastra-dev server stop' to stop the server")
            return

        try:
            # Start server using npm run dev:mastra from monorepo root
            print("   Starting server with: npm run dev:mastra")
            print("   Press Ctrl+C to stop the server")
            print()

            subprocess.run(
                ['npm', 'run', 'dev:mastra'],
                cwd=self.monorepo_root,
                check=True
            )

        except subprocess.CalledProcessError as e:
            print(f"\n❌ Failed to start Mastra server: {e}", file=sys.stderr)
            sys.exit(2)
        except KeyboardInterrupt:
            print("\n\n⏹️  Server stopped by user")

    def stop(self) -> None:
        """Stop the Mastra development server."""
        print("\n⏹️  Stopping Mastra server...")
        print()

        pid = self._get_pid()

        if not pid:
            print("ℹ️  Mastra server is not running")
            return

        try:
            # Send SIGTERM
            os.kill(pid, signal.SIGTERM)
            print(f"   Sent SIGTERM to process {pid}")

            # Wait for graceful shutdown
            for _ in range(10):
                time.sleep(0.5)
                if not self._is_running():
                    print("✅ Server stopped successfully")
                    return

            # Force kill if still running
            print("   Server did not stop gracefully, forcing...")
            os.kill(pid, signal.SIGKILL)
            print("✅ Server stopped (forced)")

        except ProcessLookupError:
            print("ℹ️  Server process already terminated")
        except PermissionError:
            print("❌ Permission denied. Try running with sudo.", file=sys.stderr)
            sys.exit(1)

    def status(self) -> None:
        """Check Mastra server status."""
        print("\n📊 Mastra Server Status")
        print("=" * 60)

        pid = self._get_pid()

        if not pid:
            print("Status: ⭕ NOT RUNNING")
            print()
            print("To start the server: mastra-dev server start")
            return

        print(f"Status: ✅ RUNNING")
        print(f"PID: {pid}")

        # Get process info
        try:
            result = subprocess.run(
                ['ps', '-p', str(pid), '-o', 'pid,ppid,%cpu,%mem,etime,cmd'],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                print()
                print("Process Info:")
                print(result.stdout)

        except Exception:
            pass

        print()
        print("To stop the server: mastra-dev server stop")
        print("To view logs: mastra-dev server logs")

    def logs(self, lines: int = 50, follow: bool = False) -> None:
        """View Mastra server logs.

        Args:
            lines: Number of log lines to display
            follow: Whether to follow log output
        """
        print(f"\n📋 Mastra Server Logs (last {lines} lines)")
        print("=" * 60)
        print()

        log_file = self.logs_dir / 'mastra.log'

        if not log_file.exists():
            print("ℹ️  No log file found")
            print(f"   Expected location: {log_file}")
            print()
            print("   The server may not have been started yet,")
            print("   or logs may be written to a different location.")
            return

        try:
            if follow:
                # Tail -f equivalent
                subprocess.run(['tail', '-f', '-n', str(lines), str(log_file)])
            else:
                # Tail -n equivalent
                result = subprocess.run(
                    ['tail', '-n', str(lines), str(log_file)],
                    capture_output=True,
                    text=True
                )
                print(result.stdout)

        except KeyboardInterrupt:
            print("\n\n⏹️  Stopped following logs")
        except Exception as e:
            print(f"❌ Failed to read logs: {e}", file=sys.stderr)

    def start_studio(self, port: int = 4111) -> None:
        """Start Mastra Studio.

        Args:
            port: Studio port (default: 4111)

        Raises:
            RuntimeError: If Studio fails to start
        """
        print("\n🎨 Starting Mastra Studio...")
        print(f"   Port: {port}")
        print()

        # Check if Mastra server is running
        if not self._is_running():
            print("⚠️  Mastra server is not running!")
            print("   Studio requires the Mastra server on port 3000")
            print()
            response = input("   Start Mastra server first? (Y/n): ")
            if response.lower() != 'n':
                print()
                self.start()
                return

        try:
            print("   Starting Studio with: npm run dev:studio")
            print("   Press Ctrl+C to stop Studio")
            print()
            print(f"   Studio will be available at: http://localhost:{port}")
            print()

            subprocess.run(
                ['npm', 'run', 'dev:studio'],
                cwd=self.monorepo_root,
                check=True
            )

        except subprocess.CalledProcessError as e:
            print(f"\n❌ Failed to start Mastra Studio: {e}", file=sys.stderr)
            sys.exit(2)
        except KeyboardInterrupt:
            print("\n\n⏹️  Studio stopped by user")

    def _is_running(self) -> bool:
        """Check if Mastra server is running.

        Returns:
            True if server is running, False otherwise
        """
        return self._get_pid() is not None

    def _get_pid(self) -> int | None:
        """Get PID of running Mastra server.

        Returns:
            PID if found, None otherwise
        """
        try:
            # Search for node process running mastra
            result = subprocess.run(
                ['pgrep', '-f', 'node.*mastra'],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0 and result.stdout.strip():
                # Return first PID
                return int(result.stdout.strip().split('\n')[0])

            return None

        except Exception:
            return None
