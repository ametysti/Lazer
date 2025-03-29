from globals import *
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import binascii

ENCRYPTION_KEY = bytes.fromhex("6821be3c5fb0deaa8ed7c8ecb67241a17c6b164986bf2bc20b615b0eff805736")
NONCE = bytes.fromhex("981581d01d703b1d4c79701f")

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - Lazer")
        self.setFixedSize(350, 150)
        self.set_background_image()
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)

        context.token_label = QLabel("Enter Token")
        context.token_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        context.token_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        context.token_label.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.3);
            border-radius: 8px;
            padding: 6px;
            margin: 0 30px;
        """)

        context.token_input = QLineEdit()
        context.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        context.token_input.setFont(QFont("Arial", 12))
        context.token_input.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 5px;
            padding: 8px;
            color: black;
        """)

        self.help_btn = QPushButton("?")
        self.help_btn.setFixedSize(28, 28)
        self.help_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.3);
                border-radius: 14px;
                color: black;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.6);
            }
        """)
        self.help_btn.clicked.connect(self.show_help)

        self.visibility_btn = QPushButton("👁")
        self.visibility_btn.setFixedSize(28, 28)
        self.visibility_btn.setStyleSheet(self.help_btn.styleSheet())
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
                background-color: rgba(255, 255, 255, 0.3);
                color: black;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.6);
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

    def set_background_image(self):
        pixmap = QPixmap("assets/background.jpg")
        background_label = QLabel(self)
        background_label.setPixmap(pixmap)
        background_label.setGeometry(self.rect())
        background_label.setScaledContents(True)
        self.setAutoFillBackground(True)

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
            QMessageBox.warning(self, "Login Failed", "Invalid token. Please make sure it is formatted correctly.")
