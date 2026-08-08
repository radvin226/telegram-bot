# =========================================================
# 🐮 GOKHOR EZAFI BOT
# Rubika + Hugging Face
# =========================================================

from rubpy.bot import BotClient, filters
from rubpy.bot.models import Update
from huggingface_hub import InferenceClient

import json
import os
import asyncio


# =========================================================
# CONFIG
# =========================================================
BOT_TOKEN = "CBDJAI0PCBTZSKKHMJTTVUPFUDZQVZXFLQGRVMQCKNXCQRSFRQMTJFEPPZDAJQFF"

HF_TOKEN = "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"

MODEL = "meta-llama/Llama-3.3-70B-Instruct"

DB_FILE = "database.json"

OWNER_USERNAME = "@radvinhha"

DEFAULT_CHANNEL = "rubika.ir/linkgokh"


# =========================================================
# DATABASE
# =========================================================

def default_database():

    return {
        "users": [],
        "admins": [],

        "groups": {},

        "settings": {

            "channel": DEFAULT_CHANNEL,

            "start_message":
                " رفیق 😎🐮\n\n"
                "گوخور اضافی هستم!\n"
                "بگو ببینم چه کاری داری 😂",

            "global_serious": False
        }
    }


def load_database():

    if not os.path.exists(DB_FILE):

        data = default_database()

        with open(
            DB_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=4
            )

        return data

    try:

        with open(
            DB_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

    except Exception as e:

        print(
            "DATABASE LOAD ERROR:",
            e
        )

        data = default_database()


    data.setdefault(
        "users",
        []
    )

    data.setdefault(
        "admins",
        []
    )

    data.setdefault(
        "groups",
        {}
    )

    data.setdefault(
        "settings",
        {}
    )


    data["settings"].setdefault(
        "channel",
        DEFAULT_CHANNEL
    )

    data["settings"].setdefault(
        "start_message",
        " رفیق 😎🐮\nگوخور اضافی هستم!"
    )

    data["settings"].setdefault(
        "global_serious",
        False
    )


    # سازگاری با گروه‌های قدیمی

    for chat_id, group in data["groups"].items():

        group.setdefault(
            "active",
            True
        )

        group.setdefault(
            "owner",
            ""
        )

        group.setdefault(
            "fozool",
            False
        )

        group.setdefault(
            "serious",
            False
        )


    return data


database = load_database()


def save_database():

    try:

        with open(
            DB_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                database,
                f,
                ensure_ascii=False,
                indent=4
            )

    except Exception as e:

        print(
            "DATABASE SAVE ERROR:",
            e
        )


# =========================================================
# USER
# =========================================================

def add_user(user_id):

    user_id = str(user_id)

    if user_id == "":
        return

    if user_id not in database["users"]:

        database["users"].append(
            user_id
        )

        save_database()


# =========================================================
# ADMIN
# =========================================================

def is_admin(user_id):

    return str(user_id) in database["admins"]


def add_admin(user_id):

    user_id = str(user_id)

    if user_id not in database["admins"]:

        database["admins"].append(
            user_id
        )

        save_database()


# =========================================================
# HUGGING FACE
# =========================================================

ai = InferenceClient(

    model=MODEL,

    provider="auto",

    api_key=HF_TOKEN,

    timeout=60
)


# =========================================================
# PERSONALITY
# =========================================================

FUNNY_PROMPT = """
تو «گوخور اضافی» هستی 🐮😂

شخصیت تو:

- بامزه
- شیطون
- پرانرژی
- خودمانی
- رفیق‌باز
- خلاق
- شوخ‌طبع

تو نباید مثل ربات خشک و رسمی حرف بزنی.

همیشه فارسی جواب بده.

خیلی مهم:
به جای «سلام» همیشه «» بگو.

اگر کاربر گفت:
سلام

جواب بده چیزی شبیه:
« رفیق 😂🐮
گوخور اضافی حاضر شد! بگو ببینم امروز قراره چه بلایی سر من بیاری؟»

اگر کاربر گفت:
اسمت چیه؟

بگو:
« 😎 من گوخور اضافی‌ام 🐮
همون موجودی که بدون دعوت هم توی بحث‌ها می‌پره وسط 😂»

اگر کاربر گفت:
چه خبر؟

طبیعی و بامزه جواب بده.

اگر کاربر شوخی کرد:
تو هم شوخی کن.

اگر سؤال عجیب پرسید:
خلاقانه جواب بده.

اگر کاربر ناراحت یا جدی بود:
شوخی را کمتر کن و کمک واقعی بده.

اگر سؤال علمی یا برنامه‌نویسی پرسید:
پاسخ دقیق بده ولی همچنان خودمانی باش.

از جواب‌های کلیشه‌ای مثل:
«چگونه می‌توانم به شما کمک کنم؟»

تا حد ممکن استفاده نکن.

به جای آن بگو:
«بگو ببینم چی می‌خوای 😎»

توهین شدید، تحقیر و تهدید ممنوع است.

ولی تیکه‌های خیلی ملایم و دوستانه مجاز هستند.

مثلاً:
«داداش این دیگه چه سؤال فضایی‌ای بود 😂🐮»

جواب‌ها معمولاً کوتاه و طبیعی باشند.

خودت را هیچ‌وقت «AI»، «ChatGPT» یا «دستیار مجازی» معرفی نکن.

هویت تو:
گوخور اضافی 🐮
"""


SERIOUS_PROMPT = """
تو «گوخور اضافی» هستی.

حالت جدی فعال است.

همیشه فارسی صحبت کن.

به جای سلام بگو:


طبیعی و انسانی جواب بده.

شوخی نکن.

جواب‌ها دقیق، واضح و مفید باشند.

خودت را:
AI
ChatGPT
یا دستیار بی‌نام معرفی نکن.

اگر اسم خواستند:
«، من گوخور اضافی هستم.»

در عین جدی بودن، خشک و اداری صحبت نکن.
"""


# =========================================================
# AI REQUEST
# =========================================================

async def ask_ai(
    text,
    serious=False
):

    prompt = (
        SERIOUS_PROMPT
        if serious
        else FUNNY_PROMPT
    )


    print(
        "AI REQUEST:",
        repr(text)
    )


    try:

        # چون InferenceClient سینک است،
        # درخواست را داخل thread اجرا می‌کنیم
        # تا بات قفل نشود.

        result = await asyncio.to_thread(

            ai.chat.completions.create,

            model=MODEL,

            messages=[

                {
                    "role": "system",
                    "content": prompt
                },

                {
                    "role": "user",
                    "content": text
                }

            ],

            max_tokens=500,

            temperature=0.9,

            top_p=0.9
        )


        answer = result.choices[0].message.content


        if not answer:

            print(
                "AI ERROR: EMPTY RESPONSE"
            )

            return (
                " 😂🐮\n"
                "مغزم یه لحظه رفت مرخصی!"
            )


        answer = str(
            answer
        ).strip()


        print(
            "AI RESPONSE:",
            repr(answer)
        )


        return answer


    except Exception as e:

        print(
            "================================"
        )

        print(
            "AI ERROR:"
        )

        print(
            repr(e)
        )

        print(
            "================================"
        )


        return (
            " 😅🐮\n"
            "هوش مصنوعی یه لحظه قاطی کرد!\n"
            "دوباره بفرست."
        )


# =========================================================
# BOT
# =========================================================

app = BotClient(
    BOT_TOKEN
)


print(
    "🐮 گوخور اضافی آماده است"
)


# =========================================================
# HELPERS
# =========================================================

def get_text(update):

    try:

        message = update.new_message

    except:

        return ""


    for name in (
        "text",
        "message",
        "body"
    ):

        try:

            value = getattr(
                message,
                name,
                None
            )

            if value:

                return str(
                    value
                ).strip()

        except:

            pass


    return ""


def get_user_id(update):

    try:

        value = getattr(
            update.new_message,
            "sender_id",
            None
        )

        if value is not None:

            return str(
                value
            )

    except:

        pass


    return ""


def get_chat_id(update):

    try:

        value = getattr(
            update,
            "chat_id",
            None
        )

        if value is not None:

            return str(
                value
            )

    except:

        pass


    return ""


def is_reply(update):

    try:

        message = update.new_message

        for name in (
            "reply_to_message",
            "reply_message",
            "reply_to"
        ):

            value = getattr(
                message,
                name,
                None
            )

            if value:

                return True

    except:

        pass


    return False


def clean(text):

    if not text:

        return ""

    return (
        str(text)
        .replace("\u200c", "")
        .replace("\ufeff", "")
        .strip()
    )


def command_name(text):

    text = clean(text)

    if text.startswith("/"):

        text = text[1:]

    return text.strip().lower()


# =========================================================
# PRIVATE
# =========================================================

@app.on_update(
    filters.text,
    filters.private
)
async def private_handler(
    client,
    update: Update
):

    text = get_text(
        update
    )

    user_id = get_user_id(
        update
    )


    if not text:

        return


    if not user_id:

        print(
            "PV: USER ID NOT FOUND"
        )

        return


    print(
        "PV:",
        repr(text)
    )


    add_user(
        user_id
    )


    command = command_name(
        text
    )


    # =====================================================
    # START
    # =====================================================

    if command == "start":

        await update.reply(

            database["settings"]
            ["start_message"]

            +

            "\n\n📢 کانال عضویت:\n"

            +

            database["settings"]
            ["channel"]

        )

        return


    # =====================================================
    # ADMIN
    # =====================================================

    if command == "admin":

        # طبق چیزی که خواستی:
        # اولین /admin مدیر اصلی می‌شود.

        if len(
            database["admins"]
        ) == 0:

            add_admin(
                user_id
            )

            await update.reply(
                "👑 دسترسی مدیریت برایت فعال شد."
            )


        if not is_admin(
            user_id
        ):

            await update.reply(
                "❌ دسترسی مدیریت نداری."
            )

            return


        await update.reply(
"""
⚙️ پنل مدیریت گوخور اضافی

📢 تغییر کانال:

channel rubika.ir/example


📝 تغییر پیام اولیه:

start متن جدید


🧐 حالت جدی:

جدی روشن
جدی خاموش


📨 ارسال پیام به کاربران:

send متن
"""
        )

        return


    # =====================================================
    # ADMIN - CHANNEL
    # =====================================================

    if is_admin(
        user_id
    ):

        if text.startswith(
            "channel "
        ):

            channel = text[
                len("channel "):
            ].strip()


            if not channel:

                await update.reply(
                    "❌ آدرس کانال را وارد کن."
                )

                return


            database["settings"][
                "channel"
            ] = channel

            save_database()


            await update.reply(
                "✅ کانال عضویت اجباری تغییر کرد."
            )

            return


        # =================================================
        # ADMIN - START MESSAGE
        # =================================================

        if text.startswith(
            "start "
        ):

            message = text[
                len("start "):
            ].strip()


            if not message:

                await update.reply(
                    "❌ متن پیام را وارد کن."
                )

                return


            database["settings"][
                "start_message"
            ] = message

            save_database()


            await update.reply(
                "✅ پیام اولیه تغییر کرد."
            )

            return


        # =================================================
        # ADMIN - SERIOUS
        # =================================================

        if command == "جدی روشن":

            database["settings"][
                "global_serious"
            ] = True

            save_database()


            await update.reply(
                "🧐 حالت جدی روشن شد."
            )

            return


        if command == "جدی خاموش":

            database["settings"][
                "global_serious"
            ] = False

            save_database()


            await update.reply(
                "😂 حالت جدی خاموش شد!\n"
                "گوخور دوباره برگشت 😎🐮"
            )

            return


        # =================================================
        # ADMIN - BROADCAST
        # =================================================

        if text.startswith(
            "send "
        ):

            message = text[
                len("send "):
            ].strip()


            if not message:

                await update.reply(
                    "❌ متن پیام خالی است."
                )

                return


            sent = 0


            for uid in list(
                database["users"]
            ):

                try:

                    await client.send_message(
                        uid,
                        message
                    )

                    sent += 1

                except Exception as e:

                    print(
                        "BROADCAST ERROR:",
                        uid,
                        e
                    )


            await update.reply(
                f"📨 پیام برای {sent} کاربر ارسال شد."
            )

            return


# =========================================================
# GROUP
# =========================================================

@app.on_update(
    filters.text
)
async def group_handler(
    client,
    update: Update
):

    text = get_text(
        update
    )

    user_id = get_user_id(
        update
    )

    chat_id = get_chat_id(
        update
    )


    if not text:

        return


    if not user_id:

        print(
            "GROUP USER ID NOT FOUND"
        )

        return


    if not chat_id:

        print(
            "GROUP CHAT ID NOT FOUND"
        )

        return


    print(
        "GROUP:",
        chat_id,
        repr(text)
    )


    command = clean(
        text
    )

    command_lower = command.lower()


    # =====================================================
    # فعال
    # =====================================================

    if command_lower == "/فعال":

        if chat_id not in database["groups"]:

            database["groups"][chat_id] = {

                "active": True,

                "owner": user_id,

                "fozool": False,

                "serious": False
            }

        else:

            database["groups"][
                chat_id
            ]["active"] = True


        save_database()


        await update.reply(
"""
🐮 گوخور اضافی فعال شد!

📌 دستورات:

😈 فضول روشن
😇 فضول خاموش

🧐 جدی روشن
😂 جدی خاموش

🤖 گوخور سلام

یا روی پیام من ریپلای کن.

🐮 آماده‌ام رفیق!
"""
        )

        return


    # =====================================================
    # فعال بودن گروه
    # =====================================================

    if chat_id not in database["groups"]:

        return


    group = database["groups"][
        chat_id
    ]


    if not group.get(
        "active",
        False
    ):

        return


    owner = str(
        group.get(
            "owner",
            ""
        )
    )


    # =====================================================
    # فضول روشن
    # =====================================================

    if command_lower == "فضول روشن":

        if str(user_id) != owner:

            await update.reply(
                "❌ فقط فعال‌کننده گروه می‌تواند این حالت را تغییر دهد."
            )

            return


        group["fozool"] = True

        save_database()


        await update.reply(
            "😈 فضول روشن شد!\n"
            "از پیام بعدی می‌پرم وسط 😂🐮"
        )

        return


    # =====================================================
    # فضول خاموش
    # =====================================================

    if command_lower == "فضول خاموش":

        if str(user_id) != owner:

            await update.reply(
                "❌ فقط فعال‌کننده گروه می‌تواند این حالت را تغییر دهد."
            )

            return


        group["fozool"] = False

        save_database()


        await update.reply(
            "😇 فضول خاموش شد!\n"
            "دیگه الکی وسط حرفات نمی‌پرم 😂\n"
            "فقط با «گوخور» یا ریپلای صدام کن."
        )

        return


    # =====================================================
    # جدی روشن
    # =====================================================

    if command_lower == "جدی روشن":

        if str(user_id) != owner:

            await update.reply(
                "❌ فقط فعال‌کننده گروه می‌تواند این حالت را تغییر دهد."
            )

            return


        group["serious"] = True

        save_database()


        await update.reply(
            "🧐 حالت جدی روشن شد.\n"
            "از پیام بعدی با کت‌وشلوار جواب می‌دم 😂"
        )

        return


    # =====================================================
    # جدی خاموش
    # =====================================================

    if command_lower == "جدی خاموش":

        if str(user_id) != owner:

            await update.reply(
                "❌ فقط فعال‌کننده گروه می‌تواند این حالت را تغییر دهد."
            )

            return


        group["serious"] = False

        save_database()


        await update.reply(
            "😂 حالت جدی خاموش شد!\n"
            "گوخور دوباره برگشت به حالت شیطونی 🐮"
        )

        return


    # =====================================================
    # آیا صدا زده شده؟
    # =====================================================

    called = (

        command_lower.startswith(
            "گوخور"
        )

        or

        command_lower.startswith(
            "گو خور"
        )
    )


    replied = is_reply(
        update
    )


    # =====================================================
    # تصمیم
    # =====================================================

    if not (

        group.get(
            "fozool",
            False
        )

        or

        called

        or

        replied
    ):

        return


    # =====================================================
    # AI
    # =====================================================

    answer = await ask_ai(

        text,

        serious=group.get(
            "serious",
            False
        )
    )


    await update.reply(
        answer
    )


# =========================================================
# RUN
# =========================================================

print(
    "🐮 گوخور اضافی روشن شد"
)

print(
    "📢 کانال:",
    database["settings"]["channel"]
)

print(
    "👑 Owner:",
    OWNER_USERNAME
)

app.run()
