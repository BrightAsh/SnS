import base64
import tempfile
import cv2
from openai import OpenAI
from config.settings import VISION_CLIENT, OPENAI_API_KEY
from google.cloud import vision

client = OpenAI(api_key=OPENAI_API_KEY)

def detect_product_name_from_image(image_bgr):
    """
    BGR 이미지(OpenCV)를 받아 Vision API + GPT-4o로 제품명을 추론
    """

    # 1. Vision API 호출
    _, tmp_path = tempfile.mkstemp(suffix=".jpg")
    cv2.imwrite(tmp_path, image_bgr)
    with open(tmp_path, "rb") as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = VISION_CLIENT.web_detection(image=image)

    if response.error.message:
        raise Exception(f"Vision API Error: {response.error.message}")

    # 2. web_entities 추출
    entities = [e.description for e in response.web_detection.web_entities if e.score > 0.5 and e.description]
    entity_text = ", ".join(entities)

    # 3. 이미지 base64 인코딩
    image_base64 = base64.b64encode(content).decode("utf-8")

    # 4. GPT-4o에 이미지 + 키워드 함께 전달
    gpt_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI that identifies product names from an image and a keyword list."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "This is a product image. Below are the keywords extracted by an image recognition system:\n\n"
                            f"{entity_text}\n\n"
                            "Using both the image and the keyword list, determine the exact product name.\n"
                            "Return ONLY the product name (e.g., 'Nike Air Max 97').\n"
                            "If you're unsure, return: Unknown. Do not explain."
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
        max_tokens=100,
        temperature=0.2
    )

    return gpt_response.choices[0].message.content.strip()

if __name__ == '__main__':
    import cv2

    image_path = './assets/test_image_1.jpg'
    image_bgr = cv2.imread(image_path)

    if image_bgr is None:
        print("❌ 이미지 로딩 실패: 경로 확인 필요")
        exit()

    product_name = detect_product_name_from_image(image_bgr)
    print(f"🧠 최종 추론된 제품명: {product_name}")
