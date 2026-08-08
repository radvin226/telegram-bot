# ============================================================
# 🐮 گوخور اضافی
# Rubika Bot + Forced Channel + AI
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

BOT_TOKEN = "CBDJAI0TVGUZJHEDUNOIJUIFUETMMQPUZEUAKROMARQWYYLBGMIBGWOAJEKTGFZN"

HF_TOKEN = "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"

MODEL = "meta-llama/Llama-3.3-70B-Instruct"

CHANNEL_LINK = "rubika.ir/linkgokh"

# بعداً با /channelid مقدار واقعی اینجا ذخیره می‌شود
CHANNEL_ID = "c=c0DySFl0a7501a52aaea7d7381111798"

DB_FILE = "database.json"


# ============================================================
# DATABASE
# ============================================================

def default_db():
    return {
        "users": [],
        "admins": [],
        "groups": {},
        "settings": {
            "channel_id": CHANNEL_ID,
            "channel_link": CHANNEL_LINK,
            "start_message":
                "درود رفیق 😎🐮\n"
                "گوخور اضافی آماده‌ست 😂"
        }
    }


def load_db():

    if not os.path.exists(DB_FILE):

        data = default_db()

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
            "DATABASE ERROR:",
            repr(e)
        )

        data = default_db()


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

    try:

        with open(
            DB_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                db,
                f,
                ensure_ascii=False,
                indent=4
            )

    except Exception as e:

        print(
            "DATABASE SAVE ERROR:",
            repr(e)
        )


# ============================================================
# AI
# ============================================================

ai = InferenceClient(
    model=MODEL,
    provider="auto",
    api_key=HF_TOKEN,
    timeout=60
)


FUNNY_PROMPT = """
تو «گوخور اضافی» هستی 🐮😂

همیشه فارسی حرف بزن.

هرگز به جای درود از سلام استفاده نکن.

شخصیت:
- بامزه
- شیطون
- پرانرژی
- رفیق‌باز
- خلاق
- خودمانی

اگر کاربر شوخی کرد، شوخی کن.

اگر سؤال عجیب پرسید، خلاقانه جواب بده.

اگر سؤال جدی بود، دقیق جواب بده ولی خشک نباش.

گاهی تیکه‌های خیلی ملایم و دوستانه بینداز.

توهین سنگین نکن.

خودت را ChatGPT یا AI معرفی نکن.

اسم تو همیشه:
گوخور اضافی 🐮

مثال:

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
همونی که معمولاً بدون دعوت وسط بحث پیداش میشه 😂
"""


SERIOUS_PROMPT = """
تو «گوخور اضافی» هستی.

همیشه فارسی صحبت کن.

به جای سلام بگو درود.

حالت جدی فعال است.

شوخی نکن.

دقیق و مفید جواب بده.

ولی خشک و اداری حرف نزن.

اگر اسم خواستند:
درود، من گوخور اضافی هستم.
"""


async def ask_ai(text, serious=False):

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
            "AI RESPONSE:",
            repr(answer)
        )


        return answer


    except Exception as e:

        print(
            "AI ERROR:",
            repr(e)
        )


        return (
            "درود 😅🐮\n"
            "هوش مصنوعیم یه لحظه قاطی کرد!"
        )


# ============================================================
# BOT
# ============================================================

app = BotClient(
    BOT_TOKEN
)


print(
    "🐮 گوخور اضافی آماده است"
)


# ============================================================
# HELPERS
# ============================================================

def get_text(update):

    try:

        text = getattr(
            update.new_message,
            "text",
            None
        )

        return str(
            text or ""
        ).strip()

    except:

        return ""


def get_user_id(update):

    try:

        value = getattr(
            update.new_message,
            "sender_id",
            None
        )

        return str(
            value or ""
        )

    except:

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

    except:

        pass


    try:

        value = getattr(
            update.new_message,
            "chat_id",
            None
        )

        return str(
            value or ""
        )

    except:

        return ""


def is_reply(update):

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

    except:

        pass


    return False


