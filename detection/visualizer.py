# visualizer.py
# detection/visualizer.py

import cv2

def show_detected_image(image, detections):
    """
    탐지된 객체를 이미지에 표시하고 창으로 출력
    :param image: 원본 이미지 (OpenCV BGR)
    :param detections: 탐지 결과 리스트 (bbox, class_id, confidence 포함)
    """
    print("[시각화] 탐지 결과를 이미지에 표시합니다...")

    display_image = image.copy()

    for idx, det in enumerate(detections):
        x1, y1, x2, y2 = det["bbox"]
        label = f"{idx+1}번"

        # 바운딩 박스
        cv2.rectangle(display_image, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # 번호 라벨
        cv2.putText(display_image, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cv2.imshow("탐지 결과", display_image)
    cv2.waitKey(0)  # 창을 수동으로 닫을 때까지 대기


if __name__ == "__main__":
    from screen.capture import capture_screen
    from detection.model_loader import load_model
    from detection.detector import detect_objects

    img = capture_screen()
    model = load_model()
    results = detect_objects(model, img)
    show_detected_image(img, results)
