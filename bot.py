# ============================================================
# 🐮 گوخور اضافی
# Rubika Bot + Forced Channel Membership + HuggingFace AI
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

# مدل جدید - Qwen نیست
MODEL = "meta-llama/Llama-3.3-70B-Instruct"

# لینک کانال برای نمایش به کاربر
CHANNEL_LINK = "https://rubika.ir/linkgokh"

# خیلی مهم:
# شناسه واقعی کانال را اینجا بگذار.
#
# اگر نسخه rubpy تو لینک کانال را به عنوان chat_id قبول می‌کند:
# CHANNEL_ID = "rubika.ir/linkgokh"
#
# در غیر این صورت شناسه کانال را قرار بده.
CHANNEL_ID = "rubika.ir/linkgokh"

DATABASE_FILE = "database.json"


# ============================================================
# دیتابیس
# ============================================================

def create_default_database():

    return {
        "users": [],
        "admins": [],

        "groups": {},

        "settings": {
            "channel_id": CHANNEL_ID,
            "channel_link": CHANNEL_LINK,

            "start_message": (
                "درود رفیق 😎🐮\n\n"
                "من گوخور اضافی‌ام!\n"
                "بگو ببینم چه کاری داری 😂"
            )
        }
    }


def load_database():

    if not os.path.exists(DATABASE_FILE):

        data = create_default_database()

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

        data = create_default_database()


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
        "درود رفیق 😎🐮\nگوخور اضافی هستم!"
    )


    # سازگاری گروه‌های قبلی

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


database = load_database()


def save_database():

    try:

        with open(
            DATABASE_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                database,
                file,
                ensure_ascii=False,
                indent=4
            )

    except Exception as error:

        print(
            "❌ DATABASE SAVE ERROR:",
            repr(error)
        )


# ============================================================
# کاربران
# ============================================================

def add_user(user_id):

    user_id = str(user_id)

    if not user_id:
        return

    if user_id not in database["users"]:

        database["users"].append(
            user_id
        )

        save_database()


# ============================================================
# ادمین
# ============================================================

def is_admin(user_id):

    return str(user_id) in database["admins"]


def add_admin(user_id):

    user_id = str(user_id)

    if user_id not in database["admins"]:

        database["admins"].append(
            user_id
        )

        save_database()


# ============================================================
# HuggingFace
# ============================================================

ai = InferenceClient(

    model=MODEL,

    provider="auto",

    api_key=HF_TOKEN,

    timeout=60
)


# ============================================================
# شخصیت گوخور اضافی
# ============================================================

FUNNY_SYSTEM = """
تو «گوخور اضافی» هستی 🐮😂

یک هوش مصنوعی فارسی‌زبان بامزه، شیطون، پرانرژی و رفیق‌باز.

قوانین اصلی:

1. همیشه فارسی جواب بده.

2. به جای «سلام» همیشه «درود» بگو.

3. خشک و رباتی حرف نزن.

4. اگر کاربر شوخی کرد، شوخی کن.

5. اگر سؤال عجیب پرسید، خلاقانه جواب بده.

6. اگر سؤال جدی پرسید، جواب دقیق بده ولی لحن را انسانی نگه دار.

7. گاهی از 😂 😎 🐮 استفاده کن.

8. تیکه‌های دوستانه و خیلی ملایم مجاز هستند.

9. توهین سنگین، تحقیر و تهدید ممنوع است.

10. خودت را ChatGPT یا AI معرفی نکن.

11. اگر پرسید اسمت چیست، بگو:
«درود 😎 من گوخور اضافی‌ام 🐮»

12. جواب‌های خیلی طولانی و بی‌دلیل نده.

13. مثل یک رفیق واقعی صحبت کن.

مثال:

کاربر:
درود

تو:
درود رفیق 😎🐮
گوخور اضافی حاضر و آماده‌ست!
بگو ببینم چه نقشه‌ای داری؟ 😂

کاربر:
چه خبر؟

تو:
درود 😂
خبر خاصی نیست، منم اینجام دارم به زندگی دیجیتالیم ادامه می‌دم 🐮

کاربر:
چرا فضولی می‌کنی؟

تو:
چون گوخور اضافی‌ام دیگه 😂
اسممو که الکی نذاشتن!
"""


SERIOUS_SYSTEM = """
تو «گوخور اضافی» هستی.

حالت جدی فعال است.

همیشه فارسی صحبت کن.

به جای سلام بگو:
درود

شوخی نکن.

جواب‌ها دقیق، واضح و مفید باشند.

خشک و اداری حرف نزن.

اگر اسم خواستند:
«درود، من گوخور اضافی هستم.»

خودت را ChatGPT یا AI معرفی نکن.
"""