def add_user(user_id):

    user_id = str(user_id)

    if (
        user_id
        and
        user_id not in db["users"]
    ):

        db["users"].append(
            user_id
        )

        save_db()


# ============================================================
# CHANNEL MEMBERSHIP
# ============================================================

async def check_membership(
    client,
    user_id
):

    channel_id = db[
        "settings"
    ].get(
        "channel_id",
        ""
    )


    if not channel_id:

        print(
            "❌ CHANNEL_ID NOT SET"
        )

        return None


    try:

        member = await client.get_chat_member(

            str(channel_id),

            str(user_id)
        )


        print(
            "CHANNEL MEMBER RESULT:",
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
            "CHANNEL STATUS:",
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
            "❌ MEMBERSHIP CHECK ERROR:",
            repr(e)
        )

        return None


# ============================================================
# FORCE JOIN MESSAGE
# ============================================================

async def force_join_message(update):

    await update.reply(
        "درود رفیق 🐮❤️\n\n"
        "برای استفاده از گوخور اضافی، "
        "اول داخل کانال زیر عضو شو 👇\n\n"
        f"📢 {db['settings']['channel_link']}\n\n"
        "بعد از عضویت دوباره /start رو بزن "
        "تا تأییدت کنم 😎🐮"
    )


# ============================================================
# PRIVATE
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


        if not text or not user_id:

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
        # START
        # ====================================================

        if command in (
            "/start",
            "start"
        ):

            result = await check_membership(

                client,

                user_id
            )


            # هنوز CHANNEL_ID تنظیم نشده
            if result is None:

                await update.reply(
                    "⚠️ عضویت اجباری هنوز تنظیم نشده.\n\n"
                    "ادمین باید اول دستور /channelid را "
                    "در کانال اجرا کند."
                )

                return


            # عضو نیست
            if result is False:

                await force_join_message(
                    update
                )

                return


            # عضو است
            await update.reply(
                "درود رفیق 😎🐮\n\n"
                "✅ عضویتت تأیید شد!\n\n"
                "گوخور اضافی آماده‌ست 😂\n"
                "بگو ببینم چه کاری داری؟"
            )

            return


        # ====================================================
        # ADMIN
        # ====================================================

        if command == "/admin":

            # اولین /admin مدیر اصلی
            if not db["admins"]:

                db["admins"].append(
                    str(user_id)
                )

                save_db()


                await update.reply(
                    "👑 دسترسی مدیریت برایت فعال شد."
                )


            if str(user_id) not in db["admins"]:

                await update.reply(
                    "❌ دسترسی مدیریت نداری."
                )

                return


            await update.reply(
"""
⚙️ پنل مدیریت گوخور اضافی

📢 تنظیم کانال:

/channelid

🔗 تغییر لینک:

/link rubika.ir/linkgokh

📝 تغییر پیام شروع:

/startmsg متن جدید

📨 ارسال پیام به کاربران:

/send متن

🔎 تست عضویت:

/check
"""
            )

            return


        # ====================================================
        # ADMIN COMMANDS
        # ====================================================

        if str(user_id) not in db["admins"]:

            return


        # ====================================================
        # CHANNEL ID
        # ====================================================

        if command == "/channelid":

            # چون این دستور در PV اجرا می‌شود،
            # شناسه کانال را از اینجا نمی‌توان حدس زد.
            #
            # بنابراین کانال باید پیام /channelid را
            # به بات فوروارد کند یا شناسه چت آن را
            # از آپدیت کانال دریافت کنیم.

            await update.reply(
                "📢 برای تنظیم کانال، ربات باید یک پیام "
                "از خود کانال دریافت کند.\n\n"
                "یک پیام در کانال بفرست و دستور "
                "/channelid را همان‌جا ارسال کن."
            )

            return


        # ====================================================
        # LINK
        # ====================================================

        if command.startswith(
            "/link "
        ):

            value = text[
                len("/link "):
            ].strip()


            if value:

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


        # ====================================================
        # START MESSAGE
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

                save_db()


                await update.reply(
                    "✅ پیام اولیه تغییر کرد."
                )

            return


        # ====================================================
        # BROADCAST
        # ====================================================

        if command.startswith(
            "/send "
        ):

            value = text[
                len("/send "):
            ].strip()


            count = 0


            for uid in list(
                db["users"]
            ):

                try:

                    await client.send_message(
                        uid,
                        value
                    )

                    count += 1

                except Exception as e:

                    print(
                        "SEND ERROR:",
                        repr(e)
                    )


            await update.reply(
                f"📨 برای {count} کاربر ارسال شد."
            )

            return


        # ====================================================
        # CHECK
        # ====================================================

        if command == "/check":

            result = await check_membership(
                client,
                user_id
            )


            if result is True:

                await update.reply(
                    "✅ عضویت تأیید شد."
                )

            elif result is False:

                await update.reply(
                    "❌ عضویت تأیید نشد."
                )

            else:

                await update.reply(
                    "⚠️ CHANNEL_ID تنظیم نشده."
                )

            return


    except Exception as e:

        print(
            "PRIVATE ERROR:",
            repr(e)
        )


