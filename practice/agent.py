import json
from pathlib import Path
from typing import List
import re

from .ai_clients import ask_openai, ask_gemini

BASE = Path(__file__).resolve().parent

# ---- Load prompt + few-shot examples safely ----
def read_text_safe(path: Path) -> str:
    """Đọc file text với utf-8, bỏ qua ký tự lỗi nếu có"""
    return path.read_text(encoding="utf-8", errors="ignore")

system_prompt = read_text_safe(BASE / "prompt.txt")
few_shots = json.loads(read_text_safe(BASE / "few_shots.json"))

# ---- Chat memory ----
memory: List[dict] = []
MAX_MEMORY = 100  # tối đa 100 messages trong memory (50 exchanges)

# ---- Helper ----
def clean_reply(text: str) -> str:
    """
    Loại bỏ các dấu ****, các marker rác và chuẩn hóa khoảng trắng.
    Giữ newline tự nhiên.
    """
    # loại bỏ các cụm nhiều dấu * liền nhau
    text = re.sub(r"\*{2,}", "", text)
    # chuẩn hóa khoảng trắng, nhưng giữ newline
    text = re.sub(r"[ \t]+", " ", text)      # replace space/tab dư
    text = re.sub(r" *\n *", "\n", text)    # trim space xung quanh newline
    return text.strip()

# ---- Query agent ----
def query_agent(user_query: str, max_exchanges: int = 10) -> str:
    """
    Gửi user_query tới AI, trả về reply đã clean, giữ newline tự nhiên.
    - max_exchanges: số exchanges trước đó gửi lại cho model (mỗi exchange = user+assistant)
    """
    global memory

    messages = [{"role": "system", "content": system_prompt}]

    # add few-shot examples
    for ex in few_shots:
        messages.append({"role": "user", "content": ex["user"]})
        messages.append({"role": "assistant", "content": ex["assistant"]})

    # add short-term memory (last max_exchanges)
    num_messages = max_exchanges * 2  # mỗi exchange = 2 messages
    messages.extend(memory[-num_messages:])

    # add current message
    messages.append({"role": "user", "content": user_query})

    # ---- Call AI ----
    try:
        reply = ask_openai(messages)
    except Exception:
        reply = ask_gemini(messages)

    # ---- Clean reply ----
    reply = clean_reply(reply)

    # ---- Save memory ----
    memory.append({"role": "user", "content": user_query})
    memory.append({"role": "assistant", "content": reply})

    # cắt memory nếu vượt max
    if len(memory) > MAX_MEMORY:
        memory = memory[-MAX_MEMORY:]

    return reply
