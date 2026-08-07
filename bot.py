# ==========================================
# Sigma Gemini Telegram Bot
# Part 1/10
# ==========================================

import telebot
import sqlite3
import os
import time
import json
import google.generativeai as genai

from telebot import types


# ==========================
# تنظیمات اصلی
# ==========================

BOT_TOKEN = "8956404018:AAHdIV2Jhv9FOK9Xs9qqwxsX-AKofRt-fb4"

GEMINI_KEY = "AQ.Ab8RN6KXcEAaUdLskXVFCiYL0sIemjFV3R0CFnL5zuLwHruk3w"

OWNER_ID = 6420547446   # آیدی عددی خودت

CHANNEL = "@hvxxxklllll"


# ==========================
# اتصال تلگرام
# ==========================

bot = telebot.TeleBot(
    BOT_TOKEN,
    parse_mode="HTML"
)


# ==========================
# اتصال Gemini
# ==========================

genai.configure(
    api_key=GEMINI_KEY
)


# مدل چت اصلی
chat_model = genai.GenerativeModel(
    "gemini-3.6-flash"
)


# مدل قوی‌تر برای درخواست‌های سنگین
pro_model = genai.GenerativeModel(
    "gemini-3.1-pro"
)



# ==========================
# دیتابیس داخلی
# ==========================

db = sqlite3.connect(
    "sigma_database.db",
    check_same_thread=False
)

cursor = db.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS users(

user_id INTEGER PRIMARY KEY,

personality TEXT DEFAULT 'سیگما',

history TEXT DEFAULT '',

joined INTEGER DEFAULT 0

)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS groups(

group_id INTEGER PRIMARY KEY,

enabled INTEGER DEFAULT 1

)
""")


db.commit()



print("Database Loaded...")
# ==========================================
# Part 2/10
# Personality System
# ==========================================


# ==========================
# شخصیت های اصلی
# ==========================

PERSONALITIES = {

"سیگما":
"""
تو یک شخصیت Sigma هستی.
آرام، با اعتماد به نفس، باهوش و کمی مرموز صحبت کن.
جواب ها کوتاه ولی تاثیرگذار باشند.
""",


"دوست":
"""
مثل یک دوست صمیمی رفتار کن.
مهربان، شوخ و راحت صحبت کن.
""",


"استاد":
"""
مثل یک استاد حرفه ای جواب بده.
آموزشی، دقیق و کامل توضیح بده.
""",


"هکر":
"""
مثل یک متخصص برنامه نویسی و امنیت رفتار کن.
فنی و حرفه ای صحبت کن.
""",


"انگیزشی":
"""
مثل یک مربی انگیزشی صحبت کن.
انرژی مثبت بده.
""",


"سلطان":
"""
با اعتماد به نفس بالا و لحن قدرتمند صحبت کن.
"""
}



# ==========================
# ساخت 100 شخصیت
# ==========================

extra_personalities = [

"گیمر",
"دانشمند",
"پزشک",
"وکیل",
"کارآفرین",
"کمدین",
"کارآگاه",
"نویسنده",
"معلم",
"مربی",
"منتقد",
"فیلسوف",
"هنرمند",
"خواننده",
"رپر",
"بدنساز",
"ورزشکار",
"خلبان",
"مهندس",
"طراح",
"مدیر",
"رهبر",
"آشپز",
"مسافر",
"کاوشگر",
"تاریخ دان",
"روانشناس",
"اقتصاددان",
"بازاریاب",
"فروشنده",
"برنامه نویس",
"طراح بازی",
"منتور",
"مشاور",
"شوخ",
"جدی",
"رسمی",
"خجالتی",
"جسور",
"رازآلود",
"آینده نگر",
"منتقد فیلم",
"خبرنگار",
"تحلیلگر",
"استراتژیست",
"مخترع",
"خلاق",
"نابغه",
"ساده گو"
]


for name in extra_personalities:

    PERSONALITIES[name] = f"""

تو شخصیت {name} هستی.

با سبک مخصوص این شخصیت جواب بده.
شخصیت خودت را حفظ کن.

"""



# تکمیل تا 100 عدد

for i in range(
    len(PERSONALITIES)+1,
    101
):

    PERSONALITIES[
        f"شخصیت {i}"
    ] = f"""

تو شخصیت شماره {i} هستی.
رفتار منحصر به فرد داشته باش.

