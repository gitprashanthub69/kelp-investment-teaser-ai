
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Kelp AI"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "YOUR_SECRET_KEY_HERE_CHANGE_IN_PROD"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External APIs
    OPENAI_API_KEY: str
    UNSPLASH_ACCESS_KEY: str | None = None

    # Database
    DATABASE_URL: str | None = None
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./sql_app.db"

    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()
