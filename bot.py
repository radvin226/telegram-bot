import asyncio
import random
import threading
from telethon import TelegramClient, events
import telebot
from google import genai

# ========== تنظیمات ==========
API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
BOT_TOKEN = "8923520269:AAGnYoOz0rIibUa8p-hqGGZlM2dse6YU8uo"      # ⚠️ حتماً عوض کنید
AI_API_KEY = "AQ.Ab8RN6JlTmIgo2aTxAfdIRTdRCUq4mJuO6DPFbEpu5N7LHqzMg"         # ⚠️ حتماً عوض کنید
MY_CHAT_ID = 6420547446                        # ⚠️ آیدی واقعی خودتان را بگذارید
CANCEL_KEYWORD = "زرنزن"

SYSTEM_PROMPT = """تو یک دستیار صمیمی فارسی‌زبان هستی.
پاسخ‌هایت کوتاه، طبیعی و همراه با ایموجی باشند.
هرگز اشاره نکن که هوش مصنوعی هستی."""

# ========== وضعیت مشترک ==========
auto_reply_active = False

# ========== Telebot (کنترل پنل) ==========
tg_bot = telebot.TeleBot(BOT_TOKEN)

@tg_bot.message_handler(commands=['start'])
def bot_start(message):
    global auto_reply_active
    if message.chat.id != MY_CHAT_ID:
        tg_bot.reply_to(message, "⛔ فقط صاحب اکانت مجاز است.")
        return
    auto_reply_active = True
    tg_bot.reply_to(message,
        "✅ پاسخگویی خودکار روی اکانت شخصی فعال شد.\n"
        f"برای غیرفعال کردن «{CANCEL_KEYWORD}» را بفرستید."
    )

@tg_bot.message_handler(func=lambda m: m.chat.id == MY_CHAT_ID and CANCEL_KEYWORD in (m.text or "").lower())
def bot_cancel(message):
    global auto_reply_active
    auto_reply_active = False
    tg_bot.reply_to(message, "❌ پاسخگویی خودکار غیرفعال شد.\n/start را بزنید تا دوباره فعال شود.")

# اجرای Telebot در ترد جداگانه
def run_bot():
    tg_bot.infinity_polling()
threading.Thread(target=run_bot, daemon=True).start()

# ========== Telethon (پاسخگوی اکانت شخصی) ==========
client = TelegramClient("personal_session", API_ID, API_HASH)
ai_client = genai.Client(api_key=AI_API_KEY)

@client.on(events.NewMessage(incoming=True))
async def handle_personal_messages(event):
    global auto_reply_active

    if event.is_group or event.is_channel or not auto_reply_active:
        return

    text = (event.raw_text or "").strip()
    lower_text = text.lower()

    # 🟢 پاسخ ثابت سلام/درود
    if any(w in lower_text for w in ['سلام', 'سلان', 'درود', 'slm', 'salam']):
        await asyncio.sleep(random.uniform(1, 2.5))
        await event.reply("درود عزیزم خوبی 😊🌹")
        print(f"✅ پاسخ سلام به: {event.chat_id}")
        return

    # 🤖 پاسخ AI
    try:
        response = ai_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                {"role": "user", "parts": [{"text": SYSTEM_PROMPT}]},
                {"role": "user", "parts": [{"text": text}]}
            ]
        )
        ai_reply = response.text.strip()
    except Exception as e:
        print(f"❌ خطای AI: {e}")
        ai_reply = "الان نمی‌تونم جواب بدم 😔"

    await asyncio.sleep(random.uniform(1.5, 4))
    final_msg = (
        f"{ai_reply}\n\n"
        f"🔔 این پیام بصورت خودکار ارسال شده\n"
        f"برای لغو «{CANCEL_KEYWORD}» را به بات بفرستید"
    )
    await event.reply(final_msg)
    print(f"✅ پاسخ AI به {event.chat_id}: {ai_reply[:50]}...")


# ========== اجرا ==========
async def main():
    await client.start()
    print("🚀 متصل شد! پاسخگویی با /start در بات فعال می‌شود.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
