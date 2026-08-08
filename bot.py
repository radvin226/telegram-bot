# ============================================================
# 🐮 گوخور اضافی - FULL SINGLE FILE
# ============================================================

import os
import json
import asyncio

from rubpy.bot import BotClient, filters
from rubpy.bot.models import Update
from huggingface_hub import InferenceClient


# ============================================================
# CONFIG
# ============================================================

BOT_TOKEN = "توکن جدید روبیکا را اینجا بگذار"
HF_TOKEN = "توکن جدید HuggingFace را اینجا بگذار"

CHANNEL_ID = "c=c0DySFl0a7501a52aaea7d7381111798"
CHANNEL_LINK = "rubika.ir/linkgokh"

DB_FILE = "database.json"

MODEL = "meta-llama/Llama-3.3-70B-Instruct"


# ============================================================
# DATABASE
# ============================================================

def create_db():

    return {
        "admins": [],
        "users": [],

        "settings": {
            "channel_id": CHANNEL_ID,
            "channel_link": CHANNEL_LINK,

            "start_message":
                "درود رفیق 😎🐮\n\n"
                "گوخور اضافی آماده‌ست!"
        },

        "groups": {}
    }


def save_db(data):

    try:

        with open(
            DB_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4
            )

    except Exception as e:

        print(
            "DATABASE SAVE ERROR:",
            repr(e)
        )


def load_db():

    if not os.path.exists(DB_FILE):

        data = create_db()

        save_db(data)

        return data


    try:

        with open(
            DB_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

    except Exception as e:

        print(
            "DATABASE ERROR:",
            repr(e)
        )

        data = create_db()


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


    return data


db = load_db()


def save():

    save_db(
        db
    )


# ============================================================
# ADMIN
# ============================================================

def add_admin(user_id):

    user_id = str(
        user_id
    )

    if user_id not in db["admins"]:

        db["admins"].append(
            user_id
        )

        save()


    return True


def is_admin(user_id):

    user_id = str(
        user_id
    )

    return user_id in [
        str(x)
        for x in db["admins"]
    ]


# ============================================================
# USER
# ============================================================

def add_user(user_id):

    user_id = str(
        user_id
    )

    if not user_id:
        return


    if user_id not in db["users"]:

        db["users"].append(
            user_id
        )

        save()


# ============================================================
# AI
# ============================================================

FUNNY_PROMPT = """
تو «گوخور اضافی» هستی 🐮😂

همیشه فارسی جواب بده.

هیچ‌وقت به جای درود از سلام استفاده نکن.

شخصیت:
بامزه، شیطون، دوستانه، پرانرژی و خودمانی.

اگر کاربر شوخی کرد، شوخی کن.

اگر سؤال جدی بود، جواب درست و مفید بده.

توهین سنگین نکن.

خودت را ChatGPT معرفی نکن.

اگر پرسید اسمت چیست:
«درود 😎 من گوخور اضافی‌ام 🐮»

جواب‌ها طبیعی و کوتاه باشند.
"""


SERIOUS_PROMPT = """
تو «گوخور اضافی» هستی.

همیشه فارسی جواب بده.

به جای سلام بگو درود.

حالت جدی فعال است.

شوخی نکن.

دقیق، واضح و مفید جواب بده.

خودت را ChatGPT معرفی نکن.

اگر اسم پرسیدند:
«درود، من گوخور اضافی هستم.»
"""


ai = InferenceClient(
    model=MODEL,
    provider="auto",
    api_key=HF_TOKEN,
    timeout=90
)


async def ask_ai(
    text,
    serious=False
):

    prompt = (
        SERIOUS_PROMPT
        if serious
        else FUNNY_PROMPT
    )

    try:

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

            temperature=0.9
        )


        answer = (
            result
            .choices[0]
            .message
            .content
        )


        if not answer:

            return "درود 😂🐮"


        return str(
            answer
        ).strip()


    except Exception as e:

        print(
            "AI ERROR:",
            repr(e)
        )

        return (
            "درود 😅🐮\n"
            "هوش مصنوعیم یه لحظه هنگ کرد!"
        )


# ============================================================
# BOT
# ============================================================

bot = BotClient(
    BOT_TOKEN
)


# ============================================================
# HELPERS
# ============================================================

def text_of(update):

    try:

        message = update.new_message

        value = getattr(
            message,
            "text",
            None
        )

        if value:

            return str(
                value
            ).strip()

    except Exception:
        pass

    return ""


def user_of(update):

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


def chat_of(update):

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