"""




# ==========================
# توابع کاربران
# ==========================


def create_user(uid):

    cursor.execute(
    """
    INSERT OR IGNORE INTO users
    (user_id,personality,history,joined)

    VALUES(?,?,?,?)
    """,
    (
        uid,
        "سیگما",
        "",
        0
    ))

    db.commit()



def get_user(uid):

    cursor.execute(
    """
    SELECT *
    FROM users
    WHERE user_id=?
    """,
    (uid,)
    )

    return cursor.fetchone()



def set_personality(uid,name):

    cursor.execute(
    """
    UPDATE users

    SET personality=?

    WHERE user_id=?
    """,
    (
        name,
        uid
    ))

    db.commit()



def save_history(uid,text):

    cursor.execute(
    """
    UPDATE users

    SET history=?

    WHERE user_id=?
    """,
    (
        text[-5000:],
        uid
    ))

    db.commit()



print("Personality System Loaded...")
# ==========================================
# Part 3/10
# Start Commands & Channel Join
# ==========================================


# ==========================
# بررسی عضویت کانال
# ==========================

def check_join(user_id):

    try:

        member = bot.get_chat_member(
            CHANNEL,
            user_id
        )

        if member.status in [
            "member",
            "administrator",
            "creator"
        ]:
            return True

        return False


    except Exception:

        # اگر نتوانست بررسی کند
        # اجازه می دهد تا بات کار کند

        return True





# ==========================
# پیام عضویت
# ==========================


def join_message():

    return """
🔒 برای استفاده از ربات ابتدا عضو کانال شوید:

👇 کانال:
https://t.me/hvxxxklllll

بعد دوباره /start بزنید.
"""





# ==========================
# Start
# ==========================


@bot.message_handler(
    commands=["start"]
)
def start(message):


    uid = message.from_user.id


    create_user(uid)


    # فقط در پیوی چک شود

    if message.chat.type == "private":


        if not check_join(uid):

            bot.reply_to(
                message,
                join_message()
            )

            return



    bot.reply_to(
        message,
"""
🔥 <b>Sigma Gemini AI فعال شد</b>


قابلیت ها:

🧠 چت هوش مصنوعی

🎭 تغییر شخصیت:
/set سیگما


📜 لیست شخصیت ها:
/list


🎨 ساخت تصویر:

ساخت تصویر: متن تصویر


⚙️ مدیریت:
/admin


موفق باشی 😎
"""
)





# ==========================
# لیست شخصیت ها
# ==========================


@bot.message_handler(
    commands=["list"]
)
def personality_list(message):


    text = "🎭 شخصیت های موجود:\n\n"


    for p in PERSONALITIES.keys():

        text += "• " + p + "\n"


    bot.reply_to(
        message,
        text[:4000]
    )





# ==========================
# تغییر شخصیت
# ==========================


@bot.message_handler(
    commands=["set"]
)
def change_personality(message):


    uid = message.from_user.id


    name = message.text.replace(
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

            f"""
✅ شخصیت تغییر کرد

🎭 شخصیت فعال:
<b>{name}</b>

حالا با همین حالت با من صحبت کن.
"""
        )


    else:


        bot.reply_to(
            message,

            """
❌ این شخصیت وجود ندارد

از /list استفاده کن.
"""
        )





print("Commands Loaded...")
# ==========================================
# Part 4/10
# Gemini Chat Engine
# ==========================================


# ==========================
# ساخت پرامپت شخصیت
# ==========================


def build_prompt(uid, user_text):


    data = get_user(uid)


    if data:

        personality = data[1]

        history = data[2]


    else:

        personality = "سیگما"

        history = ""



    style = PERSONALITIES.get(
        personality,
        PERSONALITIES["سیگما"]
    )



    prompt = f"""

تو یک هوش مصنوعی داخل تلگرام هستی.

شخصیت فعال:

{style}


قوانین:

- همیشه شخصیت را حفظ کن
- طبیعی و انسانی جواب بده
- اگر کاربر فارسی صحبت کرد فارسی جواب بده
- جواب های مفید بده
- توهین بی دلیل نکن


تاریخچه گفتگو:

{history}



پیام جدید کاربر:

{user_text}


پاسخ:

"""


    return prompt





# ==========================
# انتخاب مدل
# ==========================


def ask_gemini(uid,text):


    try:


        prompt = build_prompt(
            uid,
            text
        )


        # حالت عادی

        result = chat_model.generate_content(
            prompt
        )


        return result.text



    except Exception as e:


        print(
            "Gemini Error:",
            e
        )


        try:


            # اگر مدل اصلی مشکل داشت

            result = pro_model.generate_content(
                prompt
            )


            return result.text



        except:


            return """
⚠️ ارتباط با هوش مصنوعی مشکل دارد.
بعداً دوباره امتحان کن.
"""





# ==========================
# ذخیره گفتگو
# ==========================


def add_chat_history(
        uid,
        user,
        ai
):


    data = get_user(uid)



    old = ""

    if data:

        old = data[2]



    new_history = old + f"""

کاربر:
{user}

ربات:
{ai}

"""



    save_history(
        uid,
        new_history
    )






# ==========================
# دریافت پیام های متنی
# ==========================


@bot.message_handler(
    func=lambda m:
    m.content_type == "text"
)
def normal_chat(message):


    uid = message.from_user.id



    # دستورات را رد کن

    if message.text.startswith("/"):

        return



    create_user(uid)



    # بررسی عضویت فقط پیوی

    if message.chat.type == "private":

        if not check_join(uid):

            bot.reply_to(
                message,
                join_message()
            )

            return




    bot.send_chat_action(
        message.chat.id,
        "typing"
    )



    answer = ask_gemini(
        uid,
        message.text
    )



    add_chat_history(
        uid,
        message.text,
        answer
    )



    bot.reply_to(
        message,
        answer
    )




print("Gemini Engine Loaded...")
# ==========================================
# Part 5/10
# Image Generation System
# ==========================================


# ==========================
# مدل تصویر
# ==========================

try:

    image_model = genai.GenerativeModel(
        "nano-banana-pro"
    )

except Exception:

    image_model = None





# ==========================
# ساخت تصویر
# ==========================


def generate_image(prompt):


    try:


        if image_model is None:

            return None



        response = image_model.generate_content(
            prompt
        )


        return response



    except Exception as e:


        print(
            "IMAGE ERROR:",
            e
        )


        return None






# ==========================
# دستور تصویر
# ==========================


@bot.message_handler(
    func=lambda m:
    m.text and
    m.text.startswith("ساخت تصویر:")
)
def create_image(message):


    prompt = message.text.replace(
        "ساخت تصویر:",
        ""
    ).strip()



    if not prompt:


        bot.reply_to(
            message,

            """
❌ پرامپت تصویر خالی است

مثال:

ساخت تصویر: یک شهر آینده با نور نئون
"""
        )

        return



    bot.send_chat_action(
        message.chat.id,
        "upload_photo"
    )



    result = generate_image(
        prompt
    )



    if result:


        try:


            # اگر API تصویر خروجی فایل بدهد

            image = result.parts[0]


            bot.send_photo(
                message.chat.id,
                image
            )



        except Exception:


            bot.reply_to(
                message,

"""
✅ درخواست تصویر ارسال شد

ولی فرمت خروجی این مدل با نسخه فعلی API سازگار نیست.
"""
            )


    else:


        bot.reply_to(
            message,

"""
⚠️ ساخت تصویر در این API فعال نیست
یا سهمیه آن تمام شده است.

مدل تصویر را در Google AI Studio فعال کن.
"""
        )





print("Image System Loaded...")
# ==========================================
# Part 6/10
# Group System
# ==========================================


# ==========================
# ذخیره گروه
# ==========================


def save_group(group_id):


    cursor.execute(
    """
    INSERT OR IGNORE INTO groups
    (group_id,enabled)

    VALUES(?,?)
    """,
    (
        group_id,
        1
    ))

    db.commit()






# ==========================
# بررسی ادمین بودن ربات
# ==========================


def bot_is_admin(chat_id):


    try:


        me = bot.get_me()


        member = bot.get_chat_member(
            chat_id,
            me.id
        )


        if member.status in [
            "administrator",
            "creator"
        ]:

            return True



        return False



    except Exception as e:


        print(
            "ADMIN CHECK ERROR",
            e
        )


        return False






# ==========================
# ورود به گروه
# ==========================


@bot.message_handler(
    content_types=[
        "new_chat_members"
    ]
)
def new_member(message):


    for user in message.new_chat_members:


        if user.id == bot.get_me().id:


            save_group(
                message.chat.id
            )



            if bot_is_admin(
                message.chat.id
            ):



                bot.send_message(
                    message.chat.id,

"""
🔥 <b>گوه خور اضافی فعال شد</b> 😎


ربات با موفقیت فعال شد.


قابلیت ها:

🧠 چت هوش مصنوعی
🎭 شخصیت ها
🧹 مدیریت پیام
🔇 سکوت کاربران
🚫 حذف کاربران


برای کار کردن مدیریت،
ربات باید ادمین کامل گروه باشد.
"""
                )


            else:


                bot.send_message(
                    message.chat.id,

"""
⚠️ ربات اضافه شد.

