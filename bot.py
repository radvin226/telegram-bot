# ==========================================
# Sigma AI Telegram Bot
# Full Version
# Only AI API from Railway
# ==========================================

import telebot
from telebot import types
from huggingface_hub import InferenceClient
import sqlite3
import time
import os



# ==========================
# CONFIG
# ==========================


BOT_TOKEN = "PUT_YOUR_TELEGRAM_TOKEN_HERE"


OWNER_ID = 6420547446


CHANNEL = "@YOUR_CHANNEL"



# فقط این از Railway می‌آید

AI_API_KEY = os.getenv(
    "AI_API_KEY"
)


if not AI_API_KEY:

    raise Exception(
        "AI_API_KEY missing"
    )



# ==========================
# TELEGRAM
# ==========================


bot = telebot.TeleBot(
    BOT_TOKEN,
    parse_mode="HTML"
)



# ==========================
# AI
# ==========================


ai = InferenceClient(
    api_key=AI_API_KEY
)



MODEL = "Qwen/Qwen2.5-7B-Instruct"



# ==========================
# DATABASE
# ==========================


db = sqlite3.connect(
    "sigma.db",
    check_same_thread=False
)


cur = db.cursor()



cur.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY,
personality TEXT,
history TEXT
)
""")


db.commit()



# ==========================
# PERSONALITIES
# ==========================


PERSONALITIES = {


"سیگما":
"آرام، کوتاه، با اعتماد به نفس و کمی مرموز جواب بده.",


"دوست":
"مثل یک دوست صمیمی مهربان صحبت کن.",


"استاد":
"مثل یک استاد حرفه‌ای آموزش بده.",


"برنامه نویس":
"مثل یک متخصص برنامه نویسی جواب بده.",


"شوخ":
"شوخ و سرگرم کننده جواب بده."

}
# ==========================
# USER FUNCTIONS
# ==========================


def create_user(uid):

    cur.execute(
        """
        INSERT OR IGNORE INTO users
        VALUES(?,?,?)
        """,
        (
            uid,
            "سیگما",
            ""
        )
    )

    db.commit()



def get_user(uid):

    cur.execute(
        """
        SELECT *
        FROM users
        WHERE id=?
        """,
        (uid,)
    )

    return cur.fetchone()



def change_personality(uid, name):

    cur.execute(
        """
        UPDATE users
        SET personality=?
        WHERE id=?
        """,
        (
            name,
            uid
        )
    )

    db.commit()



def save_history(uid, text):

    cur.execute(
        """
        UPDATE users
        SET history=?
        WHERE id=?
        """,
        (
            text[-5000:],
            uid
        )
    )

    db.commit()



# ==========================
# INLINE MENUS
# ==========================


def main_menu():

    kb = types.InlineKeyboardMarkup(
        row_width=2
    )


    kb.add(
        types.InlineKeyboardButton(
            "🤖 چت با AI",
            callback_data="chat"
        )
    )


    kb.add(
        types.InlineKeyboardButton(
            "🎭 شخصیت",
            callback_data="personality"
        ),

        types.InlineKeyboardButton(
            "📚 لیست",
            callback_data="list"
        )
    )


    kb.add(
        types.InlineKeyboardButton(
            "👑 مدیریت",
            callback_data="admin"
        )
    )


    return kb




def personality_menu():

    kb = types.InlineKeyboardMarkup(
        row_width=2
    )


    for name in PERSONALITIES:

        kb.add(
            types.InlineKeyboardButton(
                "🎭 "+name,
                callback_data="person_"+name
            )
        )


    kb.add(
        types.InlineKeyboardButton(
            "⬅️ برگشت",
            callback_data="back"
        )
    )


    return kb




# ==========================
# START
# ==========================


@bot.message_handler(
    commands=["start"]
)
def start(message):

    uid = message.from_user.id


    create_user(uid)



    bot.reply_to(
        message,

        """
🔥 <b>Sigma AI فعال شد</b>

سلام 👋

