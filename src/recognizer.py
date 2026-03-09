import os
import face_recognition


class FaceRecognizer:
    def __init__(self, faces_dir):
        self.known_encodings = []
        self.known_names = []
        self.load_known_faces(faces_dir)

    def load_known_faces(self, faces_dir):
        if not os.path.exists(faces_dir):
            return

        for person in os.listdir(faces_dir):
            person_path = os.path.join(faces_dir, person)
            if not os.path.isdir(person_path):
                continue

            for img in os.listdir(person_path):
                img_path = os.path.join(person_path, img)
                image = face_recognition.load_image_file(img_path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    self.known_encodings.append(encodings[0])
                    self.known_names.append(person)

    def recognize(self, rgb):
        locations = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, locations)

        names = []
        for enc in encodings:
            matches = face_recognition.compare_faces(
                self.known_encodings, enc, tolerance=0.5
            )
            name = "Unknown"
            if True in matches:
                name = self.known_names[matches.index(True)]
            names.append(name)

        return locations, names
