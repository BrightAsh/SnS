# helpers.py
# utils/helpers.py

import re

def extract_object_number(command: str) -> int or None:
    """
    '3번 제품', '1번 보여줘' 같은 문장에서 숫자 인덱스 추출
    :param command: 음성 명령 문자열
    :return: 객체 인덱스 (0부터 시작), 없으면 None
    """
    match = re.search(r'(\d+)\s*번', command)
    if match:
        number = int(match.group(1)) - 1  # 인덱스는 0부터 시작
        return number if number >= 0 else None
    return None
if __name__ == "__main__":
    test_commands = [
        "1번 제품 보여줘",
        "3번 제품 검색",
        "그냥 보여줘",
        "0번 제품",
        "100번"
    ]

    for cmd in test_commands:
        idx = extract_object_number(cmd)
        print(f"{cmd} → {idx}")
