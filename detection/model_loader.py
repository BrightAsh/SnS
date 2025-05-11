# detection/model_loader.py

from ultralytics import YOLO
from config.settings import YOLO_MODEL_PATH, DEVICE

def load_model():
    """
    YOLO 모델 로드 (yolov5s.pt 또는 yolov8n.pt)
    """
    print(f"[모델 로딩] '{YOLO_MODEL_PATH}' 로드 중...")
    try:
        model = YOLO(YOLO_MODEL_PATH)
        model.to(DEVICE)
        print(f"[모델 로딩 완료] 디바이스: {DEVICE}")
        return model
    except Exception as e:
        print(f"[오류] 모델 로딩 실패: {e}")
        raise e

if __name__ == "__main__":
    model = load_model()
