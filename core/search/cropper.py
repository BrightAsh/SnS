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
