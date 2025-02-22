from PyQt5 import QtWidgets, QtCore
from ui import MainWindow
from logic import FaceAuthLogic

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    logic = FaceAuthLogic(window)
    logic.frame_processed.connect(window.update_camera_feed)
    logic.recognition_result.connect(window.handle_recognition_result, QtCore.Qt.QueuedConnection)
    window.show()
    print("Logic and UI connected")
    app.exec_()