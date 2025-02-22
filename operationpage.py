from PyQt5 import QtCore, QtWidgets


class OperationPage(QtWidgets.QWidget):
    def __init__(self, name=None, main_window=None):
        super().__init__()
        self.back_btn = None
        self.confirm_btn = None
        self.name_label = None
        self.title_label = None
        self.name = name
        self.main_window = main_window
        self.setup_ui()
        self.setup_styles()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignCenter)

        # Title
        self.title_label = QtWidgets.QLabel("Operation")
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 36px; color: #28A745;")

        # Name Label
        self.name_label = QtWidgets.QLabel(f"Name: {self.name}" if self.name else "No name")
        self.name_label.setAlignment(QtCore.Qt.AlignCenter)
        self.name_label.setStyleSheet("font-size: 20px; color: white;")

        # Buttons
        self.confirm_btn = QtWidgets.QPushButton("Confirm Operation")
        self.confirm_btn.setObjectName("successButton")
        self.confirm_btn.clicked.connect(self.handle_confirm)

        self.back_btn = QtWidgets.QPushButton("Back")
        self.back_btn.setObjectName("secondaryButton")
        self.back_btn.clicked.connect(self.handle_back)

        # Add widgets to layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.name_label)
        layout.addWidget(self.confirm_btn)
        layout.addWidget(self.back_btn)
        layout.addStretch()

    def setup_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2D2D2D;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                padding: 12px 24px;
                border-radius: 4px;
                background: #404040;
                color: white;
            }
            QPushButton#successButton {
                background: #28A745;
            }
            QPushButton#secondaryButton {
                background: #6C757D;  # Gray for Back button
            }
        """)

    def handle_confirm(self):
        print("Operation confirmed successfully")

    def handle_back(self):
        if self.main_window:
            self.main_window.stack.setCurrentIndex(0)  # Go back to tabs
            self.main_window.tabs.setCurrentIndex(1)  # Go to Face Recognition tab
        else:
            print("Error: MainWindow reference not set")

    def set_name(self, name):
        """Update the name displayed on the page."""
        self.name = name
        self.name_label.setText(f"Name: {name}" if name else "No name")
