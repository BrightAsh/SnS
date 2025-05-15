# stream_main.py (exec_() 제거 → running 루프 기반 리팩토링)

import sys
from PyQt5.QtWidgets import QApplication

from core.gpt.commands import interpret_command, interpret_command_test
from core.voice.listener import listen_for_command
from core.utils.tts import speak
from app.LiveOverlay import LiveOverlay

app = QApplication(sys.argv)


def run():
    print("[SnS 실시간 모드] 시스템을 시작합니다. '챗봇'이라고 말해주세요.")

    while True:
        try:
            speak("필요하시면 저를 불러주세요")
            # command = listen_for_command()
            command = '안녕'
            result = interpret_command_test(command)

            if result["action"] == "wakeword":
                speak("무엇을 도와드릴까요?")
                while True:
                    # follow_up = listen_for_command()
                    follow_up = '인식'
                    result = interpret_command_test(follow_up)

                    if result["action"] == "trigger":
                        speak("제품 인식을 시작합니다.")
                        overlay = LiveOverlay()
                        overlay.show()
                        while True:
                            app.processEvents()
                            if not overlay.running or not overlay.isVisible():
                                break
                    elif result["action"] == "exit":
                        speak("종료합니다.")
                        break
                    else:
                        speak("다시 말씀해 주세요.")

            else:
                print("[대기 중] '챗봇' 호출 대기 중...")

        except KeyboardInterrupt:
            print("\n[종료] 시스템 전체 종료됨.")
            break
        except Exception as e:
            print(f"[오류] {e}")
            continue

if __name__ == "__main__":
    run()