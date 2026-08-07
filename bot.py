# ==========================================
# Sigma AI Telegram Bot
# HuggingFace + Inline Keyboard + Railway
# ==========================================

import telebot
from telebot import types
from huggingface_hub import InferenceClient
import sqlite3
import time


# ==========================
# CONFIG
# ==========================

BOT_TOKEN = "8956404018:AAHdIV2Jhv9FOK9Xs9qqwxsX-AKofRt-fb4" 

HF_TOKEN = "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"

OWNER_ID = 6420547446

CHANNEL = "@hvxxxklllll"


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
"مثل یک استاد حرفه‌ای آموزش بده",

"برنامه نویس":
"مثل یک متخصص برنامه نویسی جواب بده",

"شوخ":
"شوخ و سرگرم کننده باش"

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
    

    db.commit()
    # ==========================================
# INLINE KEYBOARDS
# ==========================================


def main_menu():

    kb = types.InlineKeyboardMarkup()

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
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "📚 لیست شخصیت ها",
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

    kb = types.InlineKeyboardMarkup()

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


@bot.message_handler(commands=["start"])
def start(message):

    uid = message.from_user.id

    create_user(uid)


    bot.reply_to(
        message,
        """
🔥 <b>Sigma AI فعال شد</b>

سلام 👋

من یک هوش مصنوعی با چند شخصیت هستم.

از منو انتخاب کن:
        """,
        reply_markup=main_menu()
    )



# ==========================================
# CALLBACK BUTTONS
# ==========================================


@bot.callback_query_handler(
    func=lambda call: True
)
def buttons(call):

    uid = call.from_user.id


    if call.data == "chat":

        bot.answer_callback_query(call.id)

        bot.send_message(
            uid,
            "💬 پیام خودت را بفرست..."
        )


    elif call.data == "personality":

        bot.edit_message_text(
            "🎭 یک شخصیت انتخاب کن:",
            uid,
            call.message.message_id,
            reply_markup=personality_menu()
        )


    elif call.data == "list":

        txt="🎭 شخصیت ها:\n\n"

        for p in PERSONALITIES:
            txt += "• "+p+"\n"


        bot.edit_message_text(
            txt,
            uid,
            call.message.message_id,
            reply_markup=main_menu()
        )



    elif call.data.startswith("set_"):

        name = call.data.replace(
            "set_",
            ""
        )


        set_personality(
            uid,
            name
        )


        bot.edit_message_text(
            f"✅ شخصیت تغییر کرد به:\n<b>{name}</b>",
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

    # دستورات را رد کن
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
{PERSONALITIES.get(personality)}

تاریخچه گفتگو:
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


        response = ai.chat_completion(

            model=MODEL,

            messages=[
                {
                    "role":"system",
                    "content":
                    PERSONALITIES.get(
                        personality
                    )
                },

                {
                    "role":"user",
                    "content":prompt
                }
            ],

            max_tokens=500
        )


        answer = (
            response
            .choices[0]
            .message
            .content
        )



    except Exception as e:

        print(
            "AI ERROR:",
            e
        )

        answer = """
❌ خطا در ارتباط با هوش مصنوعی

لطفاً دوباره تلاش کن.
"""



    save_history(
        uid,
        history
        +
        "\nکاربر:"
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
# COMMAND LIST
# ==========================================


@bot.message_handler(
    commands=["menu"]
)
def menu(message):

    bot.send_message(
        message.chat.id,
        "🔥 منوی اصلی:",
        reply_markup=main_menu()
    )



@bot.message_handler(
    commands=["list"]
)
def list_command(message):

    txt="🎭 شخصیت ها:\n\n"

    for p in PERSONALITIES:
        txt += "• "+p+"\n"


    bot.reply_to(
        message,
        txt
    )
    # ==========================================
# ADMIN PANEL
# ==========================================


def admin_menu():

    kb = types.InlineKeyboardMarkup()


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
        "👑 پنل مدیریت",
        reply_markup=admin_menu()
    )




# اضافه کردن دکمه های ادمین
old_buttons = buttons


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


        bot.answer_callback_query(
            call.id
        )


        bot.send_message(
            uid,
            f"👥 کاربران: {count}"
        )



    elif call.data == "broadcast":


        bot.send_message(
            uid,
            "📢 متن پیام همگانی را ارسال کن:"
        )


        bot.register_next_step_handler(
            call.message,
            broadcast_send
        )





def broadcast_send(message):

    if message.from_user.id != OWNER_ID:
        return


    text = message.text


    cur.execute(
        "SELECT id FROM users"
    )


    users = cur.fetchall()


    sent = 0


    for u in users:

        try:

            bot.send_message(
                u[0],
                text
            )

            sent += 1


        except:

            pass



    bot.reply_to(
        message,
        f"✅ ارسال شد: {sent}"
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
            timeout=60,
            long_polling_timeout=60
        )


    except Exception as e:

        print(
            "CRASH:",
            e
        )

        time.sleep(10)
