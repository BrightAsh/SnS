# overlay_labels/draw.py
from PyQt5.QtGui import QPainter, QPen, QColor, QFont

def draw_objects(self, event):
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