# ============================================================
# CHANNEL HANDLER
# ============================================================

@app.on_update(
    filters.text
)
async def channel_and_group_handler(
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


        print(
            "CHAT:",
            chat_id,
            repr(text)
        )


        # ====================================================
        # ثبت شناسه کانال با دستور
        # ====================================================

        if text.strip().lower() == "/channelid":

            if str(user_id) not in db["admins"]:

                return


            db[
                "settings"
            ][
                "channel_id"
            ] = str(chat_id)


            save_db()


            await update.reply(
                "✅ کانال عضویت اجباری تنظیم شد.\n\n"
                f"🆔 Channel ID:\n{chat_id}"
            )

            return


        # ====================================================
        # گروه
        # ====================================================

        command = text.strip().lower()


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
"""
🐮 گوخور اضافی فعال شد!

📌 دستورات:

😈 فضول روشن
😇 فضول خاموش

🧐 جدی روشن
😂 جدی خاموش

🤖 گوخور سلام

یا روی پیام ریپلای کن.
"""
            )

            return


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
        # FOZOOL
        # ====================================================

        if command == "فضول روشن":

            if str(user_id) != owner:

                await update.reply(
                    "❌ فقط فعال‌کننده گروه."
                )

                return


            group[
                "fozool"
            ] = True

            save_db()


            await update.reply(
                "😈 فضول روشن شد!"
            )

            return


        if command == "فضول خاموش":

            if str(user_id) != owner:

                await update.reply(
                    "❌ فقط فعال‌کننده گروه."
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
        # SERIOUS
        # ====================================================

        if command == "جدی روشن":

            if str(user_id) != owner:

                await update.reply(
                    "❌ فقط فعال‌کننده گروه."
                )

                return


            group[
                "serious"
            ] = True

            save_db()


            await update.reply(
                "🧐 حالت جدی روشن شد."
            )

            return


        if command == "جدی خاموش":

            if str(user_id) != owner:

                await update.reply(
                    "❌ فقط فعال‌کننده گروه."
                )

                return


            group[
                "serious"
            ] = False

            save_db()


            await update.reply(
                "😂 حالت جدی خاموش شد!"
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


        replied = is_reply(
            update
        )


        if not group.get(
            "fozool",
            False
        ):

            if not called and not replied:

                return


        answer = await ask_ai(

            text,

            group.get(
                "serious",
                False
            )
        )


        await update.reply(
            answer
        )


    except Exception as e:

        print(
            "CHAT HANDLER ERROR:",
            repr(e)
        )


# ============================================================
# RUN
# ============================================================

print(
    "🐮 گوخور اضافی روشن شد"
)

print(
    "📢 Channel:",
    CHANNEL_LINK
)

print(
    "🤖 Model:",
    MODEL
)

print(
    "================================"
)


app.run()
