import sys

from PyQt6.QtWidgets import QApplication

from gamenet.client_agent.ui import ClientWindow
from gamenet.client_agent.config import ClientConfig


def main() -> int:
    application = QApplication(sys.argv)
    config = ClientConfig.from_environment()
    window = ClientWindow(config.server_url, config.pc_id, config.device_token)
    window.showFullScreen()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())