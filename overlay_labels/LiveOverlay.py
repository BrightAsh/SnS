# overlay_labels/LiveOverlay.py (해시 기반 제품 ID 매핑 적용)

import mss
import cv2
import numpy as np
import threading
import webbrowser
import imagehash
from PIL import Image

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QFont

from detection.model_loader import load_model
from detection.detector import detect_objects
from voice.listener import listen_for_command
from gpt.commands import interpret_command
from utils.tts import speak
from search.cropper import crop_object
from embedding.clip_text_predictor import predict_label
from gpt.product_name_generator import generate_product_name
from search.naver_api import search_naver_shopping


def get_image_hash(image_bgr):
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    image_pil = Image.fromarray(image_rgb)
    return imagehash.phash(image_pil)


class LiveOverlay(QWidget):
    def __init__(self):
        super().__init__()

        self.model = load_model()
        self.raw_detections = []
        self.last_frame = None
        self.voice_thread = None
        self.running = True

        self.hash_to_id = {}      # 해시 → 고유 ID
        self.id_to_bbox = {}      # ID → bbox
        self.next_id = 0          # 다음 부여할 번호

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
        self.timer.timeout.connect(self.update_detections)
        self.timer.start(100)

        self.start_voice_thread()

    def update_detections(self):
        self.hide()
        self.repaint()

        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        self.show()

        self.last_frame = frame
        self.raw_detections = detect_objects(self.model, frame)

        new_id_to_bbox = {}
        for det in self.raw_detections:
            bbox = det["bbox"]
            cropped = crop_object(frame, {"bbox": bbox})
            img_hash = get_image_hash(cropped)

            found = False
            for existing_hash, obj_id in self.hash_to_id.items():
                if abs(img_hash - existing_hash) <= 5:
                    new_id_to_bbox[obj_id] = bbox
                    found = True
                    break

            if not found:
                obj_id = self.next_id
                self.hash_to_id[img_hash] = obj_id
                new_id_to_bbox[obj_id] = bbox
                self.next_id += 1

        self.id_to_bbox = new_id_to_bbox
        self.update()

    def paintEvent(self, event):
        if not self.id_to_bbox:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for obj_id, bbox in self.id_to_bbox.items():
            x1, y1, x2, y2 = bbox
            painter.setPen(QPen(QColor(255, 0, 0), 2))
            painter.drawRect(x1, y1, x2 - x1, y2 - y1)
            painter.setFont(QFont("Arial", 14, QFont.Bold))
            painter.setPen(QColor(255, 0, 0))
            painter.drawText(x1 + 5, y1 - 10, f"No.{obj_id + 1}")

    def start_voice_thread(self):
        self.voice_thread = threading.Thread(target=self.voice_loop, daemon=True)
        self.voice_thread.start()

    def voice_loop(self):
        speak("제품 번호를 말씀해 주세요.")
        while self.running:
            try:
                command = listen_for_command()
                # command = '열번째 제품 확인해줘'
                result = interpret_command(command)

                if result["action"] == "number":
                    self.handle_number(result["number"])
                    break
                elif result["action"] == "exit":
                    speak("인식을 종료합니다.")
                    self.shutdown()
                    break
                elif result["action"] == "wakeword":
                    speak("이미 인식 중입니다. 번호를 말씀해 주세요.")
                elif result["action"] == "False":
                    continue
                else:
                    speak("잘 이해하지 못했어요. 다시 말씀해 주세요.")
            except Exception as e:
                print(f"[음성 루프 오류] {e}")
                continue

    def handle_number(self, index):
        if index not in self.id_to_bbox:
            speak("잘못된 번호입니다.")
            return

        try:
            speak(f"{index + 1}번 제품을 검색할게요.")
            bbox = self.id_to_bbox[index]
            cropped = crop_object(self.last_frame, {"bbox": bbox})
            clip_label = predict_label(cropped)
            product_name = generate_product_name(cropped, clip_label)
            url = search_naver_shopping(product_name)

            if url:
                print(f"[검색 결과] {url}")
                speak("제품 판매 페이지를 열어드릴게요.")
                webbrowser.open(url)
            else:
                speak("검색 결과가 없습니다.")
        except Exception as e:
            print(f"[handle_number 오류] {e}")
            speak("검색 중 오류가 발생했어요.")
        finally:
            self.shutdown()

    def shutdown(self):
        self.running = False
        self.timer.stop()
        self.hash_to_id.clear()
        self.id_to_bbox.clear()
        self.next_id = 0
        self.hide()
        self.close()
        QApplication.quit()
