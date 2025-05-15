# overlay_labels/live_overlay.py

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer

from core.detection.model_loader import load_model
from app.detector_runner import update_detections
from app.draw import draw_objects
from app.voice_controller import start_voice_thread


class LiveOverlay(QWidget):
    def __init__(self):
        super().__init__()

        self.model = load_model()
        self.raw_detections = []
        self.last_frame = None
        self.voice_thread = None
        self.running = True

        self.hash_to_id = {}
        self.id_to_bbox = {}
        self.id_to_full_info = {}
        self.next_id = 0

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        screen = self.screen().geometry()
        self.setGeometry(0, 0, screen.width(), screen.height())

        self.timer = QTimer()
        self.timer.timeout.connect(lambda: update_detections(self))
        self.timer.start(1)

        start_voice_thread(self)

    def paintEvent(self, event):
        draw_objects(self, event)

    def shutdown(self):
        self.running = False
        self.voice_thread.join(timeout=1.0)
        self.timer.stop()
        self.hash_to_id.clear()
        self.id_to_bbox.clear()
        self.id_to_full_info.clear()
        self.next_id = 0
        self.hide()
        self.close()
