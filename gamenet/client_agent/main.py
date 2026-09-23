import sys

from PyQt6.QtWidgets import QApplication

from gamenet.client_agent.ui import ClientWindow


def main() -> int:
    application = QApplication(sys.argv)
    window = ClientWindow("http://127.0.0.1:8765", "PC-01", "")
    window.showFullScreen()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())