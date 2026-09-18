"""
Yeh script assistant (userbot) account ke liye SESSION_STRING banata hai.
Voice Chat Mode ke liye zaroori hai (kyunki normal bots VC join nahi kar sakte).

Chalane ka tareeka:
    python generate_session.py

Zaroori:
- API_ID aur API_HASH (my.telegram.org se milega)
- Ek Telegram account (bot nahi, normal account) jo assistant ke roop me
  group/channel ki voice chat me gaana bajayega
"""

from pyrogram import Client

print("=== Roohi Music Bot - Session String Generator ===\n")

api_id = input("API_ID daalein: ").strip()
api_hash = input("API_HASH daalein: ").strip()

with Client("assistant_session", api_id=int(api_id), api_hash=api_hash) as app:
    session_string = app.export_session_string()
    print("\n✅ Aapka SESSION_STRING ban gaya hai!\n")
    print(session_string)
    print("\nIse apni .env file me SESSION_STRING= ke aage paste kar dein.")
    print("⚠️  Yeh string kisi ke saath share na karein, isse aapka account access ho sakta hai.")
