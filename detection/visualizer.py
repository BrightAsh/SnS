import time
import cv2
from utils.tts import speak
from voice.listener import listen_for_command
from gpt.commands import interpret_command

def show_detected_image(image, detections):
    """
    탐지된 객체를 이미지에 표시하고 창으로 출력
    :param image: 원본 이미지 (OpenCV BGR)
    :param detections: 탐지 결과 리스트 (bbox, class_id, confidence 포함)
    """
    print("[시각화] 탐지 결과를 이미지에 표시합니다...")

    for i, obj in enumerate(detections):
        print(f"[객체 {i + 1}] {obj}")

    display_image = image.copy()

    for idx, det in enumerate(detections):
        x1, y1, x2, y2 = det["bbox"]
        label = f"No.{idx + 1}"  # ✅ 한글 제거, 영어로

        # 빨간색 바운딩 박스
        cv2.rectangle(display_image, (x1, y1), (x2, y2), (0, 0, 255), 2)

        # 텍스트 중앙 상단 위치 계산
        text_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)
        text_width = text_size[0]
        label_x = x1 + (x2 - x1) // 2 - text_width // 2
        label_y = y1 - 10

        # 텍스트 출력 (빨간색)
        cv2.putText(display_image, label, (label_x, label_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    # 이미지 창 띄우기
    cv2.imshow("탐지 결과", display_image)
    cv2.waitKey(1)  # 바로 코드 진행
    speak(f'1번부터 {len(detections)}번 제품 중 무엇을 확인할까요?')
    n_obj = listen_for_command()
    result = interpret_command(n_obj)
    cv2.destroyAllWindows()
    return result


if __name__ == "__main__":
    from screen.capture import capture_screen
    from detection.model_loader import load_model
    from detection.detector import detect_objects

    img = capture_screen()
    model = load_model()
    results = detect_objects(model, img)
    show_detected_image(img, results)
