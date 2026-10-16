from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):

    # Database
    db_url: str = "mysql+pymysql://root:harsh@localhost:3306/ai_interview"

    # Groq AI
    groq_api_key: str = ""
    groq_api_url: str = "https://api.groq.com/openai/v1/chat/completions"
    groq_api_model: str = "qwen/qwen3.8-27b"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
