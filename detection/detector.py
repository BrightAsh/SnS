# detector.py
# detection/detector.py

def detect_objects(model, image):
    """
    이미지에서 객체를 탐지하고 결과 리스트 반환
    :param model: 로딩된 YOLO 모델
    :param image: BGR 이미지 (OpenCV)
    :return: 탐지된 객체 리스트 [ {bbox, class_id, conf}, ... ]
    """
    # print("[객체 탐지] 실행 중...")
    results = model.predict(source=image, conf=0.4, verbose=False)

    detections = []
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])      # 바운딩 박스 좌표
            class_id = int(box.cls[0])                  # 클래스 인덱스
            conf = float(box.conf[0])                   # 신뢰도
            detections.append({
                "bbox": (x1, y1, x2, y2),
                "class_id": class_id,
                "confidence": conf
            })
    # print(f"[객체 탐지 완료] {len(detections)}개 객체")
    return detections


if __name__ == "__main__":
    from screen.capture import capture_screen
    from detection.model_loader import load_model
    from detection.detector import detect_objects

    img = capture_screen()
    model = load_model()
    results = detect_objects(model, img)
    print(results)
