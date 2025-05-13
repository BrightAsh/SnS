import time
import webbrowser

from voice.listener import listen_for_command
from gpt.commands import interpret_command  # ✅ GPT 기반 명령 해석기로 교체
from screen.capture import capture_screen
from detection.model_loader import load_model
from detection.detector import detect_objects
from detection.visualizer import show_detected_image
from search.cropper import crop_object
from embedding.clip_text_predictor import predict_label
from gpt.product_name_generator import generate_product_name
from search.naver_api import search_naver_shopping
from utils.tts import speak

def run():

    model = load_model()

    while True:
        flag = False
        speak('필요하실 때, 챗봇이라고 불러주세요')
        try:
            command = listen_for_command()
            #command = '안녕 챗봇'
            result = interpret_command(command)

            if result["action"] == "wakeword":
                speak("네, 무엇을 도와드릴까요?")

                while True:
                    command = listen_for_command(timeout=10)
                    # command = '제품 인식해줘'
                    result = interpret_command(command)
                    if result["action"] == "trigger":
                        speak("제품 인식을 시작합니다.")
                        last_image = capture_screen()
                        detected_objects = detect_objects(model, last_image)
                        if not detected_objects:
                            speak("인식된 제품이 없어요.")
                            continue
                        while True:
                            result = show_detected_image(last_image, detected_objects)
                            if result["action"] == "number":
                                object_idx = result["number"]
                                if object_idx is not None and 0 <= object_idx < len(detected_objects):
                                    print(f"[명령 감지] {object_idx + 1}번 객체 검색 요청")
                                    cropped = crop_object(last_image, detected_objects[object_idx])
                                    clip_label = predict_label(cropped)
                                    product_name = generate_product_name(cropped, clip_label)
                                    url = search_naver_shopping(product_name)
                                    if url:
                                        print(f"[검색 결과] {url}")
                                        speak("제품 판매 페이지를 열어드릴께요")
                                        webbrowser.open(url)
                                        flag = True
                                        break
                                    else:
                                        print("[검색 실패] 결과 없음")
                                        speak("검색 결과가 없습니다.")
                                        flag = True
                                        break
                            elif result["action"] == "exit":
                                print("[명령 감지] 객체 인식 종료 명령")
                                flag = True
                                break
                            else:
                                speak("제품 번호를 다시 말씀해주세요")
                        if flag:
                            break
                    elif result["action"] == "exit":
                        print("[명령 감지] 객체 인식 종료 명령")
                        break
                    else:
                        speak("알 수 없는 명령입니다. 다시 말씀해주세요.")
            else:
                print(f"[대기 중] '챗봇' 호출 대기...({command}라고 말함)")

        except KeyboardInterrupt:
            print("\n[종료] SnS 시스템 종료됨.")
            break
        except Exception as e:
            print(f"[오류] {e}")
            time.sleep(1)


if __name__ == "__main__":
    run()