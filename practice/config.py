from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    """Application settings for the Weather Agent."""

    APP_TITLE: str = "Weather Agent"
    SYSTEM_PROMPT: str = "Agent thời tiết. Trả lời ngắn gọn, có đơn vị (°C, %RH, mm) và thời điểm. Dùng tool theo location."
    OPENAI_MODEL: str = "gpt-4.1-mini"
    OPENAI_API_KEY: str = "openai_api_key"
    GEMINI_API_KEY: str = "gemini_api_key"
    TAVILY_API_KEY: str = "tavily_api_key"

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()