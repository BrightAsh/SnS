# listener.py
# voice/listener.py

import speech_recognition as sr

recognizer = sr.Recognizer()
microphone = sr.Microphone()

def listen_for_command(timeout=None):
    """
    마이크로부터 음성 명령을 수신하고 텍스트로 변환
    :param timeout: 초 단위 대기 시간. None이면 무한 대기
    :return: 인식된 음성 텍스트 (소문자), 실패시 빈 문자열
    """
    with microphone as source:
        if timeout:
            print(f"[음성 대기] {timeout}초 동안 명령을 기다립니다...")
        else:
            print("[음성 대기] 명령을 기다리는 중...")

        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=timeout)
            command = recognizer.recognize_google(audio, language="ko-KR")
            print(f"[인식 성공] '{command}'")
            return command.lower()
        except sr.WaitTimeoutError:
            print("[음성 대기 종료] 시간 초과")
            return ""
        except sr.UnknownValueError:
            print("[인식 실패] 음성 내용을 이해할 수 없음")
            return ""
        except sr.RequestError as e:
            print(f"[오류] STT 서비스 오류: {e}")
            return ""


if __name__ == "__main__":
    while True:
        cmd = listen_for_command()
        print("👉", cmd)
