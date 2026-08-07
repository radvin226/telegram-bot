# ==========================================
# Sigma AI Telegram Bot
# Railway Secure Version
# HuggingFace + Inline Keyboard
# ==========================================

import os
import time
import sqlite3
import telebot

from telebot import types
from huggingface_hub import InferenceClient


# ==========================
# CONFIG
# ==========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

OWNER_ID = int(
    os.getenv(
        "OWNER_ID",
        "0"
    )
)

CHANNEL = os.getenv(
    "CHANNEL",
    ""
)


if not BOT_TOKEN:
    raise Exception(
        "BOT_TOKEN missing"
    )


if not HF_TOKEN:
    raise Exception(
        "HF_TOKEN missing"
    )



bot = telebot.TeleBot(
    BOT_TOKEN,
    parse_mode="HTML"
)



# ==========================
# AI
# ==========================

ai = InferenceClient(
    api_key=HF_TOKEN
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
"آرام، با اعتماد به نفس، کوتاه و مرموز جواب بده",

"دوست":
"مثل یک دوست صمیمی مهربان صحبت کن",

"استاد":
"مثل یک استاد حرفه‌ای توضیح بده",

"برنامه نویس":
"مثل متخصص برنامه نویسی جواب بده",

"شوخ":
"شوخ و سرگرم کننده باش"

}



# ==========================
# USER
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



def set_personality(uid,name):

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



def save_history(uid,text):

    cur.execute(
        """
        UPDATE users
        SET history=?
        WHERE id=?
        """,
        (
            text[-4000:],
            uid
        )
    )
# ==========================================
# INLINE KEYBOARDS
# ==========================================


def main_menu():

    kb = types.InlineKeyboardMarkup(row_width=2)

    kb.add(
        types.InlineKeyboardButton(
            "🤖 چت با Sigma AI",
            callback_data="chat"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "🎭 تغییر شخصیت",
            callback_data="personality"
        ),
        types.InlineKeyboardButton(
            "📚 شخصیت‌ها",
            callback_data="list"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "👑 پنل مدیریت",
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
                callback_data="set_"+name
            )
        )

    kb.add(
        types.InlineKeyboardButton(
            "⬅️ برگشت",
            callback_data="back"
        )
    )

    return kb



# ==========================================
# START
# ==========================================


@bot.message_handler(
    commands=["start"]
)
def start(message):

    uid = message.from_user.id

    create_user(uid)


    bot.reply_to(
        message,
        """
🔥 <b>Sigma AI روشن شد</b>

سلام 👋

من یک دستیار هوش مصنوعی با چند شخصیت هستم.

یکی را انتخاب کن:
        """,
        reply_markup=main_menu()
    )



# ==========================================
# BUTTON HANDLER
# ==========================================


@bot.callback_query_handler(
    func=lambda call: True
)
def buttons(call):

    uid = call.from_user.id


    if call.data == "chat":

        bot.answer_callback_query(
            call.id
        )

        bot.send_message(
            uid,
            "💬 پیام خودت را ارسال کن:"
        )


    elif call.data == "personality":

        bot.edit_message_text(
            "🎭 شخصیت را انتخاب کن:",
            uid,
            call.message.message_id,
            reply_markup=personality_menu()
        )



    elif call.data == "list":

        text = "🎭 لیست شخصیت‌ها:\n\n"

        for p in PERSONALITIES:

            text += "• "+p+"\n"


        bot.edit_message_text(
            text,
            uid,
            call.message.message_id,
            reply_markup=main_menu()
        )



    elif call.data.startswith("set_"):

        name = call.data.replace(
            "set_",
            ""
        )


        create_user(uid)


        set_personality(
            uid,
            name
        )


        bot.edit_message_text(
            f"✅ شخصیت شد:\n<b>{name}</b>",
            uid,
            call.message.message_id,
            reply_markup=main_menu()
        )



    elif call.data == "back":

        bot.edit_message_text(
            "🔥 منوی اصلی",
            uid,
            call.message.message_id,
            reply_markup=main_menu()
        )
        # ==========================================
# AI CHAT
# ==========================================


@bot.message_handler(
    func=lambda m: m.content_type == "text"
)
def chat(message):

    # رد کردن دستورات
    if message.text.startswith("/"):
        return


    uid = message.from_user.id


    create_user(uid)


    user = get_user(uid)


    personality = user[1]

    history = user[2]



    prompt = f"""
شخصیت:
{PERSONALITIES.get(personality)}

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
                    PERSONALITIES.get(
                        personality
                    )
                },

                {
                    "role": "user",
                    "content": prompt
                }

            ],

            max_tokens=500,

            temperature=0.7
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
❌ خطا در اتصال به هوش مصنوعی

لطفاً دوباره امتحان کن.
"""



    save_history(
        uid,
        history
        +
        "\nUSER:"
        +
        message.text
        +
        "\nAI:"
        +
        answer
    )



    bot.reply_to(
        message,
        answer
    )





# ==========================================
# COMMANDS
# ==========================================


@bot.message_handler(
    commands=["menu"]
)
def menu(message):

    bot.send_message(
        message.chat.id,
        "🔥 منوی اصلی",
        reply_markup=main_menu()
    )



@bot.message_handler(
    commands=["list"]
)
def list_cmd(message):

    text = "🎭 شخصیت‌ها:\n\n"


    for p in PERSONALITIES:

        text += "• " + p + "\n"


    bot.reply_to(
        message,
        text
    )
    # ==========================================
# ADMIN PANEL
# ==========================================


def admin_menu():

    kb = types.InlineKeyboardMarkup(
        row_width=2
    )


    kb.add(
        types.InlineKeyboardButton(
            "👥 تعداد کاربران",
            callback_data="users_count"
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





# ==========================================
# ADMIN BUTTONS
# ==========================================


@bot.callback_query_handler(
    func=lambda call: call.data in [
        "admin",
        "users_count",
        "broadcast"
    ]
)
def admin_buttons(call):


    uid = call.from_user.id



    if uid != OWNER_ID:

        bot.answer_callback_query(
            call.id,
            "❌ دسترسی ندارید"
        )

        return




    if call.data == "admin":


        bot.edit_message_text(
            "👑 پنل مدیریت",
            uid,
            call.message.message_id,
            reply_markup=admin_menu()
        )




    elif call.data == "users_count":


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
            "📢 متن پیام را بفرست:"
        )


        bot.register_next_step_handler(
            call.message,
            broadcast
        )





def broadcast(message):


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
        f"✅ ارسال شد برای {sent} نفر"
    )





# ==========================================
# RUN
# ==========================================


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
    db.commit()
