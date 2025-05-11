# capture.py
# screen/capture.py

import numpy as np
import cv2
import mss

def capture_screen():
    """
    현재 전체 화면을 캡처하여 OpenCV 이미지로 반환
    :return: 화면 이미지 (numpy.ndarray, BGR 형식)
    """
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # 첫 번째 모니터 (1부터 시작)
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)

        # BGRA → BGR (OpenCV 호환)
        img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img_bgr

if __name__ == "__main__":
    img = capture_screen()
    cv2.imshow("Captured Screen", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
