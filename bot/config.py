import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    # Telegram
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

    # DeepSeek
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
    DEEPSEEK_MAX_TOKENS = int(os.getenv("DEEPSEEK_MAX_TOKENS", 2000))
    DEEPSEEK_TEMPERATURE = float(os.getenv("DEEPSEEK_TEMPERATURE", 0.7))

    # Координаты
    DEFAULT_LAT = float(os.getenv("DEFAULT_LAT", 55.0965))
    DEFAULT_LON = float(os.getenv("DEFAULT_LON", 36.6355))

    # Рабочее время
    WORK_START_HOUR = int(os.getenv("WORK_START_HOUR", 9))
    WORK_END_HOUR = int(os.getenv("WORK_END_HOUR", 22))
    CONTEXT_EXPIRE_DAYS = int(os.getenv("CONTEXT_EXPIRE_DAYS", 30))

    ADMIN_ID = os.getenv("ADMIN_ID")
    DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

    # Пути
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    AUDIO_DIR = DATA_DIR / "audio"

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    CONVERSATIONS_DB = DATA_DIR / "conversations.db"
    RECIPES_DB = DATA_DIR / "recipes.db"