برای فعال شدن مدیریت گروه،
من را ادمین کنید.
"""
                )






# ==========================
# پیام های گروه
# ==========================


@bot.message_handler(
    func=lambda m:
    m.chat.type in
    [
        "group",
        "supergroup"
    ]
)
def group_chat(message):


    save_group(
        message.chat.id
    )


    # فعلا فقط پاسخ هوشمند

    text = message.text



    if not text:

        return



    # اگر ربات منشن شد

    if (
        "@"+bot.get_me().username
        in text
    ):


        clean = text.replace(
            "@"+bot.get_me().username,
            ""
        )


        answer = ask_gemini(
            message.from_user.id,
            clean
        )


        bot.reply_to(
            message,
            answer
        )





print("Group System Loaded...")
# ==========================================
# Part 7/10
# Group Management
# ==========================================



# ==========================
# بررسی ادمین بودن کاربر
# ==========================


def user_is_admin(chat_id, user_id):

    try:

        member = bot.get_chat_member(
            chat_id,
            user_id
        )


        return member.status in [
            "administrator",
            "creator"
        ]


    except:


        return False





# ==========================
# بررسی دسترسی ربات
# ==========================


def can_manage(chat_id):


    return bot_is_admin(chat_id)







# ==========================
# حذف پیام
# دستور:
# /del
# ==========================


@bot.message_handler(
    commands=["del"]
)
def delete_message(message):


    if message.chat.type == "private":

        return



    if not user_is_admin(
        message.chat.id,
        message.from_user.id
    ):

        return



    if not can_manage(
        message.chat.id
    ):

        bot.reply_to(
            message,
            "❌ ربات ادمین نیست"
        )

        return



    try:


        bot.delete_message(
            message.chat.id,
            message.reply_to_message.message_id
        )


    except:


        bot.reply_to(
            message,
            "❌ روی پیام ریپلای کن"
        )








# ==========================
# سکوت کاربر
# دستور:
# /mute
# ==========================


@bot.message_handler(
    commands=["mute"]
)
def mute_user(message):


    if message.chat.type == "private":

        return



    if not user_is_admin(
        message.chat.id,
        message.from_user.id
    ):

        return



    if not message.reply_to_message:

        bot.reply_to(
            message,
            "روی پیام کاربر ریپلای کن"
        )

        return



    user_id = (
        message
        .reply_to_message
        .from_user
        .id
    )


    try:


        bot.restrict_chat_member(

            message.chat.id,

            user_id,

            permissions=types.ChatPermissions(
                can_send_messages=False
            )
        )


        bot.reply_to(
            message,
            "🔇 کاربر ساکت شد"
        )


    except Exception as e:


        print(e)








# ==========================
# حذف کاربر
# دستور:
# /ban
# ==========================


@bot.message_handler(
    commands=["ban"]
)
def ban_user(message):


    if message.chat.type == "private":

        return



    if not user_is_admin(
        message.chat.id,
        message.from_user.id
    ):

        return



    if not message.reply_to_message:

        bot.reply_to(
            message,
            "روی پیام کاربر ریپلای کن"
        )

        return



    user_id = (
        message
        .reply_to_message
        .from_user
        .id
    )



    try:


        bot.ban_chat_member(

            message.chat.id,

            user_id
        )


        bot.reply_to(
            message,
            "🚫 کاربر حذف شد"
        )



    except Exception as e:


        print(e)





# ==========================
# پاکسازی پیام ها
# دستور:
# /clear تعداد
# ==========================


@bot.message_handler(
    commands=["clear"]
)
def clear_messages(message):


    if not user_is_admin(
        message.chat.id,
        message.from_user.id
    ):

        return



    try:


        count = int(
            message.text.split()[1]
        )


    except:


        count = 10



    for i in range(count):

        try:

            bot.delete_message(
                message.chat.id,
                message.message_id-i
            )

        except:

            pass






print("Group Management Loaded...")
# ==========================================
# Part 8/10
# Owner Admin Panel
# ==========================================


# ==========================
# چک مالک
# ==========================


def is_owner(user_id):

    return user_id == OWNER_ID






# ==========================
# آمار کاربران
# ==========================


def users_count():

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    return cursor.fetchone()[0]



def groups_count():

    cursor.execute(
        "SELECT COUNT(*) FROM groups"
    )

    return cursor.fetchone()[0]






# ==========================
# دستور ادمین
# ==========================


@bot.message_handler(
    commands=["admin"]
)
def admin_panel(message):


    uid = message.from_user.id



    if not is_owner(uid):

        bot.reply_to(
            message,
            """
❌ شما دسترسی ادمین ندارید.
"""
        )

        return




    bot.reply_to(
        message,

"""
👑 <b>پنل مدیریت ربات</b>


📊 آمار:

👤 کاربران:
{}


👥 گروه ها:
{}


دستورات:

