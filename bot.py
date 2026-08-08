# ============================================================
# 🐮 گوخور اضافی
# Rubika + HuggingFace AI
# نسخه تک فایل
# ============================================================

import os
import json
import asyncio

from rubpy.bot import BotClient, filters
from rubpy.bot.models import Update

from huggingface_hub import InferenceClient


# ============================================================
# تنظیمات
# ============================================================
BOT_TOKEN = "CBDJAI0PCBTZSKKHMJTTVUPFUDZQVZXFLQGRVMQCKNXCQRSFRQMTJFEPPZDAJQFF"

HF_TOKEN = "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"

# کانال اجباری
CHANNEL_ID = "c=c0DySFl0a7501a52aaea7d7381111798"

CHANNEL_LINK = "rubika.ir/linkgokh"

# مدل هوش مصنوعی
MODEL = "meta-llama/Llama-3.3-70B-Instruct"

# دیتابیس
DATABASE_FILE = "database.json"


# ============================================================
# بررسی تنظیمات
# ============================================================

if BOT_TOKEN == "YOUR_NEW_RUBIKA_BOT_TOKEN":
    print("⚠️ BOT_TOKEN را تنظیم کن.")

if HF_TOKEN == "YOUR_NEW_HUGGINGFACE_TOKEN":
    print("⚠️ HF_TOKEN را تنظیم کن.")


# ============================================================
# DATABASE
# ============================================================

def default_database():

    return {
        "admins": [],
        "users": [],

        "groups": {},

        "settings": {
            "channel_id": CHANNEL_ID,
            "channel_link": CHANNEL_LINK,

            "start_message":
                "درود رفیق 😎🐮\n\n"
                "گوخور اضافی آماده‌ست 😂"
        }
    }


