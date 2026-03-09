import sqlite3
import csv
from datetime import datetime
import os
import sys


def get_runtime_data_dir():
    """
    If running as EXE → write next to the exe
    If running as python → write to project /data
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        exe_dir = os.path.dirname(sys.executable)
        data_dir = os.path.join(exe_dir, "data")
    else:
        # Running normally
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(project_root, "data")

    os.makedirs(data_dir, exist_ok=True)
    return data_dir


class AttendanceManager:
    def __init__(self, _unused=None):
        self.data_dir = get_runtime_data_dir()

        self.db_path = os.path.join(self.data_dir, "attendance.db")
        self.csv_path = os.path.join(self.data_dir, "attendance.csv")

        self._init_db()
        self.marked_today = set()

        print("[ATTENDANCE] DB path:", self.db_path)
        print("[ATTENDANCE] CSV path:", self.csv_path)

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                date TEXT,
                time TEXT
            )
        """)
        conn.commit()
        conn.close()

        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Name", "Date", "Time"])

    def mark_attendance(self, name):
        today = datetime.now().strftime("%Y-%m-%d")
        if (name, today) in self.marked_today:
            return

        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO attendance (name, date, time) VALUES (?, ?, ?)",
            (name, date, time)
        )
        conn.commit()
        conn.close()

        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([name, date, time])

        self.marked_today.add((name, today))
        print(f"[ATTENDANCE] Marked: {name}")
