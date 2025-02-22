import os
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget, \
    QStackedWidget
from operationpage import OperationPage


class MainWindow(QtWidgets.QMainWindow):
    recognition_result = pyqtSignal(str, bool)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FaceAuth Pro")
        self.setGeometry(100, 100, 1280, 720)
        self.current_face = None
        self.logic = None  # Initialize logic here
        self.setup_ui()
        self.setup_styles()
        self.recognition_result.connect(self.handle_recognition_result)
        print("Recognition result signal connected")

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Stacked Widget to switch between tabs and operation page
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # Main Tabs Widget
        self.tabs_widget = QWidget()
        tabs_layout = QVBoxLayout(self.tabs_widget)
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabBarAutoHide(False)

        # Registration Tab
        self.registration_tab = QWidget()
        self.setup_registration_tab()

        # Recognition Tab
        self.recognition_tab = QWidget()
        self.setup_recognition_tab()

        self.tabs.addTab(self.registration_tab, "Face Registration")
        self.tabs.addTab(self.recognition_tab, "Face Recognition")
        tabs_layout.addWidget(self.tabs)

        # Operation Page (new, with name passed and reference to MainWindow)
        self.operation_page = OperationPage(name=None, main_window=self)

        # Add to stack
        self.stack.addWidget(self.tabs_widget)  # Index 0
        self.stack.addWidget(self.operation_page)  # Index 1

        # Status Bar
        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)

    def setup_registration_tab(self):
        layout = QVBoxLayout(self.registration_tab)
        self.camera_label_reg = QLabel()
        self.camera_label_reg.setAlignment(Qt.AlignCenter)
        self.camera_label_reg.setMinimumSize(640, 480)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter name")
        self.register_btn = QPushButton("Register Face")
        self.register_btn.setObjectName("primaryButton")

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.name_input)
        controls_layout.addWidget(self.register_btn)

        layout.addWidget(self.camera_label_reg)
        layout.addLayout(controls_layout)

    def setup_recognition_tab(self):
        layout = QVBoxLayout(self.recognition_tab)
        self.camera_label_rec = QLabel()
        self.camera_label_rec.setAlignment(QtCore.Qt.AlignCenter)
        self.camera_label_rec.setMinimumSize(640, 480)
        self.result_label = QLabel()
        self.result_label.setAlignment(QtCore.Qt.AlignCenter)

        layout.addWidget(self.camera_label_rec)
        layout.addWidget(self.result_label)

    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #2D2D2D; }
            QTabWidget::pane { border: 0; }
            QTabBar::tab { background: #404040; color: white; padding: 10px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
            QTabBar::tab:selected { background: #505050; }
            QLabel { color: white; }
            QLineEdit { padding: 8px; border-radius: 4px; border: 1px solid #606060; background: #404040; color: white; }
            QPushButton { padding: 8px 16px; border-radius: 4px; background: #404040; color: white; }
            QPushButton#primaryButton { background: #007BFF; }
            QPushButton#successButton { background: #28A745; }
            QPushButton#secondaryButton { background: #6C757D; }
        """)

    def update_camera_feed(self, image):
        pixmap = QtGui.QPixmap.fromImage(image)
        scaled_pixmap = pixmap.scaled(
            self.camera_label_reg.size() if self.tabs.currentIndex() == 0 else self.camera_label_rec.size(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        if self.stack.currentIndex() == 0:  # Only update if on tabs
            if self.tabs.currentIndex() == 0:
                self.camera_label_reg.setPixmap(scaled_pixmap)
            else:
                self.camera_label_rec.setPixmap(scaled_pixmap)

    def handle_recognition_result(self, name, authenticated):
        print(f"Received recognition result: name={name}, authenticated={authenticated}")
        if authenticated:
            self.operation_page.set_name(name)  # Set the name on the operation page
            self.stack.setCurrentIndex(1)  # Switch to operation page (index 1)
            if self.logic:
                self.logic.stop_camera()  # Stop the camera when navigating to operation page
            else:
                print("Error: Logic not initialized")
        else:
            self.result_label.setText("Not authenticated to access")
            self.result_label.setStyleSheet("color: #DC3545; font-size: 24px;")

    def closeEvent(self, event):
        """Override close event to stop the camera and logic thread."""
        if hasattr(self, 'logic') and self.logic:
            self.logic.stop()
        event.accept()
