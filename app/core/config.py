from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str
    tavily_api_key: str

    model_name: str = "claude-sonnet-4-20250514"
    embedding_provider: str = "local"
    embedding_model: str = "all-MiniLM-L6-v2"

    max_tokens: int = 4096 
    max_sources: int = 15
    max_retries: int = 3

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()