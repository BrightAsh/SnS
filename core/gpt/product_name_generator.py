from openai import OpenAI
from config.settings import OPENAI_API_KEY
import tempfile
import base64
import cv2

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_product_name(image_bgr) -> str:
    """
    GPT-4o API를 이용해 이미지 단독으로 제품명을 추론
    """
    # 이미지 → 임시 저장 → base64 변환
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
                "content": "You are an AI that helps identify real-world consumer products based on image input."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Identify the product in the image. "
                            "Respond ONLY with the exact product name (e.g., 'Apple AirPods Pro 2', 'Nike Air Max 270'). "
                            "If the image is unclear or the product cannot be confidently identified, respond with: Unknown. "
                            "Do NOT explain anything. Do NOT guess."
                        )
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

    # os.remove(tmp_path)  # ❗️필요 시 임시 이미지 삭제
    return response.choices[0].message.content.strip()

if __name__ == '__main__':
    import cv2
    from core.gpt.product_name_generator import generate_product_name

    image_path = "/assets/test_image_2.jpg"
    cropped = cv2.imread(image_path)

    if cropped is None:
        print("❌ 이미지 로딩 실패. 경로 확인 필요.")
        exit()

    product_name = generate_product_name(cropped)
    print(f"🧠 GPT-4o 추론 제품명: {product_name}")

    # # 시각화 (optional)
    # cv2.imshow("Crop 테스트 이미지", cropped)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
