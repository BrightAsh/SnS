# main.py

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

# 전역 상태
detected_objects = []
last_image = None
model = None

def run():
    global detected_objects, last_image, model
    print("[SnS] 시스템을 시작합니다. '챗봇'이라고 말해주세요.")

    model = load_model()

    while True:
        try:
            # 🎤 항상 음성 감지
            command = listen_for_command()

            if is_wakeword(command):  # "챗봇"
                print("[Wakeword 감지] 사용자 호출: 챗봇")
                speak("네, 무엇을 도와드릴까요?")

                # 👂 5초간 명령 대기
                print("[대기] 명령을 기다리는 중...")
                follow_up = listen_for_command(timeout=5)

                if is_trigger_command(follow_up):
                    print(f"[명령 감지] '{follow_up}' → 객체 인식 시작")
                    last_image = capture_screen()
                    detected_objects = detect_objects(model, last_image)
                    show_detected_image(last_image, detected_objects)

                elif is_exit_command(follow_up):
                    print("[명령 감지] 객체 인식 종료 명령")
                    detected_objects = []
                    last_image = None

                elif detected_objects:
                    object_idx = extract_object_number(follow_up)
                    if object_idx is not None and 0 <= object_idx < len(detected_objects):
                        print(f"[명령 감지] {object_idx}번 객체 검색 요청")
                        cropped = crop_object(last_image, detected_objects[object_idx])
                        clip_label = predict_label(cropped)
                        product_name = generate_product_name(cropped, clip_label)
                        url = search_naver_shopping(product_name)
                        if url:
                            print(f"[검색 결과] {url}")
                            webbrowser.open(url)
                        else:
                            print("[검색 실패] 결과 없음")
                    else:
                        print("[입력 오류] 올바른 번호를 말해주세요.")
                else:
                    print("[대기] 유효한 객체 인식 상태가 아닙니다.")

            else:
                print("[대기 중] '챗봇' 호출 대기...")

        except KeyboardInterrupt:
            print("\n[종료] SnS 시스템 종료됨.")
            break
        except Exception as e:
            print(f"[오류] {e}")
            time.sleep(1)

if __name__ == "__main__":
    run()
