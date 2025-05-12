import openai
from voice.listener import listen_for_command
from utils.tts import speak
from detection.model_loader import load_model
from detection.detector import detect_objects
from search.naver_api import search_naver_shopping
from utils.helpers import extract_object_number
from embedding.clip_text_predictor import predict_label
from gpt.product_name_generator import generate_product_name

# GPT API 키 설정
openai.api_key = "YOUR_OPENAI_API_KEY"

class AI_Agent:
    def __init__(self):
        self.model = load_model()
        self.detected_objects = []
        self.last_image = None

    def listen_for_command(self):
        command = listen_for_command()
        return command

    def interpret_command(self, command):
        """
        GPT로 명령어를 해석하여, 명령의 의미를 추출하고 툴을 선택합니다.
        """
        prompt = f"사용자 명령: '{command}'. 이 명령을 이해하고, 실행할 툴을 선택해 주세요. 예를 들어, '객체 탐지', '제품 검색' 등."
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=60
        )
        interpreted_command = response.choices[0].text.strip()
        return interpreted_command

    def execute_tool(self, interpreted_command):
        """
        해석된 명령에 맞는 툴을 실행합니다.
        """
        if interpreted_command == "제품 인식":
            return self.trigger_object_detection()
        elif interpreted_command == "제품 검색":
            return self.search_product()
        else:
            speak("알 수 없는 명령입니다. 다시 시도해주세요.")
            return None

    def trigger_object_detection(self):
        """
        객체 탐지 실행
        """
        print(f"[명령 감지] 객체 인식 시작")
        self.last_image = capture_screen()
        self.detected_objects = detect_objects(self.model, self.last_image)
        speak("몇 번 제품을 확인할까요?")
        return self.process_user_selection()

    def process_user_selection(self):
        """
        사용자가 선택한 객체 번호를 처리하고, 검색 결과를 보여줍니다.
        """
        n_obj = listen_for_command()

        if n_obj:
            object_idx = extract_object_number(n_obj)
            if object_idx is not None and 0 <= object_idx < len(self.detected_objects):
                cropped = crop_object(self.last_image, self.detected_objects[object_idx])
                clip_label = predict_label(cropped)
                product_name = generate_product_name(cropped, clip_label)
                url = search_naver_shopping(product_name)
                if url:
                    speak("제품 판매 페이지를 열어드리겠습니다.")
                    webbrowser.open(url)
                else:
                    speak("검색 결과가 없습니다.")
            else:
                speak("유효한 제품 번호를 말해주세요.")
        return None

    def search_product(self):
        """
        제품 검색 실행
        """
        speak("어떤 제품을 찾고 싶으신가요?")
        product_name = listen_for_command()
        url = search_naver_shopping(product_name)
        if url:
            speak("제품 판매 페이지를 열어드리겠습니다.")
            webbrowser.open(url)
        else:
            speak("검색 결과가 없습니다.")

def run():
    agent = AI_Agent()

    while True:
        # 🎤 명령 대기
        command = agent.listen_for_command()

        # 명령 해석 및 실행
        interpreted_command = agent.interpret_command(command)
        agent.execute_tool(interpreted_command)

if __name__ == "__main__":
    run()