def replied(update):

    try:

        message = update.new_message

        for name in (
            "reply_to_message",
            "reply_message",
            "reply_to"
        ):

            if getattr(
                message,
                name,
                None
            ):

                return True

    except Exception:
        pass

    return False


# ============================================================
# FORCE JOIN
# ============================================================

async def check_member(
    client,
    user_id
):

    try:

        channel = db[
            "settings"
        ].get(
            "channel_id",
            CHANNEL_ID
        )


        result = await client.get_chat_member(

            str(channel),

            str(user_id)
        )


        print(
            "MEMBERSHIP:",
            repr(result)
        )


        status = str(
            getattr(
                result,
                "status",
                ""
            )
        ).lower()


        if status in (
            "member",
            "administrator",
            "admin",
            "creator",
            "owner"
        ):

            return True


        raw = str(
            result
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
            "left" not in raw
            and
            "kicked" not in raw
            and
            "not_member" not in raw
        ):

            return True


        return False


    except Exception as e:

        print(
            "MEMBERSHIP ERROR:",
            repr(e)
        )

        return False


async def force_join_message(
    update
):

    link = db[
        "settings"
    ].get(
        "channel_link",
        CHANNEL_LINK
    )


    await update.reply(

        "درود رفیق 🐮❤️\n\n"

        "برای استفاده از گوخور اضافی "
        "اول داخل کانال زیر عضو شو:\n\n"

        f"📢 {link}\n\n"

        "بعد دوباره /start بزن."
    )


# ============================================================
# PRIVATE
# ============================================================

