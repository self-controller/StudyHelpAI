from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    model: str = "gpt-4.1-nano"
    whisper_model: str = "base"
    log_level: str = "INFO"
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")

    class Config:
        env_file = ".env"

settings = Settings()