# ============================================================
# درخواست AI
# ============================================================

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


        answer = str(
            answer
        ).strip()


        print(
            "🤖 AI RESPONSE:",
            repr(answer)
        )


        return answer


    except Exception as error:

        print(
            "================================"
        )

        print(
            "❌ AI ERROR:"
        )

        print(
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
# ساخت بات
# ============================================================

app = BotClient(
    BOT_TOKEN
)


print(
    "🐮 گوخور اضافی آماده است"
)


# ============================================================
# گرفتن متن
# ============================================================

def get_text(update):

    try:

        message = update.new_message

    except Exception:

        return ""


    try:

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


# ============================================================
# گرفتن user id
# ============================================================

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


# ============================================================
# گرفتن chat id
# ============================================================

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


# ============================================================
# تشخیص ریپلای
# ============================================================

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

    except Exception:

        pass


    return False


# ============================================================
# پاک کردن دستور
# ============================================================

def command_name(text):

    text = str(
        text
    ).strip()

    if text.startswith("/"):

        text = text[1:]


    return text.strip().lower()


# ============================================================
# بررسی عضویت در کانال
# ============================================================

async def check_membership(
    client,
    user_id
):

    channel_id = database[
        "settings"
    ].get(
        "channel_id",
        CHANNEL_ID
    )


    print(
        "🔎 CHECK CHANNEL:",
        channel_id,
        "USER:",
        user_id
    )


    try:

        member = await client.get_chat_member(

            str(channel_id),

            str(user_id)
        )


        print(
            "📢 MEMBER RESULT:",
            repr(member)
        )


        # --------------------------------------------
        # status
        # --------------------------------------------

        status = ""


        try:

            status = str(
                getattr(
                    member,
                    "status",
                    ""
                )
            ).lower()

        except Exception:

            pass


        print(
            "📢 MEMBER STATUS:",
            status
        )


        # عضو عادی / ادمین / مالک

        if status in (
            "member",
            "administrator",
            "admin",
            "owner",
            "creator"
        ):

            return True


        # --------------------------------------------
        # بعضی نسخه‌ها آبجکت متفاوت می‌دهند
        # --------------------------------------------

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
            "❌ CHANNEL MEMBERSHIP ERROR:"
        )

        print(
            repr(error)
        )

        print(
            "================================"
        )

        return False


# ============================================================
# پیام عضویت اجباری
# ============================================================

async def send_join_message(
    update
):

    channel = database[
        "settings"
    ].get(
        "channel_link",
        CHANNEL_LINK
    )


    await update.reply(

        "درود رفیق 🐮❤️\n\n"

        "برای استفاده از «گوخور اضافی» "
        "اول باید عضو کانال زیر بشی 👇\n\n"

        "📢 کانال:\n"

        f"{channel}\n\n"

        "بعد از عضویت دوباره /start رو بزن "
        "تا عضویتت رو بررسی کنم 😎🐮"
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


        if not text:

            return


        if not user_id:

            print(
                "❌ PRIVATE USER ID NOT FOUND"
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


        # ==================================================
        # START
        # ==================================================

        if command == "start":

            is_member = await check_membership(

                client,

                user_id
            )


            # ----------------------------------------------
            # عضو نیست
            # ----------------------------------------------

            if not is_member:

                await send_join_message(
                    update
                )

                return


            # ----------------------------------------------
            # عضو است
            # ----------------------------------------------

            await update.reply(

                "درود رفیق 😎🐮\n\n"

                "✅ عضویتت تأیید شد!\n\n"

                "گوخور اضافی آماده‌ست 😂\n\n"

                "بگو ببینم چه کاری داری؟"
            )

            return


        # ==================================================
        # ADMIN
        # ==================================================

        if command == "admin":

            # اولین نفری که /admin می‌زند
            # مدیر می‌شود

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

channel rubika.ir/linkgokh


📝 تغییر لینک کانال:

link rubika.ir/linkgokh


📝 تغییر پیام اولیه:

start متن جدید


📨 ارسال همگانی:

send متن


برای تست عضویت:

check
"""
            )

            return


        # ==================================================
        # دستورات ادمین
        # ==================================================

        if is_admin(
            user_id
        ):

            # ----------------------------------------------
            # تغییر chat id کانال
            # ----------------------------------------------

            if text.startswith(
                "channel "
            ):

                value = text[
                    len("channel "):
                ].strip()


                if value:

                    database[
                        "settings"
                    ][
                        "channel_id"
                    ] = value

                    save_database()


                    await update.reply(
                        "✅ شناسه کانال تغییر کرد."
                    )

                return


            # ----------------------------------------------
            # تغییر لینک
            # ----------------------------------------------

            if text.startswith(
                "link "
            ):

                value = text[
                    len("link "):
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


            # ----------------------------------------------
            # تغییر پیام start
            # ----------------------------------------------

            if text.startswith(
                "start "
            ):

                value = text[
                    len("start "):
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


            # ----------------------------------------------
            # ارسال همگانی
            # ----------------------------------------------

            if text.startswith(
                "send "
            ):

                value = text[
                    len("send "):
                ].strip()


                if not value:

                    await update.reply(
                        "❌ متن پیام خالی است."
                    )

                    return


                count = 0


                for uid in list(
                    database["users"]
                ):

                    try:

                        await client.send_message(
                            uid,
                            value
                        )

                        count += 1

                    except Exception as error:

                        print(
                            "SEND ERROR:",
                            uid,
                            repr(error)
                        )


                await update.reply(
                    f"📨 پیام برای {count} کاربر ارسال شد."
                )

                return


            # ----------------------------------------------
            # تست عضویت خود ادمین
            # ----------------------------------------------

            if command == "check":

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
                        "❌ عضویت تأیید نشد.\n\n"
                        "اگر مطمئنی عضو کانالی، "
                        "لاگ CHANNEL MEMBERSHIP ERROR "
                        "را در ترمینال بررسی کن."
                    )

                return


    except Exception as error:

        print(
            "================================"
        )

        print(
            "❌ PRIVATE HANDLER ERROR:"
        )

        print(
            repr(error)
        )

        print(
            "================================"
        )


# ============================================================
# GROUP
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

            print(
                "❌ GROUP USER ID NOT FOUND"
            )

            return


        if not chat_id:

            print(
                "❌ GROUP CHAT ID NOT FOUND"
            )

            return


        print(
            "GROUP:",
            chat_id,
            repr(text)
        )


        command = text.strip()

        command_lower = command.lower()


        # ==================================================
        # فعال سازی
        # ==================================================

        if command_lower in (
            "/فعال",
            "فعال"
        ):

            if chat_id not in database[
                "groups"
            ]:

                database[
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

            else:

                database[
                    "groups"
                ][
                    chat_id
                ][
                    "active"
                ] = True


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


        # ==================================================
        # گروه فعال نیست
        # ==================================================

        if chat_id not in database[
            "groups"
        ]:

            return


        group = database[
            "groups"
        ][
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


        # ==================================================
        # فضول روشن
        # ==================================================

        if command_lower == "فضول روشن":

            if str(user_id) != owner:

                await update.reply(
                    "❌ فقط فعال‌کننده گروه می‌تواند این حالت را تغییر دهد."
                )

                return


            group[
                "fozool"
            ] = True

            save_database()


            await update.reply(
                "😈 فضول روشن شد!\n"
                "از پیام بعدی می‌پرم وسط 😂🐮"
            )

            return


        # ==================================================
        # فضول خاموش
        # ==================================================

        if command_lower == "فضول خاموش":

            if str(user_id) != owner:

                await update.reply(
                    "❌ فقط فعال‌کننده گروه می‌تواند این حالت را تغییر دهد."
                )

                return


            group[
                "fozool"
            ] = False

            save_database()


            await update.reply(
                "😇 فضول خاموش شد!\n"
                "فقط با «گوخور» یا ریپلای صدام کن."
            )

            return


        # ==================================================
        # جدی روشن
        # ==================================================

        if command_lower == "جدی روشن":

            if str(user_id) != owner:

                await update.reply(
                    "❌ فقط فعال‌کننده گروه می‌تواند این حالت را تغییر دهد."
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


        # ==================================================
        # جدی خاموش
        # ==================================================

        if command_lower == "جدی خاموش":

            if str(user_id) != owner:

                await update.reply(
                    "❌ فقط فعال‌کننده گروه می‌تواند این حالت را تغییر دهد."
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


        # ==================================================
        # تشخیص صدا زدن
        # ==================================================

        called = (

            command_lower.startswith(
                "گوخور"
            )

            or

            command_lower.startswith(
                "گو خور"
            )

            or

            command_lower.startswith(
                "گوخور اضافی"
            )
        )


        replied = is_reply(
            update
        )


        # ==================================================
        # اگر فضول خاموش است
        # ==================================================

        if not group.get(
            "fozool",
            False
        ):

            if not called and not replied:

                return


        # ==================================================
        # AI
        # ==================================================

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
            "================================"
        )

        print(
            "❌ GROUP HANDLER ERROR:"
        )

        print(
            repr(error)
        )

        print(
            "================================"
        )


# ============================================================
# RUN
# ============================================================

print(
    "========================================"
)

print(
    "🐮 گوخور اضافی روشن شد"
)

print(
    "📢 Channel:",
    database["settings"]["channel_link"]
)

print(
    "🤖 Model:",
    MODEL
)

print(
    "========================================"
)


app.run()
