from globals import *

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.setup_ui()
        self.load_user_stats()

    def setup_ui(self):
        self.setWindowTitle("Lazer")
        self.setWindowIcon(QIcon("icon.ico"))
        self.setFixedSize(500, 200)
        self.setStyleSheet("""
            background-color: #121212;
            color: white;
        """)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 15)
        main_layout.setSpacing(0)

        # Progress bar at top
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(18, 18, 18, 0.95);
                border: none;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FFB6C1, stop:1 #87CEEB);
                border-radius: 2px;
            }
        """)
        main_layout.addWidget(self.progress_bar)

        # Content container
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 15, 20, 0)
        content_layout.setSpacing(15)

        # Welcome message
        self.status_label = QLabel(f"Welcome, {context.user.username}")
        self.status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFixedHeight(45)
        self.status_label.setStyleSheet("""
            background-color: rgba(18, 18, 18, 0.9);
            color: white;
            border-radius: 8px;
            padding: 12px;
            margin: 0px 20px;
            border-left: 3px solid #87CEEB;
        """)

        # Stats container
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        # DMs count box
        self.dms_box = QLabel("User's DMs: --")
        self.dms_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dms_box.setFixedHeight(40)
        self.dms_box.setStyleSheet("""
            background-color: rgba(18, 18, 18, 0.9);
            color: white;
            border-radius: 4px;
            padding: 10px 20px;
            border-left: 3px solid #FFB6C1;
            font-size: 13px;
        """)
        
        # Servers count box
        self.servers_box = QLabel("Servers Joined: --")
        self.servers_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.servers_box.setFixedHeight(40)
        self.servers_box.setStyleSheet("""
            background-color: rgba(18, 18, 18, 0.9);
            color: white;
            border-radius: 4px;
            padding: 10px 20px;
            border-left: 3px solid #87CEEB;
            font-size: 13px;
        """)
        
        stats_layout.addWidget(self.dms_box)
        stats_layout.addWidget(self.servers_box)

        # Buttons
        self.select_btn = QPushButton("Select Channels")
        self.select_btn.setFixedSize(140, 40)
        self.select_btn.setEnabled(False)  # Initially disabled
        self.select_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(35, 35, 35, 0.9);
                color: white;
                border-radius: 5px;
                border: 1px solid #87CEEB;
            }
            QPushButton:hover {
                background-color: rgba(50, 50, 50, 0.9);
                border: 2px solid #87CEEB;
            }
            QPushButton:pressed {
                background-color: rgba(35, 35, 35, 0.9);
            }
            QPushButton:disabled {
                background-color: rgba(30, 30, 30, 0.9);
                color: #777777;
                border: 1px solid #222222;
            }
        """)
        self.select_btn.clicked.connect(self.show_selector)

        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setFixedSize(140, 40)
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(35, 35, 35, 0.9);
                color: white;
                border-radius: 5px;
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
        self.logout_btn.clicked.connect(self.confirm_logout)

        # Button layout
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.logout_btn)
        btn_layout.addWidget(self.select_btn)
        btn_layout.addStretch()

        # Assemble content layout
        content_layout.addWidget(self.status_label)
        content_layout.addLayout(stats_layout)
        content_layout.addLayout(btn_layout)
        content_widget.setLayout(content_layout)

        main_layout.addWidget(content_widget)
        self.setLayout(main_layout)

    def load_user_stats(self):
        self.stats_fetcher = DataFetcher()
        self.stats_fetcher.data_loaded.connect(self.update_stats)
        self.stats_fetcher.error_occurred.connect(self.show_stats_error)
        self.stats_fetcher.start()

    def update_stats(self, dms, servers):
        """Enable select button only when both DMs and servers are loaded"""
        self.dms_box.setText(f"User's DMs: {len(dms)}")
        self.servers_box.setText(f"Servers Joined: {len(servers)}")
        context.dms = dms
        context.servers = servers
        self.select_btn.setEnabled(True)  # Enable when both datasets are ready

    def show_stats_error(self, error):
        self.dms_box.setText("DMs: Error loading")
        self.servers_box.setText("Servers: Error loading")
        self.select_btn.setEnabled(False)  # Keep disabled on error
        
        error_msg = QMessageBox()
        error_msg.setWindowTitle("Error")
        error_msg.setText(f"Failed to load user stats:\n{error}")
        error_msg.setIcon(QMessageBox.Icon.Warning)
        error_msg.setStyleSheet("""
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
        error_msg.exec()

    def confirm_logout(self):
        confirm = QMessageBox()
        confirm.setWindowTitle("Confirm Logout")
        confirm.setText("Are you sure you want to logout?")
        confirm.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        confirm.setDefaultButton(QMessageBox.StandardButton.No)
        confirm.setStyleSheet("""
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
        
        if confirm.exec() == QMessageBox.StandardButton.Yes:
            self.close()

    def show_selector(self):
        selector = ChannelSelector()
        if selector.exec() == QDialog.DialogCode.Accepted:
            selected = selector.get_selected()
            if selected:
                self.start_deletion(selected)

    def start_deletion(self, channels):
        if self.worker and self.worker.isRunning():
            return

        self.worker = DeletionWorker(channels)
        self.worker.total_messages_updated.connect(self.progress_bar.setMaximum)
        self.worker.message_progress.connect(self.increment_progress)
        self.worker.channel_progress.connect(self.status_label.setText)
        self.worker.finished.connect(self.on_finished)
        self.worker.error_occurred.connect(self.show_error)
        self.worker.start()

        self.select_btn.setEnabled(False)
        self.select_btn.setText("Deleting...")
        self.status_label.setText("Starting deletion process...")
        self.progress_bar.setValue(0)

    def increment_progress(self):
        current = self.progress_bar.value() + 1
        self.progress_bar.setValue(current)

    def on_finished(self):
        if self.worker.isRunning():
            return
            
        self.select_btn.setEnabled(True)
        self.select_btn.setText("Select Channels")
        self.status_label.setText(f"Completed: {self.progress_bar.value()}/{self.progress_bar.maximum()} messages deleted")
        
        complete_msg = QMessageBox()
        complete_msg.setWindowTitle("Complete")
        complete_msg.setText(f"Deleted {self.progress_bar.value()}/{self.progress_bar.maximum()} messages")
        complete_msg.setIcon(QMessageBox.Icon.Information)
        complete_msg.setStyleSheet("""
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
        complete_msg.exec()
        self.progress_bar.setValue(0)

    def show_error(self, error, context):
        error_msg = QMessageBox()
        error_msg.setWindowTitle("Error")
        error_msg.setText(f"Error in {context}:\n{error}")
        error_msg.setIcon(QMessageBox.Icon.Critical)
        error_msg.setStyleSheet("""
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
        error_msg.exec()