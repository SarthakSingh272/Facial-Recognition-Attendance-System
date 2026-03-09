import os
import cv2
import face_recognition
from datetime import datetime


class FaceRegistrar:
    def __init__(self, faces_dir):
        self.faces_dir = faces_dir
        os.makedirs(self.faces_dir, exist_ok=True)

    def register(self, name, frame):
        person_dir = os.path.join(self.faces_dir, name)
        os.makedirs(person_dir, exist_ok=True)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb)

        if len(locations) != 1:
            return False, "Ensure exactly one face is visible"

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(person_dir, f"{ts}.jpg")
        cv2.imwrite(path, frame)
        return True, f"Saved: {path}"
