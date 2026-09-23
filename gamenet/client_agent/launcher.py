import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LaunchAuthorization:
    authorized: bool
    launch_type: str
    executable_path: str | None
    working_directory: str | None
    launch_arguments: str | None
    process_names: list[str]


class GameLauncher:
    def launch(self, authorization: LaunchAuthorization) -> subprocess.Popen:
        if not authorization.authorized:
            raise PermissionError("Server did not authorize game launch")
        if authorization.launch_type != "DIRECT_EXE":
            raise NotImplementedError(f"Launcher adapter not implemented: {authorization.launch_type}")
        if not authorization.executable_path:
            raise FileNotFoundError("Game executable path is missing")
        executable = Path(authorization.executable_path)
        if not executable.exists():
            raise FileNotFoundError(str(executable))
        arguments = shlex.split(authorization.launch_arguments or "", posix=False)
        return subprocess.Popen(
            [str(executable), *arguments],
            cwd=authorization.working_directory or str(executable.parent),
            shell=False,
        )


class GameProcessMonitor:
    @staticmethod
    def is_running(process: subprocess.Popen) -> bool:
        return process.poll() is None

    @staticmethod
    def wait_for_exit(process: subprocess.Popen) -> int:
        return process.wait()