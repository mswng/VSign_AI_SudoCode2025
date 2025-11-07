import os
import json
import requests
from pathlib import Path
from django.contrib.auth.models import User
from users.models import Customer
from .session_manage import start_session, log_message, end_session

BASE = Path(__file__).resolve().parent
PROMPT_TEMPLATE = (BASE / "prompt.txt").read_text(encoding="utf‑8", errors="ignore")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "openai/gpt-4o"  # hoặc chọn model khác từ OpenRouter

def create_agent(user_id=None):
    try:
        if user_id:
            customer = Customer.objects.select_related("user").get(user__id=user_id)
        else:
            raise Customer.DoesNotExist
    except Customer.DoesNotExist:
        anon_user, _ = User.objects.get_or_create(username="anonymous_user")
        customer, _ = Customer.objects.get_or_create(user=anon_user)

    static_vars = {
        "username": customer.user.username,
        "email": customer.email or "Không có email",
        "sex": customer.sex or "Không xác định",
    }
    session = start_session(customer)
    return static_vars, session



def query_agent(user_id, learner_input, vocab_list="", topics="", error_stats=None):
    static_vars, session = create_agent(user_id)

    if learner_input.strip().lower() in ["kết thúc", "thoát"]:
        end_session(session, summary="Học viên tự kết thúc buổi học.")
        return "✅ Buổi học đã kết thúc. Cảm ơn bạn đã luyện tập cùng SignTutor!"

    # chuẩn bị prompt nội dung
    input_data = {
        "learner_input": learner_input,
        "vocab_list": vocab_list,
        "topics": topics,
        "error_stats": json.dumps(error_stats or {}),
        **static_vars
    }
    prompt_content = PROMPT_TEMPLATE.format(**input_data)

    # gọi OpenRouter API
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt_content}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        resp = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        resp.raise_for_status()
        ans = resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        ans = f"⚠️ Lỗi khi gọi OpenRouter API: {e}"

    log_message(
        session=session,
        recognized=learner_input,
        expected="(AI phản hồi)",
        correct=True,
        explanation=ans,
    )

    return ans
