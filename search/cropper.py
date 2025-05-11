# search/cropper.py

def crop_object(image, detection):
    """
    탐지 결과에서 지정된 객체 부분만 crop하여 반환
    :param image: 원본 이미지 (OpenCV BGR)
    :param detection: {"bbox": (x1, y1, x2, y2), ...}
    :return: crop된 이미지 (OpenCV BGR)
    """
    x1, y1, x2, y2 = detection["bbox"]

    # 이미지 경계 보호
    h, w, _ = image.shape
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)

    cropped = image[y1:y2, x1:x2].copy()
    return cropped


if __name__ == "__main__":
    from screen.capture import capture_screen
    from detection.model_loader import load_model
    from detection.detector import detect_objects
    from search.cropper import crop_object
    import cv2

    # 1. 화면 캡처
    image = capture_screen()

    # 2. 모델 로딩
    model = load_model()

    # 3. 객체 탐지
    detections = detect_objects(model, image)

    # 4. 첫 번째 객체만 crop해서 확인
    if detections:
        cropped = crop_object(image, detections[0])  # 0번 객체 (인덱스 0)
        cv2.imshow("Cropped Object", cropped)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("탐지된 객체가 없습니다.")
