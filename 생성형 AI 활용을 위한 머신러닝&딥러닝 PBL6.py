import os
import json
import re
from datetime import datetime
from typing import Any, Dict, Callable

from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# -----------------------------
# 1) 사용자 정의 함수 2개
# -----------------------------
def _normalize_dt_format(fmt: str) -> str:
    """
    모델이 YYYY/MM/DD 같은 표기를 주는 경우가 있어, 파이썬 strptime/strftime 형식으로 보정.
    이미 %Y 같은 형태면 그대로 사용.
    """
    if "%" in fmt:
        return fmt

    # 흔한 토큰을 strptime 포맷으로 치환
    # (대문자 기준) YYYY MM DD HH mm ss
    mapping = {
        "YYYY": "%Y",
        "YY": "%y",
        "MM": "%m",
        "DD": "%d",
        "HH": "%H",
        "hh": "%H",
        "mm": "%M",  # minutes
        "ss": "%S",
    }

    out = fmt
    # 긴 토큰부터 치환
    for k in sorted(mapping.keys(), key=len, reverse=True):
        out = out.replace(k, mapping[k])
    return out

# 날짜 문자열을 current_format에서 target_format으로 변환
def convert_date_format(date_str: str, current_format: str, target_format: str) -> str:
    cur = _normalize_dt_format(current_format)
    tgt = _normalize_dt_format(target_format)

    # 공백/불필요 문자 정리
    s = date_str.strip()

    # 1) 지정 포맷으로 우선 파싱
    try:
        dt = datetime.strptime(s, cur)
        return dt.strftime(tgt)
    except ValueError:
        pass

    # 2) 흔한 입력 포맷들로 보조 파싱 (모델이 포맷을 조금 틀리게 줄 때 대비)
    candidates = ["%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%Y%m%d"]
    for c in candidates:
        try:
            dt = datetime.strptime(s, c)
            return dt.strftime(tgt)
        except ValueError:
            continue

    raise ValueError(f"날짜 파싱 실패: date_str={date_str}, current_format={current_format}")

# 두 숫자 더하기 함수
def add_numbers(x: float, y: float) -> float:
    return float(x) + float(y)


# -----------------------------
# 2) OpenAIAgent 클래스
# -----------------------------
class OpenAIAgent:
    def __init__(self, model: str | None = None):
        # API Key는 하드코딩 금지: 환경변수 OPENAI_API_KEY로 주입
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = "gpt-5.2" if model is None else model

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "convert_date_format",
                    "description": (
                        "날짜 문자열(date_str)을 current_format에서 target_format으로 변환한다. "
                        "format은 Python datetime의 strptime/strftime 규칙(%Y, %m, %d 등)을 사용하거나 "
                        "YYYY-MM-DD 같은 표기도 가능하다."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date_str": {"type": "string", "description": "변환할 날짜 문자열"},
                            "current_format": {"type": "string", "description": "현재 날짜 포맷"},
                            "target_format": {"type": "string", "description": "변환할 목표 포맷"},
                        },
                        "required": ["date_str", "current_format", "target_format"],
                        "additionalProperties": False,
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "add_numbers",
                    "description": "두 숫자 x, y를 더한 값을 반환한다.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "number", "description": "첫 번째 숫자"},
                            "y": {"type": "number", "description": "두 번째 숫자"},
                        },
                        "required": ["x", "y"],
                        "additionalProperties": False,
                    },
                },
            },
        ]

        self.tool_router: Dict[str, Callable[..., Any]] = {
            "convert_date_format": convert_date_format,
            "add_numbers": add_numbers,
        }


    def call_openai(self, messages: list[dict]) -> Any:
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools,
            tool_choice="auto",
        )

    def handle_tool_calls(self, messages: list[dict], tool_calls: list[Any]) -> None:
        # assistant의 tool_calls 메시지 추가
        assistant_tool_msg = {
            "role": "assistant",
            "content": "",
            "tool_calls": [],
        }

        for tc in tool_calls:
            assistant_tool_msg["tool_calls"].append(
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
            )

        messages.append(assistant_tool_msg)

        # 각 tool_call 실행 후 role=tool 메시지로 결과 추가
        for tc in tool_calls:
            fn_name = tc.function.name
            raw_args = tc.function.arguments

            try:
                args = json.loads(raw_args) if isinstance(raw_args, str) else dict(raw_args)
            except Exception:
                # 모델이 JSON을 약간 깨뜨렸을 때 최소 복구
                args = json.loads(re.sub(r"(\w+):", r'"\1":', raw_args))

            fn = self.tool_router.get(fn_name)
            if fn is None:
                result = f"Unknown function: {fn_name}"
            else:
                try:
                    out = fn(**args)
                    result = str(out)
                except Exception as e:
                    result = f"Function error in {fn_name}: {e}"

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                }
            )

    def chat(self, user_text: str) -> str:
        messages = [
            {"role": "user", "content": user_text}
        ]

        # tool_calls가 사라질 때까지 최대 N회 반복
        for _ in range(5):
            resp = self.call_openai(messages)
            msg = resp.choices[0].message

            tool_calls = getattr(msg, "tool_calls", None)
            if tool_calls:
                self.handle_tool_calls(messages, tool_calls)
                continue

            return (msg.content or "").strip()

        return "요청 처리가 반복 한도를 초과했습니다."


# -----------------------------
# 3) 간단 테스트
# -----------------------------
if __name__ == "__main__":
    agent = OpenAIAgent()

    # tests = [
    #     "2024-12-25을 2024년 12월 25일 형식으로 바꿔줘",
    #     "23.5와 3.1을 더하면 얼마야?",
    # ]

    # for t in tests:
    #     print(f"\n[User] {t}")
    #     print(f"[Agent] {agent.chat(t)}")
    
    # (선택) 대화형
    print("대화형 모드 (종료하려면 'exit' 또는 'quit' 입력)")
    while True:
        q = input("\nUser> ").strip()
        if q.lower() in ("exit", "quit"):
            break
        print("Agent>", agent.chat(q))
