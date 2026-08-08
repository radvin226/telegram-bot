# ============================================================
# 🐮 گوخور اضافی
# Rubika + HuggingFace
# نسخه کامل تک فایل
# ============================================================

import os
import json
import asyncio

from rubpy.bot import BotClient, filters
from rubpy.bot.models import Update
from huggingface_hub import InferenceClient


# ============================================================
# 🔧 CONFIG
# ============================================================

BOT_TOKEN = "توکن جدید ربات روبیکا"
HF_TOKEN = "توکن جدید HuggingFace"

# کانال عضویت اجباری
CHANNEL_ID = "c=c0DySFl0a7501a52aaea7d7381111798"
CHANNEL_LINK = "rubika.ir/linkgokh"

# مدل هوش مصنوعی
MODEL = "meta-llama/Llama-3.3-70B-Instruct"

# دیتابیس
DB_FILE = "database.json"


# ============================================================
# 💾 DATABASE
# ============================================================

def new_database():
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


def save_db_data(data):
    try:
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

    except Exception as e:
        print("❌ DATABASE SAVE ERROR:", repr(e))


def load_db():

    if not os.path.exists(DB_FILE):

        data = new_database()

        save_db_data(data)

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
            "❌ DATABASE LOAD ERROR:",
            repr(e)
        )

        data = new_database()


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


    for gid, group in data["groups"].items():

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


db = load_db()


def save_db():
    save_db_data(db)


# ============================================================
# 👤 USERS
# ============================================================

def add_user(user_id):

    user_id = str(user_id)

    if not user_id:
        return

    if user_id not in db["users"]:

        db["users"].append(
            user_id
        )

        save_db()


# ============================================================
# 👑 ADMIN
# ============================================================

def make_admin(user_id):

    user_id = str(user_id)

    if not user_id:
        return False

    if user_id not in db["admins"]:

        db["admins"].append(
            user_id
        )

        save_db()

        print(
            "👑 NEW ADMIN:",
            user_id
        )

    return True


def is_admin(user_id):

    return str(
        user_id
    ) in [
        str(x)
        for x in db["admins"]
    ]


# ============================================================
# 🤖 AI
# ============================================================

ai = InferenceClient(
    model=MODEL,
    provider="auto",
    api_key=HF_TOKEN,
    timeout=90
)


FUNNY_PROMPT = """
تو «گوخور اضافی» هستی 🐮😂

همیشه فارسی صحبت کن.

به جای «سلام» همیشه «درود» بگو.

شخصیت تو:
- بامزه
- شیطون
- پرانرژی
- دوستانه
- خلاق
- خودمانی

اگر کاربر شوخی کرد، شوخی کن.

اگر سؤال عجیب پرسید، خلاقانه جواب بده.

اگر سؤال جدی بود، دقیق جواب بده ولی خشک نباش.

گاهی تیکه‌های خیلی ملایم و دوستانه بنداز.

توهین سنگین نکن.

خودت را ChatGPT یا دستیار هوش مصنوعی معرفی نکن.

اگر پرسید اسمت چیست:
«درود 😎 من گوخور اضافی‌ام 🐮»

اگر کاربر گفت سلام:
«درود رفیق 😂🐮»

جواب‌ها طبیعی و کوتاه باشند مگر اینکه کاربر توضیح کامل بخواهد.
"""


SERIOUS_PROMPT = """
تو «گوخور اضافی» هستی.

همیشه فارسی صحبت کن.

به جای سلام بگو درود.

حالت جدی فعال است.

شوخی نکن.

دقیق و واضح جواب بده.

خشک و رباتی نباش.

خودت را ChatGPT معرفی نکن.

اگر اسم پرسیدند:
«درود، من گوخور اضافی هستم.»
"""


