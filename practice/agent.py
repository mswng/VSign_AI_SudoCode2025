import json
from django.contrib.auth.models import User
from users.models import Customer, UserFlashcard
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .config import settings

# ----------------------------
# Memory store tạm cho session
# ----------------------------
TEMP_SESSIONS = {}  # {user_id: {"logs": [{"learner_input":..., "ai_reply":...}], "static_vars": {...}}}

# ----------------------------
# Khởi tạo model LangChain OpenRouter
# ----------------------------
llm = ChatOpenAI(
    model=settings.MODEL_NAME,
    openai_api_key=settings.OPENROUTER_API_KEY,
    openai_api_base=settings.OPENROUTER_URL,
    temperature=0.7,
    max_tokens=500,
)

# ----------------------------
# Tạo agent / session tạm
# ----------------------------
def create_agent(user_id=None):
    """Tạo agent cho user hoặc anonymous"""
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

    # Khởi tạo session tạm trong memory
    if user_id not in TEMP_SESSIONS:
        TEMP_SESSIONS[user_id] = {"logs": [], "static_vars": static_vars}

    return static_vars, TEMP_SESSIONS[user_id]

# ----------------------------
# Ghi log tạm
# ----------------------------
def log_temp_session(user_id, learner_input, ai_reply):
    """Ghi log tạm vào memory"""
    if user_id not in TEMP_SESSIONS:
        TEMP_SESSIONS[user_id] = {"logs": [], "static_vars": {}}
    TEMP_SESSIONS[user_id]["logs"].append({
        "learner_input": learner_input,
        "ai_reply": ai_reply
    })

def get_temp_session_logs(user_id):
    """Lấy tất cả log cho user"""
    return TEMP_SESSIONS.get(user_id, {}).get("logs", [])

def end_temp_session(user_id):
    """Xóa session tạm khi kết thúc"""
    TEMP_SESSIONS.pop(user_id, None)

# ----------------------------
# Gọi LLM phản hồi học viên
# ----------------------------
def query_agent(user_id, learner_input, topics=None, error_stats=None, vocab_list=None):
    """Gọi LLM phản hồi học viên"""
    static_vars, session = create_agent(user_id)

    # Nếu vocab_list chưa có → lấy từ DB
    if vocab_list is None:
        user_flashcards = UserFlashcard.objects.filter(user__user__id=user_id, learned=True)
        vocab_list = list(user_flashcards.values_list("flashcard__front_text", flat=True))

    if topics is None:
        topics = []

    # Kết thúc buổi học
    if learner_input.strip().lower() in ["kết thúc", "thoát"]:
        end_temp_session(user_id)
        return "✅ Buổi học đã kết thúc. Cảm ơn bạn đã luyện tập cùng SilentSpeak!"

    # Chuẩn bị prompt
    input_data = {
        "learner_input": learner_input,
        "vocab_list": vocab_list,
        "topics": topics,
        "error_stats": json.dumps(error_stats or {}),
        **static_vars,
    }

    prompt_template = settings.PROMPT_TEMPLATE or "{learner_input}"
    user_prompt = prompt_template.format(
        learner_input=input_data["learner_input"],
        vocab_list=", ".join(input_data["vocab_list"]),
        topics=", ".join(input_data["topics"]),
        error_stats=input_data["error_stats"],
        username=input_data["username"]
    )

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
        messages = [system_msg, human_msg]
        response = llm.generate([messages])
        ans = response.generations[0][0].text.strip()

        # Filter output: chỉ giữ ký hiệu trong vocab_list
        if vocab_list:
            filtered_lines = []
            for line in ans.split("\n"):
                if any(v in line for v in vocab_list):
                    filtered_lines.append(line)
            ans = "\n".join(filtered_lines) if filtered_lines else "⚠️ Tớ chưa được học qua chữ này."

    except Exception as e:
        ans = f"⚠️ Hệ thống AI tạm thời không khả dụng: {e}"

    # Ghi log tạm
    log_temp_session(user_id, learner_input, ans)

    return ans
