# gpt/product_name_generator.py

from openai import OpenAI
from config.settings import OPENAI_API_KEY
import tempfile
import base64
import cv2  # ❗️필수: OpenCV로 이미지 저장
import os   # ❗️필수: 임시 파일 정리 시 필요 (optional)

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_product_name(image_bgr, clip_label: str) -> str:
    """
    GPT API로 제품명 추론 (이미지 + CLIP 라벨 사용)
    """
    # 이미지 파일로 임시 저장
    _, tmp_path = tempfile.mkstemp(suffix=".jpg")
    cv2.imwrite(tmp_path, image_bgr)

    with open(tmp_path, "rb") as f:
        image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are an AI that helps identify consumer products from images."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"The object is a '{clip_label}'. Please respond with only the most accurate and concise product name or model. Do not include any explanations or descriptions. Just return the product name only."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=100
    )

    # os.remove(tmp_path)  # ❗️원한다면 임시 파일 삭제
    return response.choices[0].message.content.strip()


if __name__ == '__main__':
    import cv2
    from embedding.clip_text_predictor import predict_label
    from gpt.product_name_generator import generate_product_name

    # 1. crop된 이미지 파일 경로
    image_path = "D:/Lecture/CV/SnS/assets/test_image_2.jpg"
    cropped = cv2.imread(image_path)

    if cropped is None:
        print("❌ 이미지 로딩 실패. 경로 확인 필요.")
        exit()

    # 2. CLIP으로 텍스트 라벨 추론
    clip_label = predict_label(cropped)
    print(f"🔍 CLIP 라벨: {clip_label}")

    # 3. GPT API로 제품명 추론
    product_name = generate_product_name(cropped, clip_label)
    print(f"🧠 GPT 추론 제품명: {product_name}")

    # # 4. 시각화
    # cv2.imshow("Crop 테스트 이미지", cropped)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
