from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from .config import settings


def get_ai_model(prefer: str = "openrouter"):
   
    # === Ưu tiên 1: OpenRouter ===
    if prefer == "openrouter" and settings.OPENROUTER_API_KEY:
        try:
            return ChatOpenAI(
                model=settings.MODEL_NAME,
                openai_api_key=settings.OPENROUTER_API_KEY,
                openai_api_base=settings.OPENROUTER_URL,
                temperature=0.7,
            )
        except Exception as e:
            print(f"[⚠️ Đã xãy ra lỗi với hệ thống.] {e}")

    # === Fallback: Gemini ===
    if settings.GEMINI_API_KEY:
        try:
            return ChatGoogleGenerativeAI(
                model="gemini-3.5-flash",
                temperature=0.7,
                google_api_key=settings.GEMINI_API_KEY,
            )
        except Exception as e:
            print(f"[⚠️ Đã xãy ra lỗi với hệ thống.] {e}")

    # === Không có model nào hoạt động ===
    raise RuntimeError("❌ Không thể khởi tạo bất kỳ model AI nào. Kiểm tra API key trong .env.")
