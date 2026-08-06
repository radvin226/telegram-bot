import asyncio
import random
import os
from telethon import TelegramClient, events
from telebot.async_telebot import AsyncTeleBot
from google import genai

# ========== تنظیمات از متغیرهای محیطی ==========
API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"
BOT_TOKEN = os.environ.get("8923520269:AAGnYoOz0rIibUa8p-hqGGZlM2dse6YU8uo")
AI_API_KEY = os.environ.get("AQ.Ab8RN6KNcpLEzX1iThuvuyhHfcMO7zQsEHoe5EFTrxas3TQ26g")
MY_CHAT_ID = int(os.environ.get("MY_CHAT_ID", "0"))
CANCEL_KEYWORD = "زرنزن"
SESSION_PATH = "/app/personal_session"

if not BOT_TOKEN or not AI_API_KEY:
    raise ValueError("❌ BOT_TOKEN یا AI_API_KEY در Railway Variables تنظیم نشده!")

SYSTEM_PROMPT = """تو یک دستیار صمیمی فارسی‌زبان هستی.
پاسخ‌هایت کوتاه، طبیعی و همراه با ایموجی باشند.
هرگز اشاره نکن که هوش مصنوعی هستی."""

auto_reply_active = False

# ========== Telethon ==========
client = TelegramClient(SESSION_PATH, API_ID, API_HASH)
ai_client = genai.Client(api_key=AI_API_KEY)

@client.on(events.NewMessage(incoming=True))
async def handle_personal_messages(event):
    global auto_reply_active
    if event.is_group or event.is_channel or not auto_reply_active:
        return

    text = (event.raw_text or "").strip()
    lower_text = text.lower()

    if any(w in lower_text for w in ['سلام', 'سلان', 'درود', 'slm', 'salam']):
        await asyncio.sleep(random.uniform(1, 2.5))
        await event.reply("درود عزیزم خوبی 😊🌹")
        return

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

# ========== Telebot (Async - بدون ترد جداگانه) ==========
async_bot = AsyncTeleBot(BOT_TOKEN)

@async_bot.message_handler(commands=['start'])
async def bot_start(message):
    global auto_reply_active
    if message.chat.id != MY_CHAT_ID:
        await async_bot.reply_to(message, "⛔ فقط صاحب اکانت مجاز است.")
        return
    auto_reply_active = True
    await async_bot.reply_to(message,
        "✅ پاسخگویی خودکار فعال شد.\n"
        f"برای لغو «{CANCEL_KEYWORD}» را بفرستید."
    )

@async_bot.message_handler(func=lambda m: m.chat.id == MY_CHAT_ID and CANCEL_KEYWORD in (m.text or "").lower())
async def bot_cancel(message):
    global auto_reply_active
    auto_reply_active = False
    await async_bot.reply_to(message, "❌ غیرفعال شد.\n/start برای فعال‌سازی مجدد.")

# ========== اجرای همزمان ==========
async def main():
    await client.start()
    print("🚀 Telethon متصل شد!")
    print("🚀 ربات آماده است!")
    await asyncio.gather(
        client.run_until_disconnected(),
        async_bot.infinity_polling()
    )

if __name__ == "__main__":
    asyncio.run(main())
