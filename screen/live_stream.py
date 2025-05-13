import cv2
import mss
import numpy as np
from detection.model_loader import load_model
from detection.detector import detect_objects


def stream_and_detect():
    print("[시작] 실시간 화면 캡처 및 객체 탐지")

    model = load_model()

    with mss.mss() as sct:
        monitor = sct.monitors[1]  # 첫 번째 모니터 전체 캡처

        while True:
            screenshot = sct.grab(monitor)
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            # 객체 탐지
            detections = detect_objects(model, frame)

            # 탐지된 객체 바운딩 박스 그리기
            for det in detections:
                x1, y1, x2, y2 = det["bbox"]
                label = f"{det['class_id']} ({det['confidence']:.2f})"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            # 화면 출력
            cv2.imshow("실시간 객체 인식", frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC키 누르면 종료
                print("[종료] ESC 입력됨")
                break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    stream_and_detect()
