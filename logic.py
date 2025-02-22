import os
import cv2
from deepface import DeepFace
from PyQt5 import QtCore, QtGui

class FaceAuthLogic(QtCore.QObject):
    frame_processed = QtCore.pyqtSignal(QtGui.QImage)
    recognition_result = QtCore.pyqtSignal(str, bool)
    status_message = QtCore.pyqtSignal(str, int)
    camera_stopped = QtCore.pyqtSignal()  # Signal to notify when camera stops

    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.registered_faces = {}
        self.current_face = None
        self.last_recognition_time = 0
        self.recognition_cooldown = 0.5  # Reduced for faster testing

        # Connect UI signals
        self.ui.register_btn.clicked.connect(self.register_face)
        self.status_message.connect(self.ui.status_bar.showMessage)
        self.camera_stopped.connect(self.on_camera_stopped)  # Connect camera stopped signal

        # Start camera thread
        self.thread = QtCore.QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self.process_video)
        self.thread.start()

        # Initialize face database
        if not os.path.exists("faces"):
            os.makedirs("faces")
        self.load_registered_faces()

    def load_registered_faces(self):
        self.registered_faces = {}
        for file in os.listdir("faces"):
            if file.endswith(".jpg"):
                name = os.path.splitext(file)[0]
                self.registered_faces[name] = os.path.join("faces", file)
                print(f"Loaded face: {name} at {self.registered_faces[name]}")

    def process_video(self):
        while self.running:
            if not self.cap or not self.cap.isOpened():
                break
            ret, frame = self.cap.read()
            if ret and self.running:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.detect_faces(rgb_image)
                qt_image = QtGui.QImage(rgb_image.data, rgb_image.shape[1], rgb_image.shape[0],
                                       rgb_image.strides[0], QtGui.QImage.Format_RGB888)
                self.frame_processed.emit(qt_image)
            QtCore.QThread.msleep(30)

    def detect_faces(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))

        if len(faces) > 0:
            x, y, w, h = faces[0]
            self.current_face = frame[y:y + h, x:x + w].copy()
            print(f"Detected face shape: {self.current_face.shape}")
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Face Detected", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            current_time = QtCore.QTime.currentTime().msecsSinceStartOfDay() / 1000.0
            if self.ui.tabs.currentIndex() == 1 and current_time - self.last_recognition_time > self.recognition_cooldown:
                print("Attempting to verify face...")
                self.verify_face(self.current_face)
                self.last_recognition_time = current_time
        else:
            self.current_face = None

        cv2.putText(frame, f"Faces Detected: {len(faces)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    def verify_face(self, face_roi):
        try:
            face_path = os.path.join("faces", "temp.jpg")
            cv2.imwrite(face_path, cv2.cvtColor(face_roi, cv2.COLOR_RGB2BGR))
            print(f"Temp face saved at: {face_path}")

            for name, registered_path in self.registered_faces.items():
                print(f"Comparing with registered face: {name} at {registered_path}")
                result = DeepFace.verify(
                    img1_path=face_path,
                    img2_path=registered_path,
                    model_name="VGG-Face",
                    distance_metric="cosine",
                    enforce_detection=False
                )
                print(f"Verification result for {name}: {result}")
                if result["verified"]:
                    print(f"Emitting recognition result for {name} with True")
                    self.recognition_result.emit(name, True)
                    os.remove(face_path)
                    return
            print("No match found, emitting empty result")
            self.recognition_result.emit("", False)
        except Exception as e:
            print(f"Verification error: {e}")
            self.recognition_result.emit("", False)

    def register_face(self):
        name = self.ui.name_input.text().strip()
        if not name:
            self.status_message.emit("❌ Please enter a name!", 3000)
            return
        if self.current_face is None or self.current_face.size == 0:
            self.status_message.emit("❌ No valid face detected!", 3000)
            return

        face_path = os.path.join("faces", f"{name}.jpg")
        try:
            cv2.imwrite(face_path, cv2.cvtColor(self.current_face, cv2.COLOR_RGB2BGR))
            self.status_message.emit(f"✅ Face registered: {name}", 3000)
            QtCore.QMetaObject.invokeMethod(self.ui.name_input, "clear", QtCore.Qt.QueuedConnection)
            self.load_registered_faces()  # Refresh registered faces
            print(f"Registered new face: {name} at {face_path}")
        except Exception as e:
            self.status_message.emit(f"❌ Error: {str(e)}", 5000)

    def stop_camera(self):
        """Stop the camera and release resources safely."""
        if self.cap and self.cap.isOpened():
            self.running = False
            while self.cap.isOpened():  # Ensure camera is fully released
                ret = self.cap.grab()
                if not ret:
                    break
            self.cap.release()
            self.camera_stopped.emit()
            print("Camera stopped")
        else:
            print("Camera already stopped or not initialized")

    def start_camera(self):
        """Restart the camera if needed (optional, for future use)."""
        if not self.cap or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)
            self.running = True
            self.thread = QtCore.QThread()
            self.moveToThread(self.thread)
            self.thread.started.connect(self.process_video)
            self.thread.start()
            print("Camera restarted")

    def on_camera_stopped(self):
        """Handle camera stopped signal (optional debug or UI update)."""
        print("Camera stopped event received")

    def stop(self):
        self.stop_camera()
        if self.thread:
            self.thread.quit()
            self.thread.wait()