from globals import *
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import binascii

ENCRYPTION_KEY = bytes.fromhex("6821be3c5fb0deaa8ed7c8ecb67241a17c6b164986bf2bc20b615b0eff805736")
NONCE = bytes.fromhex("981581d01d703b1d4c79701f")

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - Lazer")
        self.setWindowIcon(QIcon("icon.ico"))
        self.setFixedSize(350, 150)
        self.setStyleSheet("""
            background-color: #121212;
            color: white;
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)

        context.token_label = QLabel("Enter Token")
        context.token_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        context.token_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        context.token_label.setStyleSheet("""
            background-color: rgba(18, 18, 18, 0.9);
            color: white;
            border-radius: 8px;
            padding: 6px;
            margin: 0 30px;
            border-bottom: 2px solid #87CEEB;
        """)

        context.token_input = QLineEdit()
        context.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        context.token_input.setFont(QFont("Arial", 12))
        context.token_input.setStyleSheet("""
            background-color: rgba(35, 35, 35, 0.9);
            border: 1px solid #444;
            border-radius: 5px;
            padding: 8px;
            color: white;
            selection-background-color: #87CEEB;
        """)

        self.help_btn = QPushButton("?")
        self.help_btn.setFixedSize(28, 28)
        self.help_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(35, 35, 35, 0.9);
                border-radius: 14px;
                color: white;
                border: 1px solid #FFB6C1;
            }
            QPushButton:hover {
                background-color: rgba(50, 50, 50, 0.9);
                border: 2px solid #FFB6C1;
            }
            QPushButton:pressed {
                background-color: rgba(35, 35, 35, 0.9);
            }
        """)
        self.help_btn.clicked.connect(self.show_help)

        self.visibility_btn = QPushButton("👁")
        self.visibility_btn.setFixedSize(28, 28)
        self.visibility_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(35, 35, 35, 0.9);
                border-radius: 14px;
                color: white;
                border: 1px solid #87CEEB;
            }
            QPushButton:hover {
                background-color: rgba(50, 50, 50, 0.9);
                border: 2px solid #87CEEB;
            }
            QPushButton:pressed {
                background-color: rgba(35, 35, 35, 0.9);
            }
        """)
        self.visibility_btn.clicked.connect(self.toggle_visibility)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.help_btn)
        btn_layout.addWidget(context.token_input)
        btn_layout.addWidget(self.visibility_btn)

        self.login_btn = QPushButton("Login")
        self.login_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.login_btn.setFixedSize(120, 40)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(35, 35, 35, 0.9);
                color: white;
                border-radius: 5px;
                border: 1px solid #87CEEB;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(50, 50, 50, 0.9);
                border: 2px solid #87CEEB;
            }
            QPushButton:pressed {
                background-color: rgba(35, 35, 35, 0.9);
            }
        """)
        self.login_btn.clicked.connect(self.accept)

        layout.addWidget(context.token_label)
        layout.addLayout(btn_layout)
        layout.addWidget(self.login_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        self.cached_token = self.load_cached_token()
        if self.cached_token:
            context.token_input.setText(self.cached_token)

    def toggle_visibility(self):
        current = context.token_input.echoMode()
        new_mode = QLineEdit.EchoMode.Normal if current == QLineEdit.EchoMode.Password else QLineEdit.EchoMode.Password
        context.token_input.setEchoMode(new_mode)

    def show_help(self):
        help_text = """<b>How to Get Your Discord Token:</b>
        <ol>
            <li>Open Discord in your browser</li>
            <li>Press Ctrl+Shift+I to open developer tools</li>
            <li>Go to the Network tab</li>
            <li>Send a message in any DM</li>
            <li>Look for "messages" requests</li>
            <li>Check request headers for "authorization"</li>
        </ol>"""
        
        msg = QMessageBox()
        msg.setWindowTitle("Token Help")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(help_text)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1a1a1a;
                color: white;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border: 1px solid #87CEEB;
            }
        """)
        msg.exec()

    def get_token(self):
        return context.token_input.text()

    def encrypt_token(self, token: str) -> str:
        aesgcm = AESGCM(ENCRYPTION_KEY)
        encrypted_token = aesgcm.encrypt(NONCE, token.encode(), None)
        return binascii.hexlify(encrypted_token).decode()

    def decrypt_token(self, encrypted_token: str) -> str:
        try:
            aesgcm = AESGCM(ENCRYPTION_KEY)
            decrypted_token = aesgcm.decrypt(NONCE, binascii.unhexlify(encrypted_token), None)
            return decrypted_token.decode()
        except Exception:
            return ""  
            
    def load_cached_token(self):
        try:
            with open(".token_cache", "r") as f:
                encrypted_token = f.read().strip()
            return self.decrypt_token(encrypted_token)
        except (FileNotFoundError, ValueError):
            return ""

    def accept(self):
        token = self.get_token()
        if token and api.login(token):
            encrypted_token = self.encrypt_token(token)
            with open(".token_cache", "w") as f:
                f.write(encrypted_token)
            super().accept()
        else:
            error_box = QMessageBox()
            error_box.setWindowTitle("Login Failed")
            error_box.setText("Invalid token. Please make sure it is formatted correctly.")
            error_box.setIcon(QMessageBox.Icon.Warning)
            error_box.setStyleSheet("""
                QMessageBox {
                    background-color: #1a1a1a;
                    color: white;
                }
                QLabel {
                    color: white;
                }
                QPushButton {
                    background-color: #2d2d2d;
                    color: white;
                    border-radius: 4px;
                    padding: 6px 12px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #3d3d3d;
                    border: 1px solid #FFB6C1;
                }
            """)
            error_box.exec()