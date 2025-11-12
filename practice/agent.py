# agent.py
import json
from pathlib import Path
from django.contrib.auth.models import User
from users.models import Customer, UserFlashcard
from .session_manage import start_session, log_message, end_session
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .config import settings   

# === Khởi tạo model LangChain OpenRouter ===
# ⚠️ Chú ý: đây là instance ChatOpenAI, dùng generate(messages_list) theo v0.3.x
llm = ChatOpenAI(
    model=settings.MODEL_NAME,
    openai_api_key=settings.OPENROUTER_API_KEY,
    openai_api_base=settings.OPENROUTER_URL,
    temperature=0.7,
    max_tokens=500,
)

# === Tạo agent học viên ===
def create_agent(user_id=None):
    try:
        if user_id:
            customer = Customer.objects.select_related("user").get(user__id=user_id)
        else:
            raise Customer.DoesNotExist
    except Customer.DoesNotExist:
        # ⚠️ Nếu không tìm thấy user, dùng anonymous
        anon_user, _ = User.objects.get_or_create(username="anonymous_user")
        customer, _ = Customer.objects.get_or_create(user=anon_user)

    static_vars = {
        "username": customer.user.username,
        "email": customer.email or "Không có email",
        "sex": customer.sex or "Không xác định",
    }

    session = start_session(customer)
    return static_vars, session

# === Gọi model phản hồi học viên ===
def query_agent(user_id, learner_input, topics="", error_stats=None, vocab_list=None):
    static_vars, session = create_agent(user_id)

    # ⚠️ Nếu chưa có vocab_list truyền vào, lấy từ DB
    if vocab_list is None:
        user_flashcards = UserFlashcard.objects.filter(user__user__id=user_id, learned=True)
        vocab_list = list(user_flashcards.values_list("flashcard__front_text", flat=True))

    # Xử lý kết thúc buổi học
    if learner_input.strip().lower() in ["kết thúc", "thoát"]:
        end_session(session, summary="Học viên tự kết thúc buổi học.")
        return "✅ Buổi học đã kết thúc. Cảm ơn bạn đã luyện tập cùng SilentSpeak!"

    # ⚠️ Chuẩn bị prompt với vocab_list
    input_data = {
        "learner_input": learner_input,
        "vocab_list": vocab_list,  # list các ký hiệu học viên đã học
        "topics": topics,
        "error_stats": json.dumps(error_stats or {}),
        **static_vars,
    }

    # ⚠️ Format prompt từ file txt (settings.PROMPT_TEMPLATE)
    prompt_template = settings.PROMPT_TEMPLATE or "{learner_input}"
    user_prompt = prompt_template.format(
        learner_input=input_data["learner_input"],
        vocab_list=", ".join(input_data["vocab_list"]),
        topics=input_data["topics"],
        error_stats=input_data["error_stats"],
        username=input_data["username"]
    )

    # ⚠️ SystemMessage ép LLM chỉ dùng vocab_list
    system_msg = SystemMessage(
        content=f"""
Bạn là SignTutor, trợ lý AI cho học viên ngôn ngữ ký hiệu Việt Nam.
Chỉ được dùng các ký hiệu trong danh sách vocab_list sau: {vocab_list}
Nếu học viên hỏi ký hiệu không có trong danh sách:
- Không tạo ký hiệu mới.
- Trả lời: "Tôi chưa được học qua chữ này, xin lỗi bạn nhé.".
Trả lời ngắn gọn, thân thiện, hoàn toàn bằng tiếng Việt.
"""
    )
    human_msg = HumanMessage(content=user_prompt)

    try:
        # ⚠️ Chú ý: generate nhận list of list of messages
        messages = [system_msg, human_msg]
        response = llm.generate([messages]) 
        ans = response.generations[0][0].text.strip()  

        # ⚠️ Filter output: chỉ giữ những ký hiệu trong vocab_list
        if vocab_list:
            filtered_lines = []
            for line in ans.split("\n"):
                if any(v in line for v in vocab_list):
                    filtered_lines.append(line)
            if filtered_lines:
                ans = "\n".join(filtered_lines)
            else:
                ans = "⚠️ Tớ chưa được học qua chữ này."
    except Exception as e:
        ans = f"⚠️ Hệ thống AI tạm thời không khả dụng: {e}"

    # ⚠️ Lưu session log
    log_message(
        session=session,
        recognized=learner_input,
        expected="(AI phản hồi)",
        correct=True,
        explanation=ans,
    )

    return ans
