from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from auth_utils import sign_in, delete_account

class DeleteAccountWindow(QDialog):
    def __init__(self, users_col, sessions_col):
        super().__init__()
        self.users_col = users_col
        self.sessions_col = sessions_col
        self.setWindowTitle("Delete Account")
        self.setFixedSize(300, 200)

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.delete_btn = QPushButton("Delete Account")
        self.delete_btn.clicked.connect(self.try_delete)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Username:")); layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Password:")); layout.addWidget(self.password_input)
        layout.addWidget(self.delete_btn)

    def try_delete(self):
        user = self.username_input.text().strip()
        pwd  = self.password_input.text().strip()

        if sign_in(self.users_col, user, pwd):
            reply = QMessageBox.question(
                self, "Confirm Deletion",
                f"Are you sure you want to permanently delete '{user}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    delete_account(self.users_col, self.sessions_col, user)
                    QMessageBox.information(self, "Deleted", f"Account '{user}' has been removed.")
                    self.accept()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to delete account: {e}")
        else:
            QMessageBox.warning(self, "Invalid Credentials", "Username or password is incorrect.")