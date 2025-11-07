from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env
load_dotenv()

class Settings(BaseSettings):
    """Cấu hình ứng dụng Silent Speak - SignTutor."""

    # Thông tin ứng dụng
    APP_TITLE: str = "Silent Speak"
    
    # Prompt hệ thống (gợi ý cho AI)
    SYSTEM_PROMPT: str = (
        "Bạn là SignTutor — trợ lý AI giúp học viên nhận diện và ghi nhớ ngôn ngữ ký hiệu Việt Nam. "
        "Luôn sử dụng **chính xác ký hiệu mà học viên nhập** để giải thích. Không thay đổi ký hiệu, không tự chọn ký hiệu khác."

    )

    # Model và API keys
    OPENAI_MODEL: str = "gpt-4.1-mini"
    OPENROUTER_API_KEY: str  # lấy từ .env, không hardcode
    GEMINI_API_KEY: str = ""  # để trống, lấy từ .env nếu cần
    TAVILY_API_KEY: str = ""  # để trống, lấy từ .env nếu cần

    class Config:
        env_file = ".env"
        extra = "allow"  # cho phép thêm biến môi trường khác

# Khởi tạo settings
settings = Settings()
