from uuid import uuid4

from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from gamenet.operator_app.api_client import OperatorApiClient


class OperatorWindow(QMainWindow):
    def __init__(self, api_client: OperatorApiClient) -> None:
        super().__init__()
        self.api_client = api_client
        self.selected_customer: dict | None = None
        self.setWindowTitle("GameNet Pro Operator")
        self.resize(760, 520)
        self._build_ui()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        login_box = QGroupBox("Operator Login")
        login_form = QFormLayout(login_box)
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        login_form.addRow("Username", self.username_input)
        login_form.addRow("Password", self.password_input)
        login_form.addRow(self.login_button)
        layout.addWidget(login_box)

        sale_box = QGroupBox("Quick Sale")
        sale_grid = QGridLayout(sale_box)
        self.customer_search = QLineEdit()
        self.customer_search.setPlaceholderText("Customer number, name or mobile")
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_customer)
        self.customer_label = QLabel("No customer selected")
        self.duration_combo = QComboBox()
        self.duration_combo.addItem("15 minutes", 900)
        self.duration_combo.addItem("30 minutes", 1800)
        self.duration_combo.addItem("1 hour", 3600)
        self.duration_combo.addItem("2 hours", 7200)
        self.quote_button = QPushButton("Get Price")
        self.quote_button.clicked.connect(self.quote)
        self.price_label = QLabel("Price: -")
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["CASH", "CARD", "BALANCE", "MIXED"])
        self.sell_button = QPushButton("Create Sale")
        self.sell_button.clicked.connect(self.create_sale)
        self.status_label = QLabel("Login required")
        sale_grid.addWidget(self.customer_search, 0, 0, 1, 2)
        sale_grid.addWidget(self.search_button, 0, 2)
        sale_grid.addWidget(self.customer_label, 1, 0, 1, 3)
        sale_grid.addWidget(QLabel("Duration"), 2, 0)
        sale_grid.addWidget(self.duration_combo, 2, 1)
        sale_grid.addWidget(self.quote_button, 2, 2)
        sale_grid.addWidget(self.price_label, 3, 0, 1, 2)
        sale_grid.addWidget(self.payment_combo, 4, 0)
        sale_grid.addWidget(self.sell_button, 4, 1)
        sale_grid.addWidget(self.status_label, 5, 0, 1, 3)
        layout.addWidget(sale_box)

    def login(self) -> None:
        try:
            user = self.api_client.login(self.username_input.text(), self.password_input.text())
            self.status_label.setText(f"Logged in as {user.get('display_name') or user['username']}")
        except Exception as error:
            self._show_error("Login failed", error)

    def search_customer(self) -> None:
        try:
            customers = self.api_client.search_customers(self.customer_search.text().strip())
            self.selected_customer = customers[0] if customers else None
            self.customer_label.setText(
                f"Selected: {self.selected_customer['name']} ({self.selected_customer['customer_number']})"
                if self.selected_customer else "Customer not found"
            )
        except Exception as error:
            self._show_error("Customer search failed", error)

    def quote(self) -> None:
        try:
            quote = self.api_client.quote("GAMING", self.duration_combo.currentData())
            self.price_label.setText(f"Price: {quote['amount']:,}")
        except Exception as error:
            self._show_error("Price lookup failed", error)

    def create_sale(self) -> None:
        if not self.selected_customer:
            self._show_error("Sale failed", "Select a customer first")
            return
        try:
            duration_seconds = self.duration_combo.currentData()
            quote = self.api_client.quote("GAMING", duration_seconds)
            sale = self.api_client.create_sale(
                {
                    "customer_id": self.selected_customer["id"],
                    "item_type": "GAMING",
                    "item_name": f"Gaming {duration_seconds} seconds",
                    "duration_seconds": duration_seconds,
                    "amount": quote["amount"],
                    "payment_method": self.payment_combo.currentText(),
                    "request_id": f"OP-SALE-{uuid4().hex.upper()}",
                }
            )
            self.status_label.setText(f"Sale {sale['id']} created: payment pending")
        except Exception as error:
            self._show_error("Sale failed", error)

    @staticmethod
    def _show_error(title: str, error: object) -> None:
        QMessageBox.critical(None, title, str(error))