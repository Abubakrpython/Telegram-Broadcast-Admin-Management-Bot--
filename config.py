import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =========================
# Telegram
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", 0))

# =========================
# Database
# =========================
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# =========================
# Validation (optional but recommended)
# =========================
if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN is not set")

if not DATABASE_URL:
    raise RuntimeError("❌ DATABASE_URL is not set")
