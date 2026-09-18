"""
Roohi Music Bot - VOICE CHAT MODE 🎙
-------------------------------------
Yeh version group ki VOICE CHAT me LIVE gaana bajata hai
(jaise AhmadMusic, Vc Music Bot jaise bots karte hain).

Kaise kaam karta hai:
  - "Bot" (BOT_TOKEN) commands sunta hai (/vplay, /vskip, etc.)
  - "Assistant" (SESSION_STRING wala normal account) voice chat me
    join hokar audio stream karta hai, kyunki Telegram Bot API
    khud voice chats join nahi kar sakta.

Commands:
  /vplay <naam>   - Gaana search karke voice chat me bajayein
  /vpause         - Pause karein
  /vresume        - Resume karein
  /vskip          - Agla gaana bajayein (agar queue me hai)
  /vstop          - Rokein aur voice chat se nikal jayein
  /vqueue         - Queue dekhein

Setup:
  1. .env me BOT_TOKEN, API_ID, API_HASH, SESSION_STRING bharein
     (SESSION_STRING generate_session.py se banega)
  2. Assistant account ko us group me add/admin banayein jaha gaana bajana hai
  3. python vc_bot.py chalayein
"""

import asyncio
import logging
import os
import uuid

import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio
from pytgcalls.types import Update as PyTgCallsUpdate
from pytgcalls.types.stream import StreamAudioEnded

