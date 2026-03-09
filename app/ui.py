import sys
import os

# ---------------- PYINSTALLER SAFE BASE PATH ----------------
BASE_DIR = getattr(
    sys,
    "_MEIPASS",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

SRC_DIR = os.path.join(BASE_DIR, "src")
DATA_DIR = os.path.join(BASE_DIR, "data")

sys.path.insert(0, SRC_DIR)

# 🔥 CRITICAL FIX FOR face_recognition MODELS
os.environ["FACE_RECOGNITION_MODELS"] = os.path.join(
    BASE_DIR, "face_recognition_models", "models"
)

# -----------------------------------------------------------

import cv2
from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QLineEdit, QMessageBox, QFileDialog, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont

from recognizer import FaceRecognizer
from attendance import AttendanceManager
from register import FaceRegistrar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Face Attendance System")
        self.setGeometry(100, 100, 1200, 750)

        header = QLabel("Face Attendance System")
        header.setFont(QFont("Arial", 18, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setFixedHeight(60)

        self.video_label = QLabel("Camera / Image Preview")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setFixedSize(800, 500)
        self.video_label.setFrameShape(QFrame.Box)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter name to register")

        self.register_btn = QPushButton("Register Face")
        self.start_btn = QPushButton("Start Camera")
        self.stop_btn = QPushButton("Stop Camera")
        self.import_btn = QPushButton("Import Image")

        self.status = QLabel("Status: Ready")
        self.status.setStyleSheet("color: green;")

        right = QVBoxLayout()
        right.addWidget(self.name_input)
        right.addWidget(self.register_btn)
        right.addSpacing(15)
        right.addWidget(self.start_btn)
        right.addWidget(self.stop_btn)
        right.addWidget(self.import_btn)
        right.addSpacing(15)
        right.addWidget(self.status)
        right.addStretch()

        right_widget = QWidget()
        right_widget.setLayout(right)
        right_widget.setFixedWidth(300)

        main = QHBoxLayout()
        main.addWidget(self.video_label)
        main.addWidget(right_widget)

        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(header)
        layout.addLayout(main)
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.faces_dir = os.path.join(DATA_DIR, "faces")
        self.recognizer = FaceRecognizer(self.faces_dir)
        self.attendance = AttendanceManager()
        self.registrar = FaceRegistrar(self.faces_dir)

        self.start_btn.clicked.connect(self.start_camera)
        self.stop_btn.clicked.connect(self.stop_camera)
        self.register_btn.clicked.connect(self.register_face)
        self.import_btn.clicked.connect(self.import_image)

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.timer.start(30)
        self.status.setText("Status: Camera running")

    def stop_camera(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
        self.video_label.setText("Camera stopped")
        self.status.setText("Status: Camera stopped")

    def register_face(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Enter a name")
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        success, msg = self.registrar.register(name, frame)
        QMessageBox.information(self, "Result", msg)
        self.recognizer = FaceRecognizer(self.faces_dir)

    def import_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.jpg *.png *.jpeg)"
        )
        if not path:
            return

        image = cv2.imread(path)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        locations, names = self.recognizer.recognize(rgb)

        for (t, r, b, l), name in zip(locations, names):
            cv2.rectangle(image, (l, t), (r, b), (0, 255, 0), 2)
            cv2.putText(image, name, (l, t - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        self.video_label.setPixmap(
            QPixmap.fromImage(QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888))
        )
        self.status.setText("Status: Image analyzed")

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locations, names = self.recognizer.recognize(rgb)

        for (t, r, b, l), name in zip(locations, names):
            if name != "Unknown":
                self.attendance.mark_attendance(name)

            cv2.rectangle(frame, (l, t), (r, b), (0, 255, 0), 2)
            cv2.putText(frame, name, (l, t - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        self.video_label.setPixmap(
            QPixmap.fromImage(QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888))
        )

