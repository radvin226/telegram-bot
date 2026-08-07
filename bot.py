import telebot
import sqlite3
import os
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime


# ================= تنظیمات =================

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")


if not BOT_TOKEN or not GEMINI_KEY:
    raise Exception(
        "BOT_TOKEN و GEMINI_KEY را داخل env قرار بده"
    )


bot = telebot.TeleBot(
    BOT_TOKEN,
    parse_mode="HTML"
)


genai.configure(
    api_key=GEMINI_KEY
)


ai = genai.GenerativeModel(
    "gemini-2.5-flash"
)



# ================= دیتابیس =================


db = sqlite3.connect(
    "sigma_users.db",
    check_same_thread=False
)

cursor = db.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY,
personality TEXT,
history TEXT
)
""")


db.commit()



def user_get(uid):

    cursor.execute(
        "SELECT * FROM users WHERE id=?",
        (uid,)
    )

    return cursor.fetchone()



def user_create(uid):

    cursor.execute(
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



def user_save(uid,personality):

    cursor.execute(
    """
    UPDATE users
    SET personality=?
    WHERE id=?
    """,
    (
        personality,
        uid
    ))

    db.commit()



def history_save(uid,text):

    cursor.execute(
    """
    UPDATE users
    SET history=?
    WHERE id=?
    """,
    (
        text[-4000:],
        uid
    ))

    db.commit()



# ================= شخصیت ها =================


personalities = {

"سیگما":
"""
تو یک شخصیت Sigma هستی.
آرام، باهوش، مستقل، کمی مرموز.
اعتماد به نفس بالا داشته باش.
""",

"رفیق":
"""
مثل یک دوست صمیمی حرف بزن.
شوخ و مهربان باش.
""",

"استاد":
"""
مثل یک استاد حرفه ای جواب بده.
آموزشی و دقیق.
""",

"هکر":
"""
مثل متخصص امنیت و برنامه نویسی رفتار کن.
فنی جواب بده.
""",

"سلطان":
"""
با اعتماد به نفس و انرژی بالا صحبت کن.
"""
}



# اضافه کردن 95 شخصیت دیگر

for i in range(1,96):

    personalities[
        f"شخصیت {i}"
    ] = f"""

شخصیت شماره {i}
رفتار منحصر به فرد داشته باش.
لحن خاص خودت را حفظ کن.

"""



# ================= دستورات =================


@bot.message_handler(commands=["start"])
def start(message):

    user_create(
        message.from_user.id
    )

    bot.reply_to(
        message,
"""
🔥 <b>Sigma Gemini AI</b> فعال شد

دستورات:

/list
لیست شخصیت ها

/set نام
تغییر شخصیت

مثال:

/set سیگما

حالا صحبت کن 😎
"""
)



@bot.message_handler(commands=["list"])
def show_list(message):

    text="\n".join(
        personalities.keys()
    )

    bot.reply_to(
        message,
        text[:4000]
    )



@bot.message_handler(commands=["set"])
def set_character(message):

    name = message.text.replace(
        "/set",
        ""
    ).strip()


    if name in personalities:

        user_create(
            message.from_user.id
        )

        user_save(
            message.from_user.id,
            name
        )


        bot.reply_to(
            message,
            f"✅ شخصیت <b>{name}</b> فعال شد"
        )

    else:

        bot.reply_to(
            message,
            "❌ این شخصیت وجود ندارد"
        )



# ================= چت AI =================


@bot.message_handler(
    func=lambda m: True
)
def chat(message):

    try:

        uid = message.from_user.id


        user_create(uid)


        data=user_get(uid)


        personality=data[1]
        history=data[2]


        prompt=f"""

تو یک ربات هوش مصنوعی هستی.

شخصیت فعال:

{personalities.get(
personality,
personalities["سیگما"]
)}


تاریخچه گفتگو:

{history}


پیام کاربر:

{message.text}


قوانین:
- طبیعی جواب بده
- شخصیت خودت را حفظ کن
- با کاربر مثل انسان صحبت کن

"""


        result=ai.generate_content(
            prompt
        )


        answer=result.text


        history_save(
            uid,
            history+
            "\nUser:"+
            message.text+
            "\nAI:"+
            answer
        )


        bot.reply_to(
            message,
            answer
        )


    except Exception as e:

        bot.reply_to(
            message,
            "⚠️ خطا در ارتباط با هوش مصنوعی"
        )

        print(e)



print(
"Sigma Gemini Bot Started..."
)


bot.infinity_polling(
    skip_pending=True
)
