import sys
from pathlib import Path

import pytest

from gamenet.client_agent.launcher import GameLauncher, LaunchAuthorization


def test_launcher_requires_server_authorization():
    authorization = LaunchAuthorization(False, "DIRECT_EXE", sys.executable, None, None, [])

    with pytest.raises(PermissionError):
        GameLauncher().launch(authorization)


def test_direct_launcher_uses_no_shell_and_monitor(tmp_path: Path):
    authorization = LaunchAuthorization(True, "DIRECT_EXE", sys.executable, str(tmp_path), "-c pass", ["python"])

    process = GameLauncher().launch(authorization)
    assert process.args[0] == sys.executable
    process.wait(timeout=2)