/stats
نمایش آمار

/broadcast متن
ارسال پیام همگانی


⚙️ مدیریت فقط برای مالک فعال است.
""".format(
    users_count(),
    groups_count()
)

)








# ==========================
# آمار
# ==========================


@bot.message_handler(
    commands=["stats"]
)
def stats(message):


    if not is_owner(
        message.from_user.id
    ):

        return



    bot.reply_to(
        message,

f"""
📊 آمار ربات:


👤 کاربران:
{users_count()}


👥 گروه ها:
{groups_count()}


🤖 وضعیت:
فعال
"""
)







# ==========================
# پیام همگانی
# ==========================


@bot.message_handler(
    commands=["broadcast"]
)
def broadcast(message):


    if not is_owner(
        message.from_user.id
    ):

        return



    text = message.text.replace(
        "/broadcast",
        ""
    ).strip()



    if not text:


        bot.reply_to(
            message,
            "متن پیام را وارد کن"
        )

        return



    cursor.execute(
        "SELECT user_id FROM users"
    )


    users = cursor.fetchall()



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

        f"""
✅ پیام ارسال شد

تعداد:
{sent}
"""
    )




print("Admin Panel Loaded...")
# ==========================================
# Part 9/10
# Settings System & Error Handler
# ==========================================



# ==========================
# جدول تنظیمات
# ==========================


cursor.execute("""
CREATE TABLE IF NOT EXISTS settings(

key TEXT PRIMARY KEY,

value TEXT

)
""")


db.commit()






# ==========================
# ذخیره تنظیم
# ==========================


def set_setting(key,value):


    cursor.execute(
    """
    INSERT OR REPLACE INTO settings

    (key,value)

    VALUES(?,?)
    """,
    (
        key,
        value
    ))


    db.commit()






# ==========================
# گرفتن تنظیم
# ==========================


def get_setting(key,default=""):


    cursor.execute(
    """
    SELECT value
    FROM settings
    WHERE key=?
    """,
    (
        key,
    ))


    result = cursor.fetchone()



    if result:

        return result[0]


    return default






# ==========================
# متن شروع قابل تغییر
# ==========================


if not get_setting("start_text"):


    set_setting(
        "start_text",

"""
🔥 Sigma Gemini AI فعال شد

با من صحبت کن 😎
"""
    )







# ==========================
# تغییر متن شروع
# فقط مالک
# ==========================


@bot.message_handler(
    commands=["setstart"]
)
def change_start(message):


    if not is_owner(
        message.from_user.id
    ):

        return



    text = message.text.replace(
        "/setstart",
        ""
    ).strip()



    if not text:


        bot.reply_to(
            message,
            "متن جدید را بنویس"
        )

        return




    set_setting(
        "start_text",
        text
    )


    bot.reply_to(
        message,
        "✅ متن شروع تغییر کرد"
    )








# ==========================
# تغییر شخصیت پیش فرض
# ==========================


@bot.message_handler(
    commands=["default"]
)
def default_personality(message):


    if not is_owner(
        message.from_user.id
    ):

        return



    name = message.text.replace(
        "/default",
        ""
    ).strip()



    if name in PERSONALITIES:


        set_setting(
            "default_personality",
            name
        )


        bot.reply_to(
            message,
            f"✅ شخصیت پیش فرض شد: {name}"
        )



    else:


        bot.reply_to(
            message,
            "❌ شخصیت پیدا نشد"
        )








# ==========================
# مدیریت خطای کلی
# ==========================


@bot.middleware_handler(
    update_types=[
        "message"
    ]
)
def error_middleware(bot_instance, message):

    try:

        pass


    except Exception as e:


        print(
            "SYSTEM ERROR:",
            e
        )






print("Settings System Loaded...")
# ==========================================
# Part 10/10
# Bot Runner
# ==========================================



# ==========================
# تست اتصال Gemini
# ==========================


def test_ai():

    try:

        result = chat_model.generate_content(
            "سلام"
        )


        if result.text:

            print(
                "Gemini Connected ✅"
            )


    except Exception as e:


        print(
            "Gemini Error ❌",
            e
        )






# ==========================
# پیام خطا برای کرش نکردن
# ==========================


def safe_polling():


    while True:


        try:


            print(
                """
========================

🔥 Sigma Gemini Bot Started

========================
"""
            )


            test_ai()



            bot.infinity_polling(
                skip_pending=True,
                timeout=60,
                long_polling_timeout=60
            )



        except Exception as e:


            print(
                "BOT CRASH:",
                e
            )


            time.sleep(5)







# ==========================
# اجرا
# ==========================


if __name__ == "__main__":


    safe_polling()