یک شخصیت انتخاب کن یا شروع به چت کن.
        """,

        reply_markup=main_menu()
    )
    # ==========================
# BUTTON HANDLER
# ==========================


@bot.callback_query_handler(
    func=lambda call: True
)
def buttons(call):

    uid = call.from_user.id



    # چت

    if call.data == "chat":

        bot.answer_callback_query(
            call.id
        )

        bot.send_message(
            uid,
            "💬 پیام خودت را بفرست:"
        )



    # شخصیت‌ها

    elif call.data == "personality":


        bot.edit_message_text(
            "🎭 یک شخصیت انتخاب کن:",
            uid,
            call.message.message_id,
            reply_markup=personality_menu()
        )



    # لیست شخصیت‌ها

    elif call.data == "list":


        txt = "🎭 شخصیت‌های موجود:\n\n"


        for p in PERSONALITIES:

            txt += "• " + p + "\n"



        bot.edit_message_text(
            txt,
            uid,
            call.message.message_id,
            reply_markup=main_menu()
        )



    # انتخاب شخصیت

    elif call.data.startswith("person_"):


        name = call.data.replace(
            "person_",
            ""
        )


        create_user(uid)


        change_personality(
            uid,
            name
        )


        bot.edit_message_text(

            f"✅ شخصیت تغییر کرد:\n<b>{name}</b>",

            uid,

            call.message.message_id,

            reply_markup=main_menu()

        )



    # برگشت

    elif call.data == "back":


        bot.edit_message_text(

            "🔥 منوی اصلی",

            uid,

            call.message.message_id,

            reply_markup=main_menu()

        )





# ==========================
# AI CHAT
# ==========================


@bot.message_handler(
    func=lambda m: m.content_type == "text"
)
def ai_chat(message):


    if message.text.startswith("/"):
        return



    uid = message.from_user.id


    create_user(uid)


    user = get_user(uid)



    personality = user[1]

    history = user[2]



    prompt = f"""

تو یک هوش مصنوعی هستی.

شخصیت:
{PERSONALITIES[personality]}


تاریخچه:
{history}


کاربر:
{message.text}

پاسخ:
"""



    try:


        bot.send_chat_action(
            uid,
            "typing"
        )



        result = ai.chat_completion(

            model=MODEL,

            messages=[

                {
                    "role": "system",
                    "content":
                    PERSONALITIES[personality]
                },


                {
                    "role": "user",
                    "content": prompt
                }

            ],


            max_tokens=500

        )



        answer = (
            result
            .choices[0]
            .message
            .content
        )



    except Exception as e:


        print(
            "AI ERROR:",
            repr(e)
        )


        answer = """
❌ خطا در ارتباط با AI

بعداً دوباره امتحان کن.
"""



    save_history(

        uid,

        history
        +
        "\nUser: "
        +
        message.text
        +
        "\nAI: "
        +
        answer

    )



    bot.reply_to(
        message,
        answer
    )
    # ==========================
# ADMIN MENU
# ==========================


def admin_menu():

    kb = types.InlineKeyboardMarkup(
        row_width=2
    )


    kb.add(
        types.InlineKeyboardButton(
            "👥 تعداد کاربران",
            callback_data="count_users"
        )
    )


    kb.add(
        types.InlineKeyboardButton(
            "📢 پیام همگانی",
            callback_data="broadcast"
        )
    )


    kb.add(
        types.InlineKeyboardButton(
            "⬅️ برگشت",
            callback_data="back"
        )
    )


    return kb




# ==========================
# ADMIN COMMAND
# ==========================


@bot.message_handler(
    commands=["admin"]
)
def admin(message):


    if message.from_user.id != OWNER_ID:


        bot.reply_to(
            message,
            "❌ دسترسی ندارید"
        )


        return



    bot.send_message(

        message.chat.id,

        "👑 <b>پنل مدیریت</b>",

        reply_markup=admin_menu()

    )





# ==========================
# ADMIN BUTTONS
# ==========================


@bot.callback_query_handler(
    func=lambda call:
    call.data in
    [
        "admin",
        "count_users",
        "broadcast"
    ]
)
def admin_buttons(call):


    uid = call.from_user.id



    if uid != OWNER_ID:


        bot.answer_callback_query(

            call.id,

            "❌ اجازه ندارید"

        )

        return




    if call.data == "admin":


        bot.edit_message_text(

            "👑 پنل مدیریت",

            uid,

            call.message.message_id,

            reply_markup=admin_menu()

        )




    elif call.data == "count_users":


        cur.execute(
            "SELECT COUNT(*) FROM users"
        )


        count = cur.fetchone()[0]



        bot.send_message(

            uid,

            f"👥 تعداد کاربران: {count}"

        )




    elif call.data == "broadcast":


        bot.send_message(

            uid,

            "📢 متن پیام همگانی را ارسال کن:"

        )


        bot.register_next_step_handler(

            call.message,

            send_broadcast

        )





def send_broadcast(message):


    if message.from_user.id != OWNER_ID:

        return



    text = message.text



    cur.execute(
        "SELECT id FROM users"
    )


    users = cur.fetchall()


    sent = 0



    for user in users:


        try:


            bot.send_message(

                user[0],

                text

            )


            sent += 1



        except:


            pass



    bot.reply_to(

        message,

        f"✅ ارسال شد برای {sent} کاربر"

    )
    # ==========================
# RUN BOT
# ==========================


print(
    "🔥 Sigma AI BOT ONLINE"
)



while True:

    try:


        bot.infinity_polling(

            skip_pending=True,

            timeout=60,

            long_polling_timeout=60

        )



    except Exception as e:


        print(
            "CRASH:",
            e
        )


        time.sleep(10)
