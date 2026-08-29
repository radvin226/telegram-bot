import telebot
import json
import os
import threading
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# =========================
# تنظیمات
# =========================

TOKEN = "8812578287:AAFuMCUsli9AkNELOUKKltW9uiYlB3HSoXY"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

DATA_FILE = "data.json"

# وضعیت ارسال پیام‌های دوره‌ای
running_groups = {}
timers = {}


# =========================
# دیتابیس JSON
# =========================

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


data = load_data()


# =========================
# دکمه شیشه‌ای
# =========================

def main_keyboard():
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            "🐶 من سگ تینام",
            callback_data="dog_tina"
        )
    )

    return keyboard


# =========================
# بررسی ادمین
# =========================

def is_admin(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)

        return member.status in [
            "administrator",
            "creator"
        ]

    except Exception as e:
        print("ADMIN CHECK ERROR:", e)
        return False


# =========================
# ارسال پیام هر ۲ دقیقه
# =========================

def send_dog_message(chat_id):

    if not running_groups.get(chat_id, False):
        return

    try:
        bot.send_message(
            chat_id,
            "🐶 من سگتم"
        )
    except Exception as e:
        print("SEND ERROR:", e)

    if running_groups.get(chat_id, False):
        timer = threading.Timer(
            120,
            send_dog_message,
            args=[chat_id]
        )

        timer.daemon = True
        timers[chat_id] = timer
        timer.start()


def start_dog_messages(chat_id):

    if running_groups.get(chat_id, False):
        return

    running_groups[chat_id] = True

    send_dog_message(chat_id)


def stop_dog_messages(chat_id):

    running_groups[chat_id] = False

    timer = timers.get(chat_id)

    if timer:
        try:
            timer.cancel()
        except:
            pass

    timers.pop(chat_id, None)


# =========================
# /start
# =========================

@bot.message_handler(commands=["start"])
def start(message):

    text = (
        "🐶 <b>من سگ تینام</b>\n\n"
        "روی دکمه زیر بزن:"
    )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=main_keyboard()
    )


# =========================
# دکمه
# =========================

@bot.callback_query_handler(func=lambda call: call.data == "dog_tina")
def dog_button(call):

    try:
        bot.answer_callback_query(
            call.id,
            "من سگ تینام 🐶"
        )

        bot.send_message(
            call.message.chat.id,
            "🐶 من سگ تینام"
        )

    except Exception as e:
        print("BUTTON ERROR:", e)


# =========================
# وقتی بات وارد گروه می‌شود
# =========================

@bot.my_chat_member_handler()
def bot_added(message):

    try:
        new_status = message.new_chat_member.status

        if new_status in ["member", "administrator"]:

            chat_id = str(message.chat.id)

            if chat_id not in data:
                data[chat_id] = {
                    "owner_id": None,
                    "owner_name": None
                }

                save_data(data)

            bot.send_message(
                message.chat.id,
                "🐶 من سگ تینام!\n\n"
                "برای ثبت صاحبم، یک ادمین روی پیام من ریپلای کنه و بنویسه:\n\n"
                "<code>صاحبته</code>"
            )

    except Exception as e:
        print("GROUP JOIN ERROR:", e)


# =========================
# ثبت صاحب
# =========================

@bot.message_handler(
    func=lambda message:
        message.text and
        message.text.strip() == "صاحبته"
)
def set_owner(message):

    # فقط گروه
    if message.chat.type not in ["group", "supergroup"]:
        return

    # باید ریپلای باشد
    if not message.reply_to_message:
        bot.reply_to(
            message,
            "❌ باید روی پیام من ریپلای کنی."
        )
        return

    # فقط ادمین
    if not is_admin(
        message.chat.id,
        message.from_user.id
    ):
        bot.reply_to(
            message,
            "❌ فقط ادمین گروه می‌تواند صاحبم را ثبت کند."
        )
        return

    replied = message.reply_to_message

    # باید روی پیام خود بات ریپلای شده باشد
    if replied.from_user.id != bot.get_me().id:
        bot.reply_to(
            message,
            "❌ باید روی پیام خودم ریپلای کنی."
        )
        return

    chat_id = str(message.chat.id)

    data[chat_id] = {
        "owner_id": message.from_user.id,
        "owner_name": (
            message.from_user.first_name or
            "ارباب"
        )
    }

    save_data(data)

    bot.reply_to(
        message,
        f"🐶 صاحب جدیدم ثبت شد!\n\n"
        f"👑 صاحب من: <b>{message.from_user.first_name}</b>\n\n"
        f"من سگ تینام 🐶"
    )

    # شروع پیام‌های هر ۲ دقیقه
    start_dog_messages(message.chat.id)


# =========================
# دستور خفه
# =========================

@bot.message_handler(
    func=lambda message:
        message.text and
        message.text.strip() == "خفه"
)
def stop_dog(message):

    # فقط گروه
    if message.chat.type not in ["group", "supergroup"]:
        return

    chat_id = str(message.chat.id)

    # صاحب ثبت نشده
    if chat_id not in data:
        bot.reply_to(
            message,
            "❌ هنوز صاحبی ندارم 🐶"
        )
        return

    owner_id = data[chat_id].get("owner_id")

    # فقط صاحب
    if message.from_user.id != owner_id:
        bot.reply_to(
            message,
            "❌ فقط صاحبم می‌تونه اینو بگه 🐶"
        )
        return

    # توقف
    stop_dog_messages(message.chat.id)

    bot.reply_to(
        message,
        "چشم ارباب 🫡🐶"
    )


# =========================
# اگر روی پیام بات ریپلای شود
# =========================

@bot.message_handler(
    func=lambda message:
        message.reply_to_message is not None
)
def reply_handler(message):

    replied = message.reply_to_message

    # آیا پیام مربوط به بات است؟
    try:
        bot_id = bot.get_me().id
    except:
        return

    if not replied.from_user:
        return

    if replied.from_user.id != bot_id:
        return

    text = (message.text or "").strip()

    # اگر دستور دیگری بود، چیزی نگو
    if text in ["صاحبته", "خفه"]:
        return


# =========================
# جلوگیری از پردازش پیام‌های نامرتبط
# =========================

@bot.message_handler(
    func=lambda message: False
)
def nothing(message):
    pass


# =========================
# اجرای بات
# =========================

print("=" * 45)
print("🐶 YAG TINA BOT")
print("🤖 BOT STARTED")
print("=" * 45)

while True:
    try:
        bot.infinity_polling(
            skip_pending=True,
            timeout=30,
            long_polling_timeout=30
        )

    except Exception as e:
        print("BOT ERROR:", e)
        time.sleep(5)
