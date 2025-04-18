from globals import *

class ChannelSelector(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Channels")
        self.setWindowIcon(QIcon("icon.ico"))
        self.setFixedSize(600, 400)
        self.max_height = 400

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)

        self.setStyleSheet("""
            background-color: #121212;
            color: white;
        """)

        self.loading_label = QLabel("Loading channels...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            background-color: rgba(18, 18, 18, 0.9);
            border-radius: 5px;
            padding: 12px;
            border-bottom: 2px solid #87CEEB;
        """)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #1a1a1a;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #3d3d3d;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #87CEEB;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        self.scroll_area.hide()

        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(0, 10, 0, 0)

        self.cancel_btn = QPushButton("Cancel")
        self.ok_btn = QPushButton("OK")

        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(35, 35, 35, 0.9);
                color: white;
                border: 1px solid #FFB6C1;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: rgba(50, 50, 50, 0.9);
                border: 2px solid #FFB6C1;
            }
            QPushButton:pressed {
                background-color: rgba(35, 35, 35, 0.9);
            }
        """)

        self.ok_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(35, 35, 35, 0.9);
                color: white;
                border: 1px solid #87CEEB;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: rgba(50, 50, 50, 0.9);
                border: 2px solid #87CEEB;
            }
            QPushButton:pressed {
                background-color: rgba(35, 35, 35, 0.9);
            }
        """)

        self.cancel_btn.clicked.connect(self.reject)
        self.ok_btn.clicked.connect(self.accept)

        self.button_layout.addStretch()
        self.button_layout.addWidget(self.cancel_btn)
        self.button_layout.addWidget(self.ok_btn)
        self.button_layout.addStretch()

        layout.addWidget(self.loading_label)
        layout.addWidget(self.scroll_area)
        layout.addLayout(self.button_layout)

        if hasattr(context, 'dms') and hasattr(context, 'servers') and context.dms and context.servers:
            self.populate_ui(context.dms, context.servers)
        else:
            self.fetcher = DataFetcher()
            self.fetcher.data_loaded.connect(self.populate_ui)
            self.fetcher.error_occurred.connect(self.show_error)
            self.fetcher.start()

    def populate_ui(self, dms, servers):
        self.loading_label.hide()

        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        self.scroll_area.setWidget(content)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        toggle_layout = QHBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 1px solid #444;
                border-radius: 4px;
                background-color: rgba(30,30,30,0.95);
                color: white;
            }
        """)
        self.search_bar.textChanged.connect(self.filter_list)

        toggle_layout.addWidget(self.search_bar)

        self.dm_toggle = QPushButton("Show DMs")
        self.dm_toggle.setCheckable(True)
        self.dm_toggle.setChecked(True)
        self.dm_toggle.setStyleSheet("""
            QPushButton {
                background-color: rgba(45,45,45,0.95);
                color: white;
                border: 1px solid #FFB6C1;
                border-radius: 4px;
                padding: 4px 10px;
            }
            QPushButton:checked {
                background-color: #FFB6C1;
                color: black;
            }
        """)
        self.dm_toggle.toggled.connect(self.toggle_dm_list)

        self.server_toggle = QPushButton("Show Servers")
        self.server_toggle.setCheckable(True)
        self.server_toggle.setStyleSheet(self.dm_toggle.styleSheet())
        self.server_toggle.toggled.connect(self.toggle_server_list)

        toggle_layout.addStretch()
        toggle_layout.addWidget(self.dm_toggle)
        toggle_layout.addWidget(self.server_toggle)
        content_layout.addLayout(toggle_layout)

        self.dm_group = self.create_group(dms, "Direct Messages", True)
        self.server_group = self.create_group(servers, "Servers", False)

        content_layout.addWidget(self.dm_group)
        content_layout.addWidget(self.server_group)

        self.server_group.setVisible(False)

        self.scroll_area.show()

    def toggle_dm_list(self, checked):
        if checked:
            self.server_toggle.setChecked(False)
            self.dm_group.setVisible(True)
            self.server_group.setVisible(False)
        else:
            self.dm_group.setVisible(False)
            # Automatically show servers if DMs are disabled
            if not self.server_toggle.isChecked():
                self.server_toggle.setChecked(True)
                self.server_group.setVisible(True)

    def toggle_server_list(self, checked):
        if checked:
            self.dm_toggle.setChecked(False)
            self.server_group.setVisible(True)
            self.dm_group.setVisible(False)
        else:
            self.server_group.setVisible(False)
            # Automatically show DMs if servers are disabled
            if not self.dm_toggle.isChecked():
                self.dm_toggle.setChecked(True)
                self.dm_group.setVisible(True)

    def filter_list(self):
        search_text = self.search_bar.text().lower()

        self.filter_group(self.dm_list, search_text)
        self.filter_group(self.server_list, search_text)

    def filter_group(self, list_widget, search_text):
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            item_widget = list_widget.itemWidget(item)
            name_label = item_widget.findChild(QLabel)

            if name_label and search_text in name_label.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def create_group(self, items, title, is_dm):
        group = QGroupBox()
        group.setStyleSheet("""
            QGroupBox {
                background-color: rgba(18, 18, 18, 0.9);
                border: 1px solid #333333;
                border-radius: 8px;
                margin-top: 10px;
            }
        """)
        layout = QVBoxLayout(group)

        header_layout = QHBoxLayout()
        label = QLabel(title)
        label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; padding-left: 6px;")

        button = QPushButton("Select All")
        button.setFixedSize(90, 24)
        button.setStyleSheet("""
            QPushButton {
                background-color: rgba(35,35,35,0.9);
                color: white;
                border: 1px solid #FFB6C1;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:checked {
                background-color: #FFB6C1;
                color: black;
            }
        """)
        header_layout.addWidget(label)
        header_layout.addStretch()
        header_layout.addWidget(button)
        layout.addLayout(header_layout)

        list_widget = QListWidget()
        list_widget.setStyleSheet("""
            QListWidget {
                background-color: rgba(22, 22, 22, 0.8);
                border: none;
                border-radius: 4px;
                font-size: 14px;
                color: white;
            }
            QListWidget::item {
                border-bottom: 1px solid #333333;
                padding: 2px 0px;
            }
            QListWidget::item:selected {
                background-color: rgba(135, 206, 235, 0.3);
                border-left: 3px solid #87CEEB;
            }
            QListWidget::item:hover:!selected {
                background-color: rgba(45, 45, 45, 0.7);
            }
        """)
        list_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        for item_data in items:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, item_data)
            item.setSizeHint(QSize(0, 40))
            widget = self.create_list_item(item_data["name"])
            list_widget.addItem(item)
            list_widget.setItemWidget(item, widget)
        layout.addWidget(list_widget)

        button.clicked.connect(lambda: self.toggle_select_all(list_widget, button))

        if is_dm:
            self.dm_list = list_widget
        else:
            self.server_list = list_widget

        return group

    def toggle_select_all(self, list_widget, button):
        select = button.text() == "Select All"
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            item.setSelected(select)
        button.setText("Deselect All" if select else "Select All")

    def create_list_item(self, name):
        widget = QWidget()
        widget.setStyleSheet("background-color: transparent;")
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(12, 8, 12, 8)

        name_label = QLabel(name)
        name_label.setStyleSheet("color: white; font-size: 13px; background-color: transparent;")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)

        return widget

    def show_error(self, message):
        error_msg = QMessageBox()
        error_msg.setWindowTitle("Error")
        error_msg.setText(f"Failed to load data:\n{message}")
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
        self.reject()

    def get_selected(self):
        selected = []
        for i in range(self.dm_list.count()):
            if self.dm_list.item(i).isSelected():
                selected.append(self.dm_list.item(i).data(Qt.ItemDataRole.UserRole))
        for i in range(self.server_list.count()):
            if self.server_list.item(i).isSelected():
                selected.append(self.server_list.item(i).data(Qt.ItemDataRole.UserRole))
        return selected
