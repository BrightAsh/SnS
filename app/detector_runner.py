# overlay_labels/detector_runner.py
import cv2
import numpy as np
import mss
from core.search.cropper import crop_object
from core.utils.image_utils import get_image_hash
from core.detection.detector import detect_objects
from config.settings import EXCLUDE_CLASSES


def update_detections(self):
    self.hide()
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    self.show()

    self.last_frame = frame
    self.raw_detections = detect_objects(self.model, frame)

    new_id_to_bbox = {}
    current_hashes = set()

    self.raw_detections = [
        det for det in self.raw_detections if self.model.names[det["class_id"]] not in EXCLUDE_CLASSES
    ]

    self.raw_detections = sorted(
        self.raw_detections,
        key=lambda det: (det["bbox"][1] // 100, det["bbox"][0])  # (y1 // 100, x1)
    )

    for det in self.raw_detections:
        bbox = det["bbox"]
        cropped = crop_object(frame, {"bbox": bbox})
        img_hash = get_image_hash(cropped)
        current_hashes.add(img_hash)

        found = False
        for existing_hash, obj_id in self.hash_to_id.items():
            if abs(img_hash - existing_hash) <= 5:
                new_id_to_bbox[obj_id] = bbox
                self.id_to_full_info[obj_id] = {
                    "last_bbox": bbox,
                    "last_frame": frame,
                    "hash": img_hash,
                    "active": True
                }
                found = True
                break

        if not found:
            obj_id = self.next_id
            self.hash_to_id[img_hash] = obj_id
            new_id_to_bbox[obj_id] = bbox
            self.id_to_full_info[obj_id] = {
                "last_bbox": bbox,
                "last_frame": frame,
                "hash": img_hash,
                "active": True
            }
            self.next_id += 1

    self.id_to_bbox = new_id_to_bbox

    for obj_id in self.id_to_full_info:
        if obj_id not in self.id_to_bbox:
            self.id_to_full_info[obj_id]["active"] = False

    self.update()