async def ask_ai(
    text,
    serious=False
):

    system_prompt = (
        SERIOUS_PROMPT
        if serious
        else FUNNY_PROMPT
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


        answer = str(
            answer
        ).strip()


        print(
            "🤖 AI RESPONSE:",
            repr(answer)
        )


        return answer


    except Exception as e:

        print(
            "❌ AI ERROR:",
            repr(e)
        )

        return (
            "درود 😅🐮\n"
            "هوش مصنوعیم یه لحظه قاطی کرد!"
        )


# ============================================================
# 🐮 BOT
# ============================================================

app = BotClient(
    BOT_TOKEN
)


print("====================================")
print("🐮 گوخور اضافی آماده است")
print("📢 CHANNEL:", CHANNEL_ID)
print("🤖 MODEL:", MODEL)
print("💾 DATABASE:", DB_FILE)
print("====================================")


# ============================================================
# 🔍 HELPERS
# ============================================================

def get_text(update):

    try:

        message = update.new_message

        value = getattr(
            message,
            "text",
            None
        )

        if value:
            return str(value).strip()

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
            return str(value)

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
            return str(value)

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
            return str(value)

    except Exception:
        pass

    return ""


def is_reply(update):

    try:

        message = update.new_message

        possible_fields = [
            "reply_to_message",
            "reply_message",
            "reply_to"
        ]

        for field in possible_fields:

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
# 📢 FORCE JOIN
# ============================================================

async def check_membership(
    client,
    user_id
):

    try:

        channel_id = db[
            "settings"
        ].get(
            "channel_id",
            CHANNEL_ID
        )


        print(
            "🔎 MEMBERSHIP CHECK"
        )

        print(
            "CHANNEL:",
            channel_id
        )

        print(
            "USER:",
            user_id
        )


        member = await client.get_chat_member(

            str(channel_id),

            str(user_id)
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


    except Exception as e:

        print(
            "===================================="
        )

        print(
            "❌ MEMBERSHIP ERROR"
        )

        print(
            repr(e)
        )

        print(
            "===================================="
        )

        return False


async def force_join(
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
        "اول باید عضو کانال زیر بشی 👇\n\n"

        f"📢 {link}\n\n"

        "بعد از عضویت دوباره /start رو بزن 😎🐮"
    )


# ============================================================
# 👤 PRIVATE HANDLER
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
            return


        print(
            "PV:",
            repr(text)
        )


        add_user(
            user_id
        )


        command = text.strip().lower()


        # ====================================================
        # 👑 ADMIN
        # ====================================================

        if command == "/admin":

            # بدون هیچ شرط قبلی
            # همین الان ادمینش کن

            make_admin(
                user_id
            )


            print(
                "👑 ADMIN ACCESS:",
                user_id
            )


            await update.reply(

                "👑 دسترسی مدیریت فعال شد!\n\n"

                "این حساب الان ادمین بات است 😎🐮\n\n"

                "دستورات مدیریت:\n"
                "/admin\n"
                "/startmsg متن\n"
                "/channel لینک\n"
                "/setchannel شناسه\n"
                "/send متن\n"
                "/check"
            )

            return


        # ====================================================
        # 🚀 START
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

                await force_join(
                    update
                )

                return


            message = db[
                "settings"
            ].get(
                "start_message",
                "درود رفیق 😎🐮"
            )


            await update.reply(
                message
            )

            return


        # ====================================================
        # 👑 ADMIN COMMANDS
        # ====================================================

        if not is_admin(
            user_id
        ):

            return


        # ----------------------------------------------------
        # /startmsg
        # ----------------------------------------------------

        if command.startswith(
            "/startmsg "
        ):

            value = text[
                len("/startmsg "):
            ].strip()


            if not value:

                await update.reply(
                    "❌ متن خالی است."
                )

                return


            db[
                "settings"
            ][
                "start_message"
            ] = value


            save_db()


            await update.reply(
                "✅ پیام اولیه تغییر کرد."
            )

            return


        # ----------------------------------------------------
        # /channel
        # ----------------------------------------------------

        if command.startswith(
            "/channel "
        ):

            value = text[
                len("/channel "):
            ].strip()


            if not value:

                await update.reply(
                    "❌ لینک خالی است."
                )

                return


            db[
                "settings"
            ][
                "channel_link"
            ] = value


            save_db()


            await update.reply(
                "✅ لینک کانال تغییر کرد."
            )

            return


        # ----------------------------------------------------
        # /setchannel
        # ----------------------------------------------------

        if command.startswith(
            "/setchannel "
        ):

            value = text[
                len("/setchannel "):
            ].strip()


            if not value:

                await update.reply(
                    "❌ شناسه کانال خالی است."
                )

                return


            db[
                "settings"
            ][
                "channel_id"
            ] = value


            save_db()


            await update.reply(
                "✅ شناسه کانال ذخیره شد."
            )

            return


        # ----------------------------------------------------
        # /check
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # /send
        # ----------------------------------------------------

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


            sent = 0


            for uid in list(
                db["users"]
            ):

                try:

                    await client.send_message(
                        uid,
                        message
                    )

                    sent += 1

                except Exception as e:

                    print(
                        "SEND ERROR:",
                        repr(e)
                    )


            await update.reply(
                f"📨 پیام برای {sent} کاربر ارسال شد."
            )

            return


    except Exception as e:

        print(
            "❌ PRIVATE ERROR:",
            repr(e)
        )


# ============================================================
# 👥 GROUP HANDLER
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

        if not user_id:
            return

        if not chat_id:
            return


        print(
            "GROUP:",
            chat_id,
            repr(text)
        )


        command = text.strip().lower()


        # ====================================================
        # 🟢 فعال
        # ====================================================

        if command in (
            "/فعال",
            "فعال"
        ):

            db[
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


            save_db()


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
        # گروه فعال نیست
        # ====================================================

        if str(chat_id) not in db[
            "groups"
        ]:

            return


        group = db[
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
        # 😈 فضول روشن
        # ====================================================

        if command == "فضول روشن":

            if str(user_id) != owner:

                await update.reply(
                    "❌ فقط فعال‌کننده گروه می‌تواند این حالت را تغییر دهد."
                )

                return


            group[
                "fozool"
            ] = True


            save_db()


            await update.reply(
                "😈 فضول روشن شد!\n"
                "از پیام بعدی می‌پرم وسط 😂🐮"
            )

            return


        # ====================================================
        # 😇 فضول خاموش
        # ====================================================

        if command == "فضول خاموش":

            if str(user_id) != owner:

                await update.reply(
                    "❌ فقط فعال‌کننده گروه می‌تواند این حالت را تغییر دهد."
                )

                return


            group[
                "fozool"
            ] = False


            save_db()


            await update.reply(
                "😇 فضول خاموش شد!\n"
                "فقط با «گوخور» یا ریپلای جواب می‌دم."
            )

            return


        # ====================================================
        # 🧐 جدی روشن
        # ====================================================

        if command == "جدی روشن":

            if str(user_id) != owner:

                await update.reply(
                    "❌ فقط فعال‌کننده گروه می‌تواند این حالت را تغییر دهد."
                )

                return


            group[
                "serious"
            ] = True


            save_db()


            await update.reply(
                "🧐 حالت جدی روشن شد.\n"
                "از پیام بعدی جدی جواب می‌دم."
            )

            return


        # ====================================================
        # 😂 جدی خاموش
        # ====================================================

        if command == "جدی خاموش":

            if str(user_id) != owner:

                await update.reply(
                    "❌ فقط فعال‌کننده گروه می‌تواند این حالت را تغییر دهد."
                )

                return


            group[
                "serious"
            ] = False


            save_db()


            await update.reply(
                "😂 حالت جدی خاموش شد!\n"
                "گوخور برگشت به حالت شیطونی 🐮"
            )

            return


        # ====================================================
        # 🤖 تشخیص صدا زدن بات
        # ====================================================

        called = (

            command.startswith(
                "گوخور"
            )

            or

            command.startswith(
                "گو خور"
            )

            or

            command.startswith(
                "گوخور اضافی"
            )
        )


        replied = is_reply(
            update
        )


        # ====================================================
        # فضول خاموش
        # ====================================================

        if not group.get(
            "fozool",
            False
        ):

            if not called and not replied:

                return


        # ====================================================
        # 🤖 AI
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


    except Exception as e:

        print(
            "❌ GROUP ERROR:",
            repr(e)
        )


# ============================================================
# 🚀 RUN
# ============================================================

print(
    "======================================"
)

print(
    "🐮 گوخور اضافی روشن شد"
)

print(
    "📢 Channel:",
    CHANNEL_ID
)

print(
    "🤖 AI:",
    MODEL
)

print(
    "💾 DB:",
    DB_FILE
)

print(
    "======================================"
)


app.run()
