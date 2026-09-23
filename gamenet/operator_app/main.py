import sys

from PyQt6.QtWidgets import QApplication

from gamenet.operator_app.api_client import OperatorApiClient
from gamenet.operator_app.ui import OperatorWindow


def main() -> int:
    application = QApplication(sys.argv)
    client = OperatorApiClient("http://127.0.0.1:8765")
    window = OperatorWindow(client)
    window.show()
    exit_code = application.exec()
    client.close()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())