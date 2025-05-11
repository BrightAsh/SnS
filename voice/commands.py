# commands.py
# voice/commands.py
from utils.helpers import extract_object_number
import re

# 🔑 "챗봇" 호출 여부
def is_wakeword(command: str) -> bool:
    if not command:
        return False
    return "챗봇" in command

# 🟢 객체 탐지 트리거 명령
def is_trigger_command(command: str) -> bool:
    if not command:
        return False
    trigger_keywords = ["제품 인식", "제품 인식해줘", "이거 뭐야", "보여줘"]
    return any(keyword in command for keyword in trigger_keywords)

# 🔴 탐지 종료 명령
def is_exit_command(command: str) -> bool:
    if not command:
        return False
    exit_keywords = ["그만", "닫아", "꺼줘", "종료"]
    return any(keyword in command for keyword in exit_keywords)

# 🔢 객체 번호 요청 파싱
def parse_command(command: str) -> dict:
    """
    명령어에서 동작 유형과 번호 등 추출
    """
    result = {"action": None, "number": None}

    number = extract_object_number(command)
    if number is not None:
        result["action"] = "search"
        result["number"] = number
    elif is_trigger_command(command):
        result["action"] = "trigger"
    elif is_exit_command(command):
        result["action"] = "exit"

    return result

# 🧠 숫자 추출 (utils.helpers 에도 중복 존재 예정)
def extract_object_number(command: str) -> int or None:
    match = re.search(r'(\d+)\s*번', command)
    if match:
        return int(match.group(1)) - 1  # 객체 인덱스는 0부터
    return None


if __name__ == "__main__":
    test = [
        "챗봇",
        "제품 인식해줘",
        "3번 제품 보여줘",
        "그만 꺼줘",
    ]
    for cmd in test:
        print(cmd, "→", parse_command(cmd))