from config import BOT_TOKEN, API_ID, API_HASH, SESSION_STRING, BOT_NAME, DOWNLOAD_DIR
from queue_manager import add_to_queue, get_queue, pop_next, current_song, clear_queue

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ---- Clients ----
# 1) Bot: commands handle karta hai
bot = Client("roohi_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 2) Assistant (userbot): voice chat join karke stream karta hai
assistant = Client("roohi_assistant", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# 3) PyTgCalls: assistant ko voice-calling capability deta hai
call_py = PyTgCalls(assistant)


# ---------- Helper: gaana download karna ----------
def download_song(query: str) -> dict:
    file_id = str(uuid.uuid4())
    out_template = os.path.join(DOWNLOAD_DIR, f"{file_id}.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": out_template,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch1",
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}
        ],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        if "entries" in info:
            info = info["entries"][0]
        return {
            "path": os.path.join(DOWNLOAD_DIR, f"{file_id}.mp3"),
            "title": info.get("title", "Unknown Title"),
            "duration": info.get("duration", 0),
            "requested_by": None,
        }


# ---------- /vplay ----------
@bot.on_message(filters.command("vplay") & filters.group)
async def vplay(_, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❗ Gaane ka naam bhi likhein.\nExample: `/vplay tum hi ho`")
        return

    query = " ".join(message.command[1:])
    chat_id = message.chat.id
    status = await message.reply_text(f"🔎 '{query}' dhoondh raha hoon...")

    try:
        loop = asyncio.get_event_loop()
        song = await loop.run_in_executor(None, download_song, query)
        song["requested_by"] = message.from_user.first_name if message.from_user else "Someone"

        already_playing = bool(get_queue(chat_id))
        add_to_queue(chat_id, song)

        if not already_playing:
            await call_py.join_group_call(
                chat_id,
                AudioPiped(song["path"], HighQualityAudio()),
            )
            await status.edit_text(
                f"▶️ Ab baj raha hai: *{song['title']}*\n"
                f"🙋 Request: {song['requested_by']}",
                parse_mode="markdown",
            )
        else:
            await status.edit_text(
                f"➕ Queue me add ho gaya: *{song['title']}*\n"
                f"📋 Position: {len(get_queue(chat_id))}",
                parse_mode="markdown",
            )

    except Exception as e:
        logger.error(f"vplay error: {e}")
        await status.edit_text(
            "❌ Kuch galat ho gaya. Check karein ki assistant account is group me hai, "
            "aur voice chat shuru hai."
        )


# ---------- /vpause ----------
@bot.on_message(filters.command("vpause") & filters.group)
async def vpause(_, message: Message):
    try:
        await call_py.pause_stream(message.chat.id)
        await message.reply_text("⏸ Pause kar diya.")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")


# ---------- /vresume ----------
@bot.on_message(filters.command("vresume") & filters.group)
async def vresume(_, message: Message):
    try:
        await call_py.resume_stream(message.chat.id)
        await message.reply_text("▶️ Resume kar diya.")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")


# ---------- /vskip ----------
@bot.on_message(filters.command("vskip") & filters.group)
async def vskip(_, message: Message):
    chat_id = message.chat.id
    next_song = pop_next(chat_id)

    if not next_song:
        try:
            await call_py.leave_group_call(chat_id)
        except Exception:
            pass
        clear_queue(chat_id)
        await message.reply_text("⏹ Queue khatam. Voice chat se nikal gaya.")
        return

    try:
        await call_py.change_stream(chat_id, AudioPiped(next_song["path"], HighQualityAudio()))
        await message.reply_text(
            f"⏭ Agla gaana: *{next_song['title']}*\n"
            f"🙋 Request: {next_song['requested_by']}",
            parse_mode="markdown",
        )
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")


# ---------- /vstop ----------
@bot.on_message(filters.command("vstop") & filters.group)
async def vstop(_, message: Message):
    chat_id = message.chat.id
    try:
        await call_py.leave_group_call(chat_id)
    except Exception:
        pass
    clear_queue(chat_id)
    await message.reply_text("⏹ Rok diya aur voice chat se nikal gaya.")


# ---------- /vqueue ----------
@bot.on_message(filters.command("vqueue") & filters.group)
async def vqueue(_, message: Message):
    q = get_queue(message.chat.id)
    if not q:
        await message.reply_text("📋 Queue khaali hai.")
        return

    text = "📋 *Current Queue:*\n\n"
    for i, song in enumerate(q):
        marker = "▶️" if i == 0 else f"{i}."
        text += f"{marker} {song['title']} — _{song['requested_by']}_\n"

    await message.reply_text(text, parse_mode="markdown")


# ---------- /vhelp ----------
@bot.on_message(filters.command("vhelp"))
async def vhelp(_, message: Message):
    text = (
        f"🎙 *{BOT_NAME} - Voice Chat Mode*\n\n"
        "/vplay <naam> - Voice chat me gaana bajayein / queue me add karein\n"
        "/vpause - Pause\n"
        "/vresume - Resume\n"
        "/vskip - Agla gaana\n"
        "/vstop - Rokein aur nikal jayein\n"
        "/vqueue - Queue dekhein\n\n"
        "⚠️ Bot ko group me admin banayein aur voice chat shuru rakhein."
    )
    await message.reply_text(text, parse_mode="markdown")


# ---------- Auto-play next song jab current khatam ho jaye ----------
@call_py.on_update()
async def on_stream_end(_, update: PyTgCallsUpdate):
    if isinstance(update, StreamAudioEnded):
        chat_id = update.chat_id
        next_song = pop_next(chat_id)
        if next_song:
            await call_py.change_stream(chat_id, AudioPiped(next_song["path"], HighQualityAudio()))
        else:
            try:
                await call_py.leave_group_call(chat_id)
            except Exception:
                pass
            clear_queue(chat_id)


async def main():
    await assistant.start()
    await bot.start()
    await call_py.start()
    print(f"✅ {BOT_NAME} (Voice Chat Mode) chalu ho gaya hai...")
    await asyncio.Event().wait()  # hamesha chalta rahega


if __name__ == "__main__":
    if not SESSION_STRING:
        print("⚠️  SESSION_STRING set nahi hai. Pehle 'python generate_session.py' chalayein.")
    elif not BOT_TOKEN or BOT_TOKEN == "PUT_YOUR_BOT_TOKEN_HERE":
        print("⚠️  Kripya .env me BOT_TOKEN daalein!")
    elif API_ID == 0:
        print("⚠️  Kripya .env me API_ID aur API_HASH daalein (my.telegram.org se)!")
    else:
        asyncio.run(main())
