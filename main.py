import time
import webbrowser

from voice.listener import listen_for_command
from voice.commands import (
    is_wakeword,
    is_trigger_command,
    is_exit_command,
    parse_command
)
from screen.capture import capture_screen
from detection.model_loader import load_model
from detection.detector import detect_objects
from detection.visualizer import show_detected_image
from search.cropper import crop_object
from embedding.clip_text_predictor import predict_label
from gpt.product_name_generator import generate_product_name
from search.naver_api import search_naver_shopping
from utils.helpers import extract_object_number
from utils.tts import speak

def run():
    print("[SnS] 시스템을 시작합니다. '챗봇'이라고 말해주세요.")
    speak('필요하실 때, 챗봇이라고 불러주세요')
    model = load_model()

    detected_objects = []
    last_image = None

    while True:
        try:
            # 🎤 음성 명령 대기
            #command = listen_for_command()
            command = '챗봇'
            if is_wakeword(command):  # "챗봇"
                print("[Wakeword 감지] 사용자 호출: 챗봇")
                speak("네, 무엇을 도와드릴까요?")
                # 👂 명령 대기 (타임아웃: 10초)
                print("[대기] 명령을 기다리는 중...")
                #follow_up = listen_for_command(timeout=10)
                follow_up = '제품 인식'

                if not follow_up:
                    print("[대기] 명령 없음, 다시 '챗봇'을 호출해주세요.")
                    speak("시간이 초과되었어요. 필요하시면 불러주세요")
                    continue

                if is_trigger_command(follow_up):
                    print(f"[명령 감지] '{follow_up}' → 객체 인식 시작")
                    last_image = capture_screen()
                    detected_objects = detect_objects(model, last_image)
                    if len(detected_objects) == 0:
                        speak("인식된 제품이 없어요.")
                        continue
                    n_obj = show_detected_image(last_image, detected_objects)

                elif is_exit_command(follow_up):
                    print("[명령 감지] 객체 인식 종료 명령")
                    detected_objects = []
                    last_image = None
                    continue

                # 음성 명령이 '그만 꺼줘'일 경우 종료 처리
                if is_exit_command(n_obj):
                    print("[명령 감지] 객체 인식 종료 명령")
                    detected_objects = []
                    last_image = None
                    continue

                elif n_obj:
                    while True:
                        object_idx = extract_object_number(n_obj)
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
                            else:
                                print("[검색 실패] 결과 없음")
                                speak("검색에 실패했어요")
                            break
                        else:
                            speak("제품 번호를 다시 말씀해주세요")
                            break
                else:
                    print("[대기] 유효한 객체 인식 상태가 아닙니다.")
                    speak("유효한 객체가 인식되지 않았어요. 다시 시도해주세요.")
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
