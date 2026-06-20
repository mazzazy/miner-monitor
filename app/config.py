from dotenv import load_dotenv
import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

ENV_FILE = PROJECT_ROOT / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    print(f"⚠️ Warning: .env file not found at {ENV_FILE}")


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


class Config:

    # -----------------------------
    # General
    # -----------------------------
    POOL_NAME = os.getenv("POOL_NAME", "Braiins Pool")

    # -----------------------------
    # Braiins (required)
    # -----------------------------
    BRAIINS_API_URL = require_env("BRAIINS_API_URL")
    BRAIINS_API_TOKEN = require_env("BRAIINS_API_TOKEN")

    # -----------------------------
    # Optional pools
    # -----------------------------
    OURPOOL_API_URL = os.getenv("OURPOOL_API_URL")

    # -----------------------------
    # Telegram (required for alerts)
    # -----------------------------
    BOT_TOKEN = require_env("BOT_TOKEN")
    CHAT_ID = require_env("CHAT_ID")

    # -----------------------------
    # Email (optional future)
    # -----------------------------
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = os.getenv("SMTP_PORT")
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASS = os.getenv("SMTP_PASS")

    # -----------------------------
    # Storage
    # -----------------------------
    HISTORY_FILE = "data/history.csv"
    STATE_FILE = "data/state.json"

    # -----------------------------
    # Thresholds
    # -----------------------------
    OFFLINE_THRESHOLD = 600
    DEAD_THRESHOLD = 3600
    LOW_HASHRATE_RATIO = 0.5

    WARNING_THRESHOLD_MINUTES = 15
    CRITICAL_THRESHOLD_MINUTES = 60

    ENABLE_TELEGRAM = True
    ENABLE_EMAIL = False
    ENABLE_SLACK = False
    ENABLE_TEAMS = False