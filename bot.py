"""
Roohi Music Bot - SIMPLE MODE
------------------------------
Ek simple Telegram bot jo YouTube se gaane search karke
audio (MP3) ke roop me DM/group me bhej deta hai.
(Group voice chat me live gaana bajane ke liye vc_bot.py use karein)

Commands:
  /start        - Bot shuru karein
  /help         - Madad / commands ki list
  /play <naam>  - Gaana search karke bhejein
"""

import logging
import os
import uuid
import shutil

import yt_dlp
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import BOT_TOKEN, BOT_NAME, MAX_FILE_SIZE_MB, DOWNLOAD_DIR

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def download_audio(query: str, out_dir: str) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    file_id = str(uuid.uuid4())
    out_template = os.path.join(out_dir, f"{file_id}.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": out_template,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch1",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        if "entries" in info:
            info = info["entries"][0]

        final_path = os.path.join(out_dir, f"{file_id}.mp3")
        return {
            "path": final_path,
            "title": info.get("title", "Unknown Title"),
            "duration": info.get("duration", 0),
        }


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"👋 Namaste {update.effective_user.first_name}!\n\n"
        f"Main *{BOT_NAME}* hoon 🎵\n\n"
        "Mujhe koi bhi gaane ka naam bhejo, main woh gaana dhoondh kar "
        "aapko MP3 file bhej dunga.\n\n"
        "Command: `/play gaane ka naam`\n"
        "Madad ke liye: /help\n\n"
        "🎙 Group voice chat me live gaana bajwana hai? `vc_bot.py` use karein."
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🎧 *Roohi Music Bot - Commands (Simple Mode)*\n\n"
        "/start - Bot shuru karein\n"
        "/play <gaane ka naam> - Gaana search karke MP3 bhejein\n"
        "/help - Yeh message dobara dekhein\n\n"
        "Example:\n`/play tum hi ho`"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❗ Gaane ka naam bhi likhein.\nExample: `/play tum hi ho`",
            parse_mode="Markdown",
        )
        return

    query = " ".join(context.args)
    status_msg = await update.message.reply_text(f"🔎 '{query}' search kar raha hoon...")

    chat_id = update.effective_chat.id
    user_dir = os.path.join(DOWNLOAD_DIR, str(chat_id))

    try:
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.RECORD_VOICE)
        await status_msg.edit_text(f"⬇️ '{query}' download ho raha hai...")

        result = download_audio(query, user_dir)
        file_path = result["path"]

        if not os.path.exists(file_path):
            await status_msg.edit_text("❌ Gaana download nahi ho paaya. Doosra naam try karein.")
            return

        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            await status_msg.edit_text(
                f"❌ File bahut badi hai ({size_mb:.1f}MB). "
                f"Telegram bots {MAX_FILE_SIZE_MB}MB se badi file nahi bhej sakte."
            )
            os.remove(file_path)
            return

        await status_msg.edit_text("📤 Bhej raha hoon...")
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_VOICE)

        with open(file_path, "rb") as audio_file:
            await update.message.reply_audio(
                audio=audio_file,
                title=result["title"],
                duration=result["duration"],
                caption=f"🎵 {result['title']}\n\n_{BOT_NAME} dwara bheja gaya_",
                parse_mode="Markdown",
            )

        await status_msg.delete()

    except Exception as e:
        logger.error(f"Error in /play: {e}")
        await status_msg.edit_text(
            "❌ Kuch galat ho gaya. Kripya doosra gaana try karein ya kuch der baad koshish karein."
        )
    finally:
        if os.path.exists(user_dir):
            shutil.rmtree(user_dir, ignore_errors=True)


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.args = update.message.text.split()
    await play(update, context)


def main():
    if not BOT_TOKEN or BOT_TOKEN == "PUT_YOUR_BOT_TOKEN_HERE":
        print("⚠️  Kripya config.py ya .env file me apna BOT_TOKEN daalein!")
        return

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))

    print(f"✅ {BOT_NAME} (Simple Mode) chalu ho gaya hai...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
