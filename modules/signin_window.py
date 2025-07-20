from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from auth_utils import sign_in
from monitoring_window import MonitoringWindow  # Add this import

class SignInWindow(QDialog):
    def __init__(self, users_col, sessions_col):
        super().__init__()
        self.users_col = users_col
        self.sessions_col = sessions_col
        self.setWindowTitle("Sign In")
        self.setFixedSize(300, 200)

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.signin_btn = QPushButton("Log In")
        self.signin_btn.clicked.connect(self.try_signin)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Username:")); layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Password:")); layout.addWidget(self.password_input)
        layout.addWidget(self.signin_btn)

    def try_signin(self):
        user = self.username_input.text().strip()
        pwd  = self.password_input.text().strip()

        if sign_in(self.users_col, user, pwd):
            print(f"Sign-in successful for user: {user}")
            self.accept()

            # 🧭 Launch Monitoring Window
            monitor_window = MonitoringWindow(user, self.sessions_col)
            monitor_window.exec_()
        else:
            QMessageBox.warning(self, "Invalid Credentials", "Username or password is incorrect.")