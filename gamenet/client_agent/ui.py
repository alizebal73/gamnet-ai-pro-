from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QFormLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gamenet.client_agent.agent import AgentConfig, ClientAgent
from gamenet.client_agent.customer_client import CustomerApiClient


class ClientWindow(QMainWindow):
    def __init__(self, base_url: str, pc_id: str, device_token: str) -> None:
        super().__init__()
        self.api = CustomerApiClient(base_url, pc_id, device_token)
        self.agent = ClientAgent(AgentConfig(base_url, pc_id, device_token, "2.4.1"))
        self.setWindowTitle("GameNet Pro Client")
        self.resize(620, 520)
        self._build_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._heartbeat)
        self.timer.start(1000)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        form = QFormLayout()
        self.customer_number = QLineEdit()
        self.pin = QLineEdit()
        self.pin.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_button = QPushButton("Login to Play")
        self.login_button.clicked.connect(self.login)
        form.addRow("Customer ID", self.customer_number)
        form.addRow("PIN", self.pin)
        form.addRow(self.login_button)
        layout.addLayout(form)
        self.profile_label = QLabel("Not logged in")
        self.connection_label = QLabel("Server: checking")
        self.games = QListWidget()
        layout.addWidget(self.profile_label)
        layout.addWidget(self.connection_label)
        layout.addWidget(QLabel("Games"))
        layout.addWidget(self.games)

    def login(self) -> None:
        try:
            profile = self.api.login(int(self.customer_number.text()), self.pin.text())
            self.agent.set_session(profile.get("active_session_id"))
            self.profile_label.setText(
                f"{profile['name']} | Credit: {profile['gaming_credit_seconds']} seconds | "
                f"Session: {profile.get('active_session_status') or 'NONE'}"
            )
            self.games.clear()
            for game in self.api.games():
                self.games.addItem(f"{game['name']} ({game['launch_type']})")
        except Exception as error:
            QMessageBox.critical(self, "Login failed", str(error))

    def _heartbeat(self) -> None:
        response = self.agent.heartbeat()
        status = response.get("session_status") or self.agent.state
        self.connection_label.setText(f"Server: {self.agent.state} | Session: {status}")

    def closeEvent(self, event) -> None:
        self.agent.close()
        self.api.close()
        event.accept()