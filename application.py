from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import Qt
import sys
from modules.signup_window import SignUpWindow
from modules.signin_window import SignInWindow
from modules.delete_window import DeleteAccountWindow
from modules.auth_utils import connect_to_cloud_db

class DriverLoginGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Driver Login Panel")
        self.setFixedSize(400, 300)

        # Connect to MongoDB
        try:
            self.users_col, self.sessions_col = connect_to_cloud_db()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Could not connect to cloud DB: {e}")
            sys.exit(1)

        # Title label
        title_label = QLabel("Hello Driver!", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        # Buttons
        sign_up_btn = QPushButton("Sign Up")
        sign_in_btn = QPushButton("Sign In")
        delete_btn = QPushButton("Delete Account")

        # Connect buttons
        sign_up_btn.clicked.connect(self.sign_up)
        sign_in_btn.clicked.connect(self.sign_in)
        delete_btn.clicked.connect(self.delete_account)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addSpacing(20)
        layout.addWidget(sign_up_btn)
        layout.addWidget(sign_in_btn)
        layout.addWidget(delete_btn)

        self.setLayout(layout)

    def sign_up(self):
        signup_dialog = SignUpWindow(self.users_col)
        signup_dialog.exec_()

    def sign_in(self):
        signin_dialog = SignInWindow(self.users_col, self.sessions_col)
        signin_dialog.exec_()

    def delete_account(self):
        delete_dialog = DeleteAccountWindow(self.users_col, self.sessions_col)
        delete_dialog.exec_()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "Exit Confirmation",
            "Are you sure you want to quit?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DriverLoginGUI()
    window.show()
    sys.exit(app.exec_())