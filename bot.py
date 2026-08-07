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


model = genai.GenerativeModel(
    "gemini-1.5-flash"
)



# ==========================
# Database
# ==========================

db = sqlite3.connect(
    "sigma.db",
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



# ==========================
# Personalities
# ==========================


PERSONALITIES = {

"سیگما":
"آرام، با اعتماد به نفس، مرموز و کوتاه جواب بده.",

"دوست":
"مثل دوست صمیمی مهربان صحبت کن.",

"استاد":
"مثل استاد حرفه ای و آموزشی جواب بده.",

"هکر":
"مثل متخصص تکنولوژی و برنامه نویسی جواب بده.",

"شوخ":
"شوخ و سرگرم کننده باش."

}



for i in range(1,101):

    PERSONALITIES[
        f"شخصیت {i}"
    ] = f"تو شخصیت شماره {i} هستی."




# ==========================
# User
# ==========================


def create_user(uid):

    cursor.execute(
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

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE id=?
        """,
        (uid,)
    )

    return cursor.fetchone()



def update_personality(uid,name):

    cursor.execute(
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



def update_history(uid,text):

    cursor.execute(
        """
        UPDATE users
        SET history=?
        WHERE id=?
        """,
        (
            text[-3000:],
            uid
        )
    )

    db.commit()



# ==========================
# Channel
# ==========================


def check_channel(uid):

    try:

        member = bot.get_chat_member(
            CHANNEL,
            uid
        )

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except:

        return True



# ==========================
# START
# ==========================


@bot.message_handler(commands=["start"])
def start(message):

    uid = message.from_user.id

    create_user(uid)


    if message.chat.type=="private":

        if not check_channel(uid):

            bot.reply_to(
                message,
                "🔒 اول عضو کانال شو:\n\nhttps://t.me/hvxxxklllll"
            )

            return


    bot.reply_to(
        message,
"""
🔥 <b>Sigma AI فعال شد</b>

دستورات:

/list
لیست شخصیت ها

/set نام
تغییر شخصیت

ساخت تصویر:
ساخت تصویر آزمایشی

/admin
پنل مالک
"""
    )



# ==========================
# LIST
# ==========================


@bot.message_handler(commands=["list"])
def list_cmd(message):

    txt="🎭 شخصیت ها:\n\n"

    for x in PERSONALITIES:

        txt += "• "+x+"\n"


    bot.reply_to(
        message,
        txt[:4000]
    )



# ==========================
# SET
# ==========================


@bot.message_handler(commands=["set"])
def set_cmd(message):

    uid=message.from_user.id

    name=message.text.replace(
        "/set",
        ""
    ).strip()


    if name in PERSONALITIES:

        create_user(uid)

        update_personality(
            uid,
            name
        )


        bot.reply_to(
            message,
            "✅ شخصیت تغییر کرد"
        )

    else:

        bot.reply_to(
            message,
            "❌ پیدا نشد"



        )



# ==========================
# CHAT
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


    user=get_user(uid)


    personality=user[1]

    history=user[2]



    prompt=f"""
شخصیت:
{PERSONALITIES[personality]}

تاریخچه:
{history}

کاربر:
{message.text}
"""


    try:

        result=model.generate_content(
            prompt
        )


        answer=result.text


    except Exception as e:

        print(e)

        answer="❌ خطای Gemini"



    update_history(
        uid,
        history+"\n"+message.text+"\n"+answer
    )


    bot.reply_to(
        message,
        answer
    )



# ==========================
# ADMIN
# ==========================


@bot.message_handler(commands=["admin"])
def admin(message):

    if message.from_user.id != OWNER_ID:

        bot.reply_to(
            message,
            "❌ دسترسی ندارید"
        )

        return


    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    count=cursor.fetchone()[0]


    bot.reply_to(
        message,
        f"👑 کاربران: {count}"
    )



# ==========================
# RUN
# ==========================


print("BOT ONLINE")


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