@bot.on_update(
    filters.text,
    filters.private
)
async def private(
    client,
    update: Update
):

    try:

        text = text_of(
            update
        )

        user_id = user_of(
            update
        )


        print(
            "PV:",
            repr(text)
        )


        print(
            "USER:",
            repr(user_id)
        )


        if not text:
            return

        if not user_id:
            return


        add_user(
            user_id
        )


        command = text.lower().strip()


        # ====================================================
        # /admin
        #
        # بسیار مهم:
        # این شرط قبل از is_admin قرار دارد.
        # ====================================================

        if command == "/admin":

            add_admin(
                user_id
            )


            print(
                "ADMIN ADDED:",
                user_id
            )


            print(
                "ADMIN LIST:",
                db["admins"]
            )


            await update.reply(

                "👑 دسترسی مدیریت فعال شد!\n\n"

                "این حساب الان ادمین بات است 🐮😎\n\n"

                "دستورات مدیریت:\n\n"

                "/admin\n"
                "/startmsg متن جدید\n"
                "/channel لینک کانال\n"
                "/setchannel شناسه کانال\n"
                "/send متن\n"
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

            ok = await check_member(

                client,

                user_id
            )


            if not ok:

                await force_join_message(
                    update
                )

                return


            await update.reply(

                db[
                    "settings"
                ].get(
                    "start_message",
                    "درود رفیق 😎🐮"
                )
            )

            return


        # ====================================================
        # ADMIN CHECK
        # ====================================================

        if not is_admin(
            user_id
        ):

            return


        # ====================================================
        # CHANGE START MESSAGE
        # ====================================================

        if command.startswith(
            "/startmsg "
        ):

            value = text[
                len("/startmsg "):
            ].strip()


            if value:

                db[
                    "settings"
                ][
                    "start_message"
                ] = value

                save()


                await update.reply(
                    "✅ پیام اولیه تغییر کرد."
                )

            return


        # ====================================================
        # CHANGE CHANNEL LINK
        # ====================================================

        if command.startswith(
            "/channel "
        ):

            value = text[
                len("/channel "):
            ].strip()


            if value:

                db[
                    "settings"
                ][
                    "channel_link"
                ] = value

                save()


                await update.reply(
                    "✅ لینک کانال تغییر کرد."
                )

            return


        # ====================================================
        # CHANGE CHANNEL ID
        # ====================================================

        if command.startswith(
            "/setchannel "
        ):

            value = text[
                len("/setchannel "):
            ].strip()


            if value:

                db[
                    "settings"
                ][
                    "channel_id"
                ] = value

                save()


                await update.reply(
                    "✅ شناسه کانال تغییر کرد."
                )

            return


        # ====================================================
        # CHECK
        # ====================================================

        if command == "/check":

            result = await check_member(

                client,

                user_id
            )


            await update.reply(

                "✅ عضویت تأیید شد."
                if result
                else
                "❌ عضویت تأیید نشد."
            )

            return


        # ====================================================
        # BROADCAST
        # ====================================================

        if command.startswith(
            "/send "
        ):

            message = text[
                len("/send "):
            ].strip()


            if not message:

                await update.reply(
                    "❌ متن خالی است."
                )

                return


            count = 0


            for uid in list(
                db["users"]
            ):

                try:

                    await client.send_message(
                        uid,
                        message
                    )

                    count += 1

                except Exception as e:

                    print(
                        "SEND ERROR:",
                        repr(e)
                    )


            await update.reply(
                f"📨 برای {count} نفر ارسال شد."
            )

            return


    except Exception as e:

        print(
            "PRIVATE ERROR:",
            repr(e)
        )


# ============================================================
# GROUP
# ============================================================

@bot.on_update(
    filters.text
)
async def group(
    client,
    update: Update
):

    try:

        text = text_of(
            update
        )

        user_id = user_of(
            update
        )

        chat_id = chat_of(
            update
        )


        if not text:
            return

        if not user_id:
            return

        if not chat_id:
            return


        print(
            "GROUP:",
            chat_id,
            repr(text)
        )


        command = text.lower().strip()


        # ====================================================
        # ACTIVATE
        # ====================================================

        if command in (
            "/فعال",
            "فعال"
        ):

            db[
                "groups"
            ][
                chat_id
            ] = {

                "active": True,

                "owner": str(
                    user_id
                ),

                "fozool": False,

                "serious": False
            }


            save()


            await update.reply(

                "🐮 گوخور اضافی فعال شد!\n\n"

                "📌 دستورات:\n\n"

                "😈 فضول روشن\n"
                "😇 فضول خاموش\n\n"

                "🧐 جدی روشن\n"
                "😂 جدی خاموش\n\n"

                "🤖 گوخور سلام\n\n"

                "یا روی پیام ریپلای کن."
            )

            return


        # ====================================================
        # GROUP STATUS
        # ====================================================

        if chat_id not in db[
            "groups"
        ]:

            return


        settings = db[
            "groups"
        ][
            chat_id
        ]


        if not settings.get(
            "active",
            False
        ):

            return


        owner = str(
            settings.get(
                "owner",
                ""
            )
        )


        # ====================================================
        # FOZOOL ON
        # ====================================================

        if command == "فضول روشن":

            if str(user_id) != owner:

                await update.reply(
                    "❌ فقط فعال‌کننده گروه می‌تواند این حالت را تغییر دهد."
                )

                return


            settings[
                "fozool"
            ] = True

            save()


            await update.reply(
                "😈 فضول روشن شد!\n"
                "از پیام بعدی جواب می‌دم 😂🐮"
            )

            return


        # ====================================================
        # FOZOOL OFF
        # ====================================================

        if command == "فضول خاموش":

            if str(user_id) != owner:

                await update.reply(
                    "❌ فقط فعال‌کننده گروه می‌تواند این حالت را تغییر دهد."
                )

                return


            settings[
                "fozool"
            ] = False

            save()


            await update.reply(
                "😇 فضول خاموش شد!\n"
                "فقط با «گوخور» یا ریپلای جواب می‌دم."
            )

            return


        # ====================================================
        # SERIOUS ON
        # ====================================================

        if command == "جدی روشن":

            if str(user_id) != owner:

                await update.reply(
                    "❌ فقط فعال‌کننده گروه می‌تواند این حالت را تغییر دهد."
                )

                return


            settings[
                "serious"
            ] = True

            save()


            await update.reply(
                "🧐 حالت جدی روشن شد.\n"
                "از پیام بعدی جدی جواب می‌دم."
            )

            return


        # ====================================================
        # SERIOUS OFF
        # ====================================================

        if command == "جدی خاموش":

            if str(user_id) != owner:

                await update.reply(
                    "❌ فقط فعال‌کننده گروه می‌تواند این حالت را تغییر دهد."
                )

                return


            settings[
                "serious"
            ] = False

            save()


            await update.reply(
                "😂 حالت جدی خاموش شد!\n"
                "گوخور برگشت به حالت شیطونی 🐮"
            )

            return


        # ====================================================
        # AI TRIGGER
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


        reply = replied(
            update
        )


        if not settings.get(
            "fozool",
            False
        ):

            if not called and not reply:

                return


        answer = await ask_ai(

            text,

            serious=settings.get(
                "serious",
                False
            )
        )


        await update.reply(
            answer
        )


    except Exception as e:

        print(
            "GROUP ERROR:",
            repr(e)
        )


# ============================================================
# RUN
# ============================================================

print()
print("🐮 گوخور اضافی آماده است")
print("📢 کانال:", CHANNEL_ID)
print("💾 دیتابیس:", DB_FILE)
print("🤖 AI:", MODEL)
print()

bot.run()
