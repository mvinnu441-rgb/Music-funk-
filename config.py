import os
from dotenv import load_dotenv

load_dotenv()

BOT_NAME = "Roohi Music Bot"

# ---- Bot Token (BotFather se) ----
BOT_TOKEN = os.getenv("BOT_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE")

# ---- Voice Chat Mode ke liye zaroori (my.telegram.org se milega) ----
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "PUT_YOUR_API_HASH_HERE")

# ---- Assistant Userbot Session String (generate_session.py chala kar banayein) ----
SESSION_STRING = os.getenv("SESSION_STRING", "")

# Telegram bots audio files 50MB se bade nahi bhej sakte (Simple Mode ke liye)
MAX_FILE_SIZE_MB = 50

# Downloads ke liye temp folder
DOWNLOAD_DIR = "downloads"
