# utils/tts.py

import pyttsx3

# TTS 엔진 초기화
engine = pyttsx3.init()
engine.setProperty("rate", 160)  # 음성 속도 조절
engine.setProperty("volume", 1.0)

def speak(text):
    """
    텍스트를 음성으로 출력
    :param text: 말할 텍스트
    """
    print(f"[TTS] ▶ '{text}'")
    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    speak("네, 무엇을 도와드릴까요?")
