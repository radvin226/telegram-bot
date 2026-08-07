# =====================================
# Sigma Gemini Telegram Bot
# Railway Version
# =====================================

import telebot
import sqlite3
import time
import google.generativeai as genai


# ==========================
# TOKEN ها
# ==========================

BOT_TOKEN = "8956404018:AAHdIV2Jhv9FOK9Xs9qqwxsX-AKofRt-fb4" 

GEMINI_KEY = "AQ.Ab8RN6KXcEAaUdLskXVFCiYL0sIemjFV3R0CFnL5zuLwHruk3w" 

OWNER_ID = 6420547446

CHANNEL = "@hvxxxklllll"



# ==========================
# Telegram
# ==========================

bot = telebot.TeleBot(
    BOT_TOKEN,
    parse_mode="HTML"
)



# ==========================
# Gemini
# ==========================

genai.configure(
    api_key=GEMINI_KEY
)


ai = genai.GenerativeModel(
    "gemini-2.0-flash"
)



# ==========================
# Database
# ==========================

db = sqlite3.connect(
    "users.db",
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
# شخصیت ها
# ==========================

PERSONALITIES = {

"سیگما":
"""
آرام، با اعتماد به نفس، باهوش و کمی مرموز صحبت کن.
""",

"دوست":
"""
مثل یک دوست صمیمی و مهربان صحبت کن.
""",

"استاد":
"""
مثل یک استاد حرفه ای و دقیق توضیح بده.
""",

"هکر":
"""
مثل متخصص برنامه نویسی و تکنولوژی جواب بده.
""",

"شوخ":
"""
شوخ و سرگرم کننده باش.
"""

}



for i in range(1,101):

    PERSONALITIES[
        f"شخصیت {i}"
    ] = f"""
تو شخصیت شماره {i} هستی.
"""


# ==========================
# User
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
    ))

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
    ))

    db.commit()



# ==========================
# Start
# ==========================


@bot.message_handler(
commands=["start"]
)
def start(message):

    create_user(
        message.from_user.id
    )


    bot.reply_to(
        message,
"""
🔥 <b>Sigma Gemini AI</b>

فعال شد 😎


دستورات:

/list
لیست شخصیت ها


/set نام
تغییر شخصیت


ساخت تصویر:
برای تصویر


/admin
پنل مالک
"""
    )



# ==========================
# List
# ==========================


@bot.message_handler(
commands=["list"]
)
def list_personality(message):

    text="🎭 شخصیت ها:\n\n"


    for p in PERSONALITIES:

        text += "• "+p+"\n"


    bot.reply_to(
        message,
        text[:4000]
    )



# ==========================
# Set personality
# ==========================


@bot.message_handler(
commands=["set"]
)
def set_character(message):

    uid=message.from_user.id


    name=message.text.replace(
        "/set",
        ""
    ).strip()



    if name in PERSONALITIES:

        create_user(uid)

        set_personality(
            uid,
            name
        )


        bot.reply_to(
            message,
            "✅ شخصیت تغییر کرد: "+name
        )

    else:

        bot.reply_to(
            message,
            "❌ شخصیت وجود ندارد"
        )



# ==========================
# Chat Gemini
# ==========================


@bot.message_handler(
func=lambda m:
m.content_type=="text"
)
def chat(message):


    if message.text.startswith("/"):

        return


    uid=message.from_user.id

    create_user(uid)


    data=get_user(uid)


    personality=data[1]


    prompt=f"""

شخصیت:
{PERSONALITIES[personality]}


کاربر:
{message.text}


جواب بده:
"""


    try:

        result=ai.generate_content(
            prompt
        )


        answer=result.text


    except Exception as e:

        answer="خطا در Gemini"


        print(e)



    bot.reply_to(
        message,
        answer
    )



# ==========================
# Image
# ==========================


@bot.message_handler(
func=lambda m:
m.text and
m.text.startswith("ساخت تصویر:")
)
def image(message):

    prompt=message.text.replace(
        "ساخت تصویر:",
        ""
    )


    bot.reply_to(
        message,
f"""
🎨 درخواست تصویر:

{prompt}

برای فعال شدن ساخت تصویر واقعی باید مدل Image Generation روی API فعال باشد.
"""
    )



# ==========================
# Admin
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



    cur.execute(
        "SELECT COUNT(*) FROM users"
    )


    count=cur.fetchone()[0]


    bot.reply_to(
        message,
f"""
👑 پنل مالک

کاربران:
{count}
"""
    )



# ==========================
# Run
# ==========================


print(
"Sigma Bot Started"
)


while True:

    try:

        bot.infinity_polling(
            skip_pending=True
        )


    except Exception as e:

        print(e)

        time.sleep(5)
