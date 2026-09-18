# 🎵 Roohi Music Bot

Telegram Music Bot — do modes ke saath:

1. **Simple Mode** (`bot.py`) — Gaana search karke MP3 file bhejta hai (DM/group me)
2. **Voice Chat Mode** (`vc_bot.py`) — Gaana **group ki live voice chat** me bajata hai 🎙

---

## 📦 File Structure
```
roohi_music_bot/
├── bot.py               # Simple Mode (MP3 bhejna)
├── vc_bot.py             # Voice Chat Mode (live VC streaming)
├── queue_manager.py       # VC Mode ke liye gaano ki queue
├── generate_session.py    # Assistant account ka session banane ke liye
├── config.py               # Settings
├── requirements.txt        # Dependencies
├── .env.example              # Environment variables ka example
└── README.md
```

---

## 🔧 Common Setup (dono modes ke liye zaroori)

### 1. Python & FFmpeg
```bash
python3 --version   # 3.9+ hona chahiye
```
FFmpeg install karein:
- **Windows**: https://ffmpeg.org/download.html se download, PATH me add karein
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

### 2. Dependencies install karein
```bash
cd roohi_music_bot
pip install -r requirements.txt
```

### 3. Bot banayein
1. Telegram par [@BotFather](https://t.me/BotFather) kholein
2. `/newbot` bhejein → naam `Roohi Music Bot` do → username choose karein
3. Milne wala **token** copy kar lein

### 4. `.env` file banayein
`.env.example` ko copy karke `.env` naam dein, aur values bharein.

---

## 🅰️ Mode 1: Simple Mode (aasan, sirf MP3 bhejta hai)

`.env` me sirf yeh chahiye:
```
BOT_TOKEN=your_bot_token
```

Chalayein:
```bash
python bot.py
```

Commands:
- `/start`, `/help`
- `/play <gaane ka naam>` → MP3 file bhej dega

✅ Isme koi extra account nahi chahiye — bas bot token se kaam chal jata hai.

---

## 🅱️ Mode 2: Voice Chat Mode (advanced, group VC me live bajata hai)

Isme ek **assistant account** bhi chahiye hota hai, kyunki Telegram Bot API 
khud voice chat join nahi kar sakta — ek normal user account (jo aap khud 
control karte hain) group me join hokar stream karta hai.

### Step 1: API_ID aur API_HASH lein
1. https://my.telegram.org par jayein, apne number se login karein
2. "API Development Tools" → naya app banayein
3. `API_ID` aur `API_HASH` copy kar lein

### Step 2: Assistant Session String banayein
```bash
python generate_session.py
```
- Apna `API_ID` aur `API_HASH` daalein
- Phir apne (assistant wale) Telegram account ka phone number aur OTP daalein
  ⚠️ **Bot account nahi** — koi bhi normal Telegram account use karein
  (recommended: apna doosra/spare account, apna main account nahi)
- Milne wala `SESSION_STRING` copy kar lein

### Step 3: `.env` file complete karein
```
BOT_TOKEN=your_bot_token
API_ID=your_api_id
API_HASH=your_api_hash
SESSION_STRING=your_session_string
```

### Step 4: Assistant ko group me add karein
Jis group me gaana bajwana hai, us assistant account ko us group me
**add karein** (member ke roop me, admin zaroori nahi par better hai).

### Step 5: Bot chalayein
```bash
python vc_bot.py
```

### Commands (group me use karein, voice chat pehle se ON honi chahiye):
| Command | Kaam |
|---|---|
| `/vplay <naam>` | Gaana bajayein / queue me add karein |
| `/vpause` | Pause |
| `/vresume` | Resume |
| `/vskip` | Agla gaana |
| `/vstop` | Rokein, VC se nikal jayein |
| `/vqueue` | Queue dekhein |
| `/vhelp` | Sab commands |

---

## ⚠️ Important Notes

- **Copyright**: Sirf apne personal/group use ke liye gaane bajayein, publicly redistribute na karein.
- **Assistant account**: Session string kisi ke saath share na karein — isse
  poora account access mil jata hai. Chahein to isके liye ek naya/spare number use karein.
- **Rate limits**: Bahut zyada requests bhejne par Telegram temporarily block kar sakta hai — normal use me koi dikkat nahi hoti.
- Voice Chat Mode ki libraries (`pytgcalls`) समय के साथ update hoti rehti hain —
  agar koi import error aaye to `pip install --upgrade py-tgcalls pyrogram` try karein.

---

## 🐛 Troubleshooting

| Problem | Solution |
|---|---|
| `SESSION_STRING set nahi hai` | `python generate_session.py` pehle chalayein |
| Bot VC join nahi kar raha | Assistant account ko group me add karein, voice chat ON karein |
| `ffmpeg not found` | FFmpeg install karke PATH me add karein |
| Download fail ho raha | `pip install --upgrade yt-dlp` try karein |

Have fun with **Roohi Music Bot**! 🎶
