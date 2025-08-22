from pydantic import BaseSettings

class Settings(BaseSettings):
    model: str = "gpt-oss:latest"
    whisper_model: str = "base"
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()