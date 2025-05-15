# overlay_labels/voice_controller.py

import threading
import webbrowser
from core.utils.tts import speak
from core.gpt.commands import interpret_command, interpret_command_test
from core.search.cropper import crop_object
from core.gpt.product_identifier import  detect_product_name_from_image
from core.search.naver_api import search_naver_shopping
from core.utils.image_utils import get_image_hash
from core.utils.cache_utils import save_cache
from core.voice.listener import listen_for_command

def start_voice_thread(self):
    self.voice_thread = threading.Thread(target=lambda: voice_loop(self), daemon=True)
    self.voice_thread.start()

def voice_loop(self):
    speak("제품 번호를 말씀해 주세요.")
    while self.running:
        try:
            command = listen_for_command()
            # command = '2번 제품 보여줘'
            result = interpret_command_test(command)

            if result["action"] == "number":
                if result["number"] not in self.id_to_full_info:
                    speak("잘못된 번호입니다.다시 말해주세요")
                    continue
                handle_number(self, result["number"])
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(0, self.shutdown)
                break
            elif result["action"] == "exit":
                speak("인식을 종료합니다.")
                self.shutdown()
                break
            elif result["action"] == "wakeword":
                speak("이미 인식 중입니다. 번호를 말씀해 주세요.")
            else:
                speak("잘 이해하지 못했어요. 다시 말씀해 주세요.")
        except Exception as e:
            print(f"[음성 루프 오류] {e}")
            continue

def handle_number(self, index):
    try:
        info = self.id_to_full_info[index]
        frame = info["last_frame"]
        bbox = info["last_bbox"]
        cropped = crop_object(frame, {"bbox": bbox})

        img_hash = str(get_image_hash(cropped))

        if img_hash in self.imagehash_to_url:
            url = self.imagehash_to_url[img_hash]
            print(f"[CACHE HIT] {url}")

        else:
            product_name = detect_product_name_from_image(cropped)
            print(product_name)
            if product_name in ['Unknown.', 'Unknown']:
                speak("제품명을 찾지 못 했어요. 인식을 종료합니다.")
                return
            url = search_naver_shopping(product_name)

            if url:
                print(f"[CACHE MISS] {url}")
                self.imagehash_to_url[img_hash] = url
                save_cache(self.imagehash_to_url)

            else:
                speak("검색 결과가 없습니다.")
                return

        speak("제품 판매 페이지를 열어드릴게요.")
        threading.Thread(target=webbrowser.open, args=(url,), daemon=True).start()

    except Exception as e:
        print(f"[handle_number 오류] {e}")
        speak("검색 중 오류가 발생했어요.")