def load_database():

    if not os.path.exists(DATABASE_FILE):

        data = default_database()

        save_database_data(data)

        return data


    try:

        with open(
            DATABASE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

    except Exception as error:

        print(
            "❌ DATABASE LOAD ERROR:",
            repr(error)
        )

        data = default_database()


    data.setdefault(
        "admins",
        []
    )

    data.setdefault(
        "users",
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
        "channel_id",
        CHANNEL_ID
    )

    data["settings"].setdefault(
        "channel_link",
        CHANNEL_LINK
    )

    data["settings"].setdefault(
        "start_message",
        "درود رفیق 😎🐮"
    )


    for group_id, group in data["groups"].items():

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


def save_database_data(data):

    try:

        with open(
            DATABASE_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4
            )

    except Exception as error:

        print(
            "❌ DATABASE SAVE ERROR:",
            repr(error)
        )


database = load_database()


def save_database():

    save_database_data(
        database
    )


# ============================================================
# USER
# ============================================================

def add_user(user_id):

    user_id = str(
        user_id
    )

    if not user_id:

        return


    if user_id not in database["users"]:

        database["users"].append(
            user_id
        )

        save_database()


# ============================================================
# ADMIN
# ============================================================

def is_admin(user_id):

    return str(
        user_id
    ) in database["admins"]


def make_admin(user_id):

    user_id = str(
        user_id
    )

    if user_id not in database["admins"]:

        database["admins"].append(
            user_id
        )

        save_database()


# ============================================================
# AI
# ============================================================

ai = InferenceClient(

    model=MODEL,

    provider="auto",

    api_key=HF_TOKEN,

    timeout=90
)


FUNNY_SYSTEM = r"""
تو «گوخور اضافی» هستی 🐮😂

شخصیت تو:

- بامزه
- شیطون
- پرانرژی
- دوستانه
- خلاق
- رفیق‌باز

قوانین:

1. همیشه فارسی جواب بده.

2. هیچ‌وقت از «سلام» استفاده نکن.
به‌جایش همیشه «درود» بگو.

3. خودت را ChatGPT معرفی نکن.

4. اگر اسم خودت را پرسیدند:
«درود 😎 من گوخور اضافی‌ام 🐮»

5. اگر کاربر شوخی کرد، شوخی کن.

6. اگر سؤال عجیب پرسید، جواب خلاقانه بده.

7. گاهی تیکه‌های خیلی ملایم و دوستانه بینداز.

8. توهین سنگین نکن.

9. اگر سؤال علمی یا جدی بود، درست و مفید جواب بده.

10. جواب‌ها طبیعی باشند، نه خشک و رباتی.

11. از ایموجی‌ها گاهی استفاده کن.

12. زیادی توضیح اضافه نده مگر اینکه کاربر درخواست کند.

نمونه:

کاربر:
سلام

تو:
درود رفیق 😂🐮
گوخور اضافی حاضر شد!
بگو ببینم چه نقشه‌ای داری؟

کاربر:
اسمت چیه؟

تو:
درود 😎
گوخور اضافی‌ام 🐮
همونی که بی‌دعوت وسط بحث پیداش میشه 😂

کاربر:
چه خبر؟

تو:
درود 😂
خبر خاصی نیست، دارم با چندتا بیت و بایت زندگی می‌کنم 🐮
"""


SERIOUS_SYSTEM = r"""
تو «گوخور اضافی» هستی.

حالت جدی فعال است.

همیشه فارسی صحبت کن.

به جای «سلام» بگو «درود».

شوخی نکن.

جواب دقیق، واضح و مفید بده.

خشک و اداری نباش.

خودت را ChatGPT معرفی نکن.

اگر اسم پرسیده شد بگو:
«درود، من گوخور اضافی هستم.»
"""


async def ask_ai(
    text,
    serious=False
):

    system_prompt = (
        SERIOUS_SYSTEM
        if serious
        else FUNNY_SYSTEM
    )


    print(
        "🤖 AI REQUEST:",
        repr(text)
    )


    try:

        result = await asyncio.to_thread(

            ai.chat.completions.create,

            model=MODEL,

            messages=[
                {
                    "role": "system",
                    "content": system_prompt
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


        answer = (
            result
            .choices[0]
            .message
            .content
        )


        if not answer:

            return (
                "درود 😂🐮\n"
                "مغزم یه لحظه هنگ کرد!"
            )


        return str(
            answer
        ).strip()


    except Exception as error:

        print(
            "================================"
        )

        print(
            "❌ AI ERROR:",
            repr(error)
        )

        print(
            "================================"
        )


        return (
            "درود 😅🐮\n"
            "هوش مصنوعیم یه لحظه قاطی کرد!\n"
            "دوباره بفرست."
        )


# ============================================================
# BOT
# ============================================================

app = BotClient(
    BOT_TOKEN
)


print(
    "======================================"
)

print(
    "🐮 گوخور اضافی آماده است"
)

print(
    "📢 Channel:",
    CHANNEL_ID
)

print(
    "🤖 Model:",
    MODEL
)

print(
    "======================================"
)


# ============================================================
# HELPERS
# ============================================================

def get_text(update):

    try:

        message = update.new_message

        text = getattr(
            message,
            "text",
            None
        )

        if text:

            return str(
                text
            ).strip()

    except Exception:

        pass


    return ""


def get_user_id(update):

    try:

        message = update.new_message

        value = getattr(
            message,
            "sender_id",
            None
        )

        if value:

            return str(
                value
            )

    except Exception:

        pass


    return ""


def get_chat_id(update):

    try:

        value = getattr(
            update,
            "chat_id",
            None
        )

        if value:

            return str(
                value
            )

    except Exception:

        pass


    try:

        message = update.new_message

        value = getattr(
            message,
            "chat_id",
            None
        )

        if value:

            return str(
                value
            )

    except Exception:

        pass


    return ""


def is_reply(update):

    try:

        message = update.new_message

        for field in (
            "reply_to_message",
            "reply_message",
            "reply_to"
        ):

            value = getattr(
                message,
                field,
                None
            )

            if value:

                return True

    except Exception:

        pass


    return False


# ============================================================
# CHANNEL MEMBERSHIP
# ============================================================

async def check_membership(
    client,
    user_id
):

    try:

        print(
            "🔎 CHECK:",
            CHANNEL_ID,
            "USER:",
            user_id
        )


        member = await client.get_chat_member(

            CHANNEL_ID,

            str(
                user_id
            )
        )


        print(
            "📢 MEMBER:",
            repr(member)
        )


        status = str(
            getattr(
                member,
                "status",
                ""
            )
        ).lower()


        print(
            "📢 STATUS:",
            status
        )


        if status in (
            "member",
            "administrator",
            "admin",
            "owner",
            "creator"
        ):

            return True


        raw = str(
            member
        ).lower()


        if (
            "administrator" in raw
            or
            "creator" in raw
            or
            "owner" in raw
        ):

            return True


        if (
            "member" in raw
            and
            "not_member" not in raw
            and
            "left" not in raw
            and
            "kicked" not in raw
        ):

            return True


        return False


    except Exception as error:

        print(
            "================================"
        )

        print(
            "❌ MEMBERSHIP ERROR:"
        )

        print(
            repr(error)
        )

        print(
            "================================"
        )

        return False


# ============================================================
# FORCE JOIN
# ============================================================

async def send_force_join(
    update
):

    await update.reply(

        "درود رفیق 🐮❤️\n\n"

        "برای استفاده از گوخور اضافی "
        "اول باید عضو کانال زیر بشی 👇\n\n"

        f"📢 {CHANNEL_LINK}\n\n"

        "بعد از عضویت دوباره /start رو بزن "
        "تا عضویتت رو بررسی کنم 😎🐮"
    )


# ============================================================
# PRIVATE HANDLER
# ============================================================

@app.on_update(
    filters.text,
    filters.private
)
async def private_handler(
    client,
    update: Update
):

    try:

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
                "❌ USER ID NOT FOUND"
            )

            return


        print(
            "PV:",
            repr(text)
        )


        add_user(
            user_id
        )


        command = text.lower().strip()


        # ====================================================
        # /admin
        # ====================================================

        if command == "/admin":

            # هرکس /admin بزند
            # ادمین می‌شود

            make_admin(
                user_id
            )


            await update.reply(

                "👑 ادمین بات شناخته شد.\n\n"

                "دسترسی مدیریت برای این حساب فعال شد.\n\n"

                "دستورات مدیریت:\n\n"

                "/admin\n"
                "/setchannel\n"
                "/channel\n"
                "/startmsg\n"
                "/send\n"
                "/check"
            )

            return


        # ====================================================
        # START
        # ====================================================

        if command in (
            "/start",
            "start"
        ):

            member = await check_membership(

                client,

                user_id
            )


            if not member:

                await send_force_join(
                    update
                )

                return


            await update.reply(

                database[
                    "settings"
                ].get(
                    "start_message",
                    "درود رفیق 😎🐮"
                )
            )

            return


        # ====================================================
        # ADMIN COMMANDS
        # ====================================================

        if is_admin(
            user_id
        ):

            # ------------------------------------------------
            # /setchannel
            # ------------------------------------------------

            if command.startswith(
                "/setchannel "
            ):

                value = text[
                    len("/setchannel "):
                ].strip()


                if value:

                    database[
                        "settings"
                    ][
                        "channel_id"
                    ] = value

                    save_database()


                    await update.reply(
                        "✅ شناسه کانال ذخیره شد."
                    )

                return


            # ------------------------------------------------
            # /channel
            # ------------------------------------------------

            if command.startswith(
                "/channel "
            ):

                value = text[
                    len("/channel "):
                ].strip()


                if value:

                    database[
                        "settings"
                    ][
                        "channel_link"
                    ] = value

                    save_database()


                    await update.reply(
                        "✅ لینک کانال تغییر کرد."
                    )

                return


            # ------------------------------------------------
            # /startmsg
            # ------------------------------------------------

            if command.startswith(
                "/startmsg "
            ):

                value = text[
                    len("/startmsg "):
                ].strip()


                if value:

                    database[
                        "settings"
                    ][
                        "start_message"
                    ] = value

                    save_database()


                    await update.reply(
                        "✅ پیام اولیه تغییر کرد."
                    )

                return


            # ------------------------------------------------
            # /check
            # ------------------------------------------------

            if command == "/check":

                result = await check_membership(

                    client,

                    user_id
                )


                if result:

                    await update.reply(
                        "✅ عضویت تأیید شد."
                    )

                else:

                    await update.reply(
                        "❌ عضویت تأیید نشد."
                    )

                return


            # ------------------------------------------------
            # /send
            # ------------------------------------------------

            if command.startswith(
                "/send "
            ):

                message = text[
                    len("/send "):
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

                    except Exception as error:

                        print(
                            "SEND ERROR:",
                            repr(error)
                        )


                await update.reply(
                    f"📨 پیام برای {sent} نفر ارسال شد."
                )

                return


    except Exception as error:

        print(
            "PRIVATE HANDLER ERROR:",
            repr(error)
        )


# ============================================================
# GROUP HANDLER
# ============================================================

@app.on_update(
    filters.text
)
async def group_handler(
    client,
    update: Update
):

    try:

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


        if not chat_id:

            return


        if not user_id:

            return


        print(
            "GROUP:",
            chat_id,
            repr(text)
        )


        command = text.strip().lower()


        # ====================================================
        # فعال سازی
        # ====================================================

        if command in (
            "/فعال",
            "فعال"
        ):

            database[
                "groups"
            ][
                str(chat_id)
            ] = {

                "active": True,

                "owner": str(
                    user_id
                ),

                "fozool": False,

                "serious": False
            }


            save_database()


            await update.reply(

                "🐮 گوخور اضافی فعال شد!\n\n"

                "📌 لیست دستورات:\n\n"

                "😈 فضول روشن\n"
                "😇 فضول خاموش\n\n"

                "🧐 جدی روشن\n"
                "😂 جدی خاموش\n\n"

                "🤖 گوخور سلام\n\n"

                "یا روی پیام ریپلای کن.\n\n"

                "آماده‌ام 😎🐮"
            )

            return


        # ====================================================
        # اگر فعال نشده
        # ====================================================

        if str(chat_id) not in database[
            "groups"
        ]:

            return


        group = database[
            "groups"
        ][
            str(chat_id)
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


        # ====================================================
        # فضول روشن
        # ====================================================

        if command == "فضول روشن":

            if str(user_id) != owner:

                await update.reply(
                    "❌ فقط کسی که بات را فعال کرده می‌تواند این تنظیم را تغییر دهد."
                )

                return


            group[
                "fozool"
            ] = True


            save_database()


            await update.reply(
                "😈 حالت فضول روشن شد!\n"
                "از پیام بعدی جواب می‌دم 😂🐮"
            )

            return


        # ====================================================
        # فضول خاموش
        # ====================================================

        if command == "فضول خاموش":

            if str(user_id) != owner:

                await update.reply(
                    "❌ فقط فعال‌کننده گروه می‌تواند این تنظیم را تغییر دهد."
                )

                return


            group[
                "fozool"
            ] = False


            save_database()


            await update.reply(
                "😇 حالت فضول خاموش شد!\n"
                "فقط وقتی «گوخور» بگی یا روی پیامم ریپلای کنی جواب می‌دم."
            )

            return


        # ====================================================
        # جدی روشن
        # ====================================================

        if command == "جدی روشن":

            if str(user_id) != owner:

                await update.reply(
                    "❌ فقط فعال‌کننده گروه می‌تواند این تنظیم را تغییر دهد."
                )

                return


            group[
                "serious"
            ] = True


            save_database()


            await update.reply(
                "🧐 حالت جدی روشن شد.\n"
                "از پیام بعدی جدی جواب می‌دم."
            )

            return


        # ====================================================
        # جدی خاموش
        # ====================================================

        if command == "جدی خاموش":

            if str(user_id) != owner:

                await update.reply(
                    "❌ فقط فعال‌کننده گروه می‌تواند این تنظیم را تغییر دهد."
                )

                return


            group[
                "serious"
            ] = False


            save_database()


            await update.reply(
                "😂 حالت جدی خاموش شد!\n"
                "گوخور برگشت به حالت شیطونی 🐮"
            )

            return


        # ====================================================
        # TRIGGER
        # ====================================================

        called = (

            command.startswith(
                "گوخور"
            )

            or

            command.startswith(
                "گو خور"
            )
        )


        replied = is_reply(
            update
        )


        # فضول خاموش
        if not group.get(
            "fozool",
            False
        ):

            if not called and not replied:

                return


        # ====================================================
        # AI
        # ====================================================

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


    except Exception as error:

        print(
            "GROUP HANDLER ERROR:",
            repr(error)
        )


# ============================================================
# RUN
# ============================================================

print(
    "======================================"
)

print(
    "🐮 گوخور اضافی روشن شد"
)

print(
    "📢 کانال:",
    CHANNEL_LINK
)

print(
    "🤖 مدل:",
    MODEL
)

print(
    "💾 Database:",
    DATABASE_FILE
)

print(
    "======================================"
)


app.run()
