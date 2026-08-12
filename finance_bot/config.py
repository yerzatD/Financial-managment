import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    bot_token: str
    api_base_url: str
    tokens_file: str


def load_config() -> Config:
    return Config(
        bot_token=os.environ.get("BOT_TOKEN", ""),
        api_base_url=os.environ.get("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/"),
        tokens_file=os.environ.get("TOKENS_FILE", "tokens.json"),
    )
