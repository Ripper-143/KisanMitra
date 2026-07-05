from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App Settings
    APP_NAME: str = "KisanMitra"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "kisan-mitra-dev-secret-key-xyz987abc"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Database
    DATABASE_URL: str = "sqlite:///./kisanmitra.db"

    # LLM (CrewAI)
    LLM_PROVIDER: str = "groq" # 'groq', 'gemini', or 'openai'
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "groq/llama-3.3-70b-versatile"

    # External APIs
    OPENWEATHERMAP_API_KEY: str = ""
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_FROM_NUMBER: str = ""
    PLANT_ID_API_KEY: str = ""
    DATA_GOV_IN_API_KEY: str = ""

    # ChromaDB RAG Settings
    CHROMA_PERSIST_DIR: str = "./rag/chroma_db"
    CHROMA_COLLECTION: str = "kisan_schemes"

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
