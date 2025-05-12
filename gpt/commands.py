from openai import OpenAI
import json
from config.settings import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def interpret_command(command: str) -> dict:
    """
    GPT를 사용해 명령을 해석하고, 'action'과 'number'를 JSON 형태로 정확히 반환합니다.
    """
    prompt = f"""
다음 사용자 명령어를 분석하여 아래 형식의 JSON으로 응답하세요.

가능한 action 값은 다음 네 가지입니다:
- "wakeword": 챗봇 호출
- "trigger": 제품 인식/탐지 요청
- "exit": 종료 요청
- "number": 제품 번호 요청 (예: "3번 보여줘")

응답 형식 (JSON):
{{
  "action": "number",       ← 또는 wakeword, trigger, exit
  "number": 3               ← 숫자 명령일 때만 포함.  (예: "3번" → 3)
}}

다음은 사용자 명령어입니다:
"{command}"

JSON으로만 응답하세요.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=50,
        temperature=0
    )

    raw_reply = response.choices[0].message.content.strip()

    try:
        result = json.loads(raw_reply)
        if result.get("action") == "number" and isinstance(result.get("number"), int):
            result["number"] = max(0, result["number"] - 1)  # 0부터 시작하도록 조정
        return result
    except json.JSONDecodeError:
        return {"action": "False", "number": None}
