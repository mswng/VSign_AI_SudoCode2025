from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import ClassVar
import os


load_dotenv()


class Settings(BaseSettings):
    """Cấu hình ứng dụng Silent Speak - SignTutor."""

    # ===== Thông tin ứng dụng =====
    APP_TITLE: str = "Silent Speak"
    SYSTEM_PROMPT: str = (
        "Bạn là SignTutor — trợ lý AI giúp học viên nhận diện và ghi nhớ ngôn ngữ ký hiệu Việt Nam. "
        "Luôn sử dụng **chính xác ký hiệu mà học viên nhập** để giải thích. "
        "Không thay đổi ký hiệu, không tự chọn ký hiệu khác."
    )

    # ===== Cấu hình model & API =====
    OPENROUTER_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_API_KEY: str  
    MODEL_NAME: str = "x-ai/grok-4.1-fast"

    GEMINI_API_KEY: str = "" 
    TAVILY_API_KEY: str = "" 

    # ===== Prompt Template =====
    BASE_DIR: ClassVar[Path] = Path(__file__).resolve().parent
    PROMPT_TEMPLATE_PATH: ClassVar[Path] = BASE_DIR / "prompt.txt"

    @property
    def PROMPT_TEMPLATE(self) -> str:
        """Đọc nội dung prompt từ file."""
        if self.PROMPT_TEMPLATE_PATH.exists():
            return self.PROMPT_TEMPLATE_PATH.read_text(encoding="utf-8", errors="ignore")
        return ""

    class Config:
        env_file = ".env"
        extra = "allow" 

settings = Settings()
