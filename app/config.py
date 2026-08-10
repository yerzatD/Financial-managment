from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    app_name: str = "FastAPI Shop"
    debug: bool = True
    database_url: str = "sqlite+aiosqlite:///./finance.db"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    secret_key: SecretStr
    algorithm: str = "HS256"
    GEMINI_API_KEY: str
    access_token_expire_minutes: int = 30
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    static_dir: str = "static"
    images_dir: str = "static/images"


settings = Settings()