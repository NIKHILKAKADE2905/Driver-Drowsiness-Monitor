from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from auth_utils import sign_up

class SignUpWindow(QDialog):
    def __init__(self, users_col):
        super().__init__()
        self.users_col = users_col
        self.setWindowTitle("Create Account")
        self.setFixedSize(300, 200)

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.signup_btn = QPushButton("Create Account")
        self.signup_btn.clicked.connect(self.try_signup)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Username:")); layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Password:")); layout.addWidget(self.password_input)
        layout.addWidget(self.signup_btn)

    def try_signup(self):
        user = self.username_input.text().strip()
        pwd  = self.password_input.text().strip()

        if not user or not pwd:
            QMessageBox.warning(self, "Missing Info", "Please enter both username and password.")
            return

        if sign_up(self.users_col, user, pwd):
            QMessageBox.information(self, "Success", f"Account created for '{user}'!")
            self.accept()
        else:
            QMessageBox.warning(self, "Username Taken", "That username already exists. Please choose another.")