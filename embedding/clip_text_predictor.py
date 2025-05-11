# embedding/clip_text_predictor.py

import torch
import open_clip
import cv2
from PIL import Image
import torchvision.transforms as T

# COCO-like 텍스트 라벨 후보 리스트
CANDIDATE_LABELS = [
    "backpack", "handbag", "suitcase", "laptop", "cell phone", "bottle",
    "shoes", "tv", "chair", "refrigerator", "keyboard", "microwave",
    "oven", "remote", "book", "teddy bear", "hair drier"
]

# 디바이스 설정
device = "cuda" if torch.cuda.is_available() else "cpu"

# CLIP 모델 로딩 (laion2b 사전학습)
model, _, preprocess = open_clip.create_model_and_transforms(
    'ViT-B-32', pretrained='laion2b_s34b_b79k'
)
tokenizer = open_clip.get_tokenizer('ViT-B-32')
model = model.to(device).eval()

def predict_label(image_bgr):
    """
    crop된 OpenCV 이미지 (BGR)를 받아 CLIP 기반 텍스트 라벨 추론
    :param image_bgr: OpenCV BGR 이미지
    :return: 가장 유사한 텍스트 라벨 (예: 'backpack')
    """
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    image_pil = Image.fromarray(image_rgb)
    image_tensor = preprocess(image_pil).unsqueeze(0).to(device)

    with torch.no_grad():
        image_features = model.encode_image(image_tensor)
        text_tokens = tokenizer(CANDIDATE_LABELS).to(device)
        text_features = model.encode_text(text_tokens)

        # 유사도 계산 → 소프트맥스 확률
        logits = image_features @ text_features.T
        probs = logits.softmax(dim=-1).cpu().numpy()[0]

        top_index = probs.argmax()
        return CANDIDATE_LABELS[top_index]


if __name__=='__main__':
    # test_clip_predictor.py

    import cv2
    from screen.capture import capture_screen
    from detection.model_loader import load_model
    from detection.detector import detect_objects
    from search.cropper import crop_object
    from embedding.clip_text_predictor import predict_label
    img = capture_screen()
    model = load_model()
    detections = detect_objects(model, img)

    if not detections:
        print("❌ 객체 탐지 실패")
        exit()

    cropped = crop_object(img, detections[0])
    label = predict_label(cropped)

    print(f"📌 CLIP 예측 결과: {label}")
    cv2.imshow("Cropped Object", cropped)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

