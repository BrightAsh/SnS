import sys
import signal
from PyQt5.QtWidgets import QApplication

from voice.listener import listen_for_command
from gpt.commands import interpret_command
from utils.tts import speak
from overlay_labels.LiveOverlay import LiveOverlay

app = QApplication(sys.argv)  # 루프 밖, run() 함수 맨 위에 선언

def run():
    print("[SnS 실시간 모드] 시스템을 시작합니다. '챗봇'이라고 말해주세요.")

    while True:
        try:
            speak("필요하시면 챗봇이라고 불러주세요")
            # command = listen_for_command()
            command = '안녕 챗봇'
            result = interpret_command(command)
            while True:
                if result["action"] == "wakeword":
                    speak("무엇을 도와드릴까요?")
                    # follow_up = listen_for_command()
                    follow_up = '화면에 있는 제품들 인식해줘'
                    result = interpret_command(follow_up)

                    if result["action"] == "trigger":
                        speak("제품 인식을 시작합니다.")
                        overlay = LiveOverlay()
                        overlay.show()
                        app.exec_()
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
