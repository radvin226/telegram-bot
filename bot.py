# ============================================================
#                  VOIDCHATER 🐮
#             Telegram AI Group Bot
# ============================================================

import os
import json
import time
import threading

import telebot
from telebot import types
from huggingface_hub import InferenceClient


# ============================================================
# CONFIG
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
HF_TOKEN = os.getenv("HF_TOKEN", "").strip()

AI_MODEL = os.getenv(
    "AI_MODEL",
    "meta-llama/Llama-3.3-70B-Instruct"
).strip()

DB_FILE = "database.json"


if not BOT_TOKEN:
    raise RuntimeError(
        "❌ BOT_TOKEN در Railway Variables تنظیم نشده است."
    )

if not HF_TOKEN:
    raise RuntimeError(
        "❌ HF_TOKEN در Railway Variables تنظیم نشده است."
    )


# ============================================================
# BOT
# ============================================================

bot = telebot.TeleBot(
    BOT_TOKEN,
    parse_mode="HTML",
    threaded=True
)


# ============================================================
# DATABASE
# ============================================================

db_lock = threading.Lock()


def default_database():

    return {
        "admins": [],
        "users": [],

        "groups": {},

        "settings": {
            "start_message":
                "درود رفیق 😂🐮\n\n"
                "من <b>voidchater</b> هستم.\n"
                "گوخور اضافی آماده‌ست!"
        }
    }


def save_db():

    with db_lock:

        temp_file = DB_FILE + ".tmp"

        with open(
            temp_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                database,
                f,
                ensure_ascii=False,
                indent=4
            )

        os.replace(
            temp_file,
            DB_FILE
        )


def load_db():

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
            "DATABASE ERROR:",
            repr(e)
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
        "start_message",
        "درود رفیق 😂🐮"
    )

    return data


database = load_db()


# ============================================================
# DATABASE HELPERS
# ============================================================

def add_user(user_id):

    uid = str(user_id)

    if uid not in database["users"]:

        database["users"].append(
            uid
        )

        save_db()


def add_admin(user_id):

    uid = str(user_id)

    if uid not in database["admins"]:

        database["admins"].append(
            uid
        )

        save_db()


def is_admin(user_id):

    return str(user_id) in [
        str(x)
        for x in database["admins"]
    ]


# ============================================================
# AI PERSONALITY
# ============================================================

FUNNY_SYSTEM = r"""
تو «گوخور اضافی» هستی 😂🐮

شخصیت تو:

- بددهن
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

4. اگر کاربر پرسید اسمت چیه:
«😎 من گوخور اضافی‌ام»

5. اگر کاربر شوخی کرد، شوخی کن.

6. اگر سؤال خیلی عجیب پرسید،
با لحن شوخی بگو:
«خیلی خری 😂»

7. تیکه‌های سنگین و شوخی‌های تند داشته باش،
ولی تهدید، نفرت‌پراکنی یا توهین به گروه‌های محافظت‌شده نکن.

8. اگر سؤال علمی یا جدی بود،
درست و مفید جواب بده.

9. جواب‌ها طبیعی باشند، نه خشک و رباتی.

10. از ایموجی زیاد ولی طبیعی استفاده کن.

11. زیادی توضیح اضافه نده مگر اینکه کاربر درخواست کند.

12. اگر کاربر گفت سلام:

«درود رفیق 😂
گوخور اضافی حاضر شد!
بگو ببینم چه نقشه‌ای داری؟»

13. اگر کاربر پرسید اسمت چیه:

«گوخور اضافی‌ام 😂
همونی که بی‌دعوت وسط بحث پیداش میشه.»

14. اگر کاربر پرسید چه خبر،
خودمانی و بامزه جواب بده.

15. همیشه فارسی صحبت کن.
"""


SERIOUS_SYSTEM = r"""
تو «گوخور اضافی» هستی.

حالت جدی فعال است.

همیشه فارسی صحبت کن.

به جای «سلام» بگو «درود».

شوخی نکن.

جواب دقیق، واضح و مفید بده.

خشک و اداری باش.

خودت را ChatGPT معرفی نکن.

اگر اسم پرسیده شد بگو:

«درود، من گوخور اضافی بودم،
ولی الان گوخور کت‌شلواری‌ام.»
"""


# ============================================================
# AI
# ============================================================

ai = InferenceClient(
    api_key=HF_TOKEN
)


def ask_ai(
    text,
    serious=False
):

    system = (
        SERIOUS_SYSTEM
        if serious
        else FUNNY_SYSTEM
    )

    try:

        result = ai.chat_completion(

            model=AI_MODEL,

            messages=[

                {
                    "role": "system",
                    "content": system
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
# MAIN INLINE KEYBOARD
# ============================================================

def main_keyboard():

    keyboard = types.InlineKeyboardMarkup(
        row_width=2
    )


    keyboard.add(

        types.InlineKeyboardButton(
            "🤖 شروع گفتگو",
            callback_data="chat"
        ),

        types.InlineKeyboardButton(
            "🛠 تنظیمات",
            callback_data="settings"
        )
    )


    keyboard.add(

        types.InlineKeyboardButton(
            "📞 پشتیبانی",
            callback_data="support"
        ),

        types.InlineKeyboardButton(
            "📦 محصولات",
            callback_data="products"
        )
    )


    keyboard.add(

        types.InlineKeyboardButton(
            "📋 دستورات",
            callback_data="commands"
        )
    )


    return keyboard


# ============================================================
# ADMIN KEYBOARD
# ============================================================

def admin_keyboard():

    keyboard = types.InlineKeyboardMarkup(
        row_width=2
    )


    keyboard.add(

        types.InlineKeyboardButton(
            "📋 دستورات",
            callback_data="commands"
        ),

        types.InlineKeyboardButton(
            "👑 وضعیت من",
            callback_data="admin_status"
        )
    )


    keyboard.add(

        types.InlineKeyboardButton(
            "⚙️ تنظیمات",
            callback_data="settings"
        )
    )


    return keyboard


# ============================================================
# GROUP KEYBOARD
# ============================================================

def group_keyboard():

    keyboard = types.InlineKeyboardMarkup(
        row_width=2
    )


    keyboard.add(

        types.InlineKeyboardButton(
            "📋 دستورات",
            callback_data="commands"
        ),

        types.InlineKeyboardButton(
            "😈 وضعیت فضول",
            callback_data="fozool_status"
        )
    )


    keyboard.add(

        types.InlineKeyboardButton(
            "🧐 وضعیت جدی",
            callback_data="serious_status"
        )
    )


    return keyboard


# ============================================================
# COMMAND LIST
# ============================================================

def commands_text():

    return (
        "🐮 <b>دستورات voidchater</b>\n\n"

        "👑 <b>مدیریت</b>\n"
        "/admin — ادمین شدن در PV\n"
        "/admins — لیست ادمین‌های گروه\n\n"

        "🟢 <b>فعال‌سازی گروه</b>\n"
        "<code>فعال</code>\n\n"

        "😈 <b>فضول</b>\n"
        "فضول روشن\n"
        "فضول خاموش\n\n"

        "🧐 <b>حالت جدی</b>\n"
        "جدی روشن\n"
        "جدی خاموش\n\n"

        "🤖 <b>هوش مصنوعی</b>\n"
        "گوخور سلام\n\n"

        "یا روی پیام بات ریپلای کن."
    )


# ============================================================
# START
# ============================================================

@bot.message_handler(
    commands=["start"]
)
def start_handler(message):

    try:

        add_user(
            message.from_user.id
        )


        bot.send_message(

            message.chat.id,

            database[
                "settings"
            ].get(
                "start_message",
                "درود رفیق 😂🐮"
            ),

            reply_markup=main_keyboard()
        )


    except Exception as e:

        print(
            "START ERROR:",
            repr(e)
        )


# ============================================================
# ADMIN
# ============================================================

@bot.message_handler(
    commands=["admin"]
)
def admin_handler(message):

    try:

        # فقط PV
        if message.chat.type != "private":

            bot.reply_to(

                message,

                "👤 این دستور رو داخل PV خودم بزن."
            )

            return


        user_id = message.from_user.id


        add_user(
            user_id
        )


        # بدون نیاز به ID دستی
        add_admin(
            user_id
        )


        bot.send_message(

            message.chat.id,

            "👑 <b>ادمین فعال شد!</b>\n\n"

            "دسترسی مدیریت برای این حساب "
            "با موفقیت فعال شد. 😎🐮\n\n"

            "از منوی زیر استفاده کن:",

            reply_markup=admin_keyboard()
        )


    except Exception as e:

        print(
            "ADMIN ERROR:",
            repr(e)
        )


# ============================================================
# ACTIVATE GROUP
# فقط «فعال»
# ============================================================

@bot.message_handler(
    func=lambda message:

        message.chat.type in [
            "group",
            "supergroup"
        ]

        and

        message.text

        and

        message.text.strip().lower()
        == "فعال"
)
def activate_group(message):

    try:

        chat_id = message.chat.id

        user_id = message.from_user.id


        # ------------------------------------------
        # بررسی ادمین گروه
        # ------------------------------------------

        member = bot.get_chat_member(

            chat_id,

            user_id
        )


        if member.status not in [
            "administrator",
            "creator"
        ]:

            bot.reply_to(

                message,

                "❌ فقط ادمین گروه می‌تواند "
                "بات را فعال کند."
            )

            return


        # ------------------------------------------
        # ذخیره گروه
        # ------------------------------------------

        database[
            "groups"
        ][
            str(chat_id)
        ] = {

            "active": True,

            "owner": user_id,

            "fozool": False,

            "serious": False
        }


        save_db()


        # ------------------------------------------
        # گرفتن ادمین‌های گروه
        # ------------------------------------------

        admins = bot.get_chat_administrators(
            chat_id
        )


        admin_lines = []


        for admin in admins:

            user = admin.user


            name = (
                user.first_name
                or
                "بدون نام"
            )


            if user.username:

                display = (
                    f"@{user.username}"
                )

            else:

                display = name


            if admin.status == "creator":

                role = "👑 مالک"

            else:

                role = "🛡 ادمین"


            admin_lines.append(
                f"{role} — {display}"
            )


        admins_text = "\n".join(
            admin_lines
        )


        if not admins_text:

            admins_text = (
                "ادمین‌ها پیدا نشدن."
            )


        # ------------------------------------------
        # پیام فعال شدن
        # ------------------------------------------

        bot.send_message(

            chat_id,

            "🐮 <b>گوخور اضافی فعال شد!</b>\n\n"

            "👑 <b>ادمین‌های این گروه:</b>\n\n"

            f"{admins_text}\n\n"

            "❤️ اینا مالکای منن!\n"

            "ولی من بیشتر "
            "<b>رادوین</b> "
            "و <b>ایران</b> رو دوست دارم 🇮🇷😂\n\n"

            "📋 <b>دستورات:</b>\n\n"

            "😈 فضول روشن\n"
            "😇 فضول خاموش\n\n"

            "🧐 جدی روشن\n"
            "😂 جدی خاموش\n\n"

            "🤖 گوخور سلام\n\n"

            "یا روی پیام من ریپلای کن.",

            reply_markup=group_keyboard()
        )


    except Exception as e:

        print(
            "ACTIVATE ERROR:",
            repr(e)
        )


        bot.reply_to(

            message,

            "❌ هنگام فعال‌سازی خطایی رخ داد."
        )


# ============================================================
# FOZOOL
# ============================================================

@bot.message_handler(
    func=lambda message:

        message.chat.type in [
            "group",
            "supergroup"
        ]

        and

        message.text

        and

        message.text.strip().lower()
        in [
            "فضول روشن",
            "فضول خاموش"
        ]
)
def fozool_handler(message):

    try:

        chat_id = message.chat.id

        user_id = message.from_user.id


        group = database[
            "groups"
        ].get(
            str(chat_id)
        )


        if not group:

            return


        if not group.get(
            "active",
            False
        ):

            return


        # فقط صاحب فعال‌کننده
        if user_id != group.get(
            "owner"
        ):

            bot.reply_to(

                message,

                "❌ فقط ادمین فعال‌کننده "
                "می‌تواند این حالت را تغییر دهد."
            )

            return


        command = (
            message.text
            .strip()
            .lower()
        )


        if command == "فضول روشن":

            group[
                "fozool"
            ] = True

            save_db()


            bot.reply_to(

                message,

                "😈 <b>فضول روشن شد!</b>\n"
                "از پیام بعدی می‌پرم وسط 😂🐮"
            )

            return


        if command == "فضول خاموش":

            group[
                "fozool"
            ] = False

            save_db()


            bot.reply_to(

                message,

                "😇 <b>فضول خاموش شد!</b>\n"
                "فقط با «گوخور» یا ریپلای جواب می‌دم."
            )


    except Exception as e:

        print(
            "FOZOOL ERROR:",
            repr(e)
        )


# ============================================================
# SERIOUS
# ============================================================

@bot.message_handler(
    func=lambda message:

        message.chat.type in [
            "group",
            "supergroup"
        ]

        and

        message.text

        and

        message.text.strip().lower()
        in [
            "جدی روشن",
            "جدی خاموش"
        ]
)
def serious_handler(message):

    try:

        chat_id = message.chat.id

        user_id = message.from_user.id


        group = database[
            "groups"
        ].get(
            str(chat_id)
        )


        if not group:

            return


        if not group.get(
            "active",
            False
        ):

            return


        if user_id != group.get(
            "owner"
        ):

            bot.reply_to(

                message,

                "❌ فقط ادمین فعال‌کننده "
                "می‌تواند این حالت را تغییر دهد."
            )

            return


        command = (
            message.text
            .strip()
            .lower()
        )


        if command == "جدی روشن":

            group[
                "serious"
            ] = True

            save_db()


            bot.reply_to(

                message,

                "🧐 <b>حالت جدی روشن شد!</b>\n"
                "از پیام بعدی جدی جواب می‌دم."
            )

            return


        if command == "جدی خاموش":

            group[
                "serious"
            ] = False

            save_db()


            bot.reply_to(

                message,

                "😂 <b>حالت جدی خاموش شد!</b>\n"
                "گوخور برگشت به حالت شیطونی 🐮"
            )


    except Exception as e:

        print(
            "SERIOUS ERROR:",
            repr(e)
        )


# ============================================================
# ADMINS COMMAND
# ============================================================

@bot.message_handler(
    commands=["admins"]
)
def admins_command(message):

    if message.chat.type not in [
        "group",
        "supergroup"
    ]:

        return


    try:

        admins = bot.get_chat_administrators(
            message.chat.id
        )


        lines = []


        for admin in admins:

            user = admin.user


            name = (
                user.first_name
                or
                "بدون نام"
            )


            if user.username:

                name += (
                    f" (@{user.username})"
                )


            if admin.status == "creator":

                role = "👑 مالک"

            else:

                role = "🛡 ادمین"


            lines.append(
                f"{role} — {name}"
            )


        bot.send_message(

            message.chat.id,

            "👑 <b>ادمین‌های گروه:</b>\n\n"

            +
            "\n".join(lines)
        )


    except Exception as e:

        print(
            "ADMINS ERROR:",
            repr(e)
        )


        bot.reply_to(

            message,

            "❌ نتونستم ادمین‌های گروه رو دریافت کنم."
        )


# ============================================================
# GROUP AI
# ============================================================

@bot.message_handler(
    func=lambda message:

        message.chat.type in [
            "group",
            "supergroup"
        ]

        and

        bool(message.text)
)
def group_ai_handler(message):

    try:

        text = (
            message.text
            .strip()
        )


        command = text.lower()


        # دستورات
        if command in [
            "فعال",
            "فضول روشن",
            "فضول خاموش",
            "جدی روشن",
            "جدی خاموش"
        ]:

            return


        group = database[
            "groups"
        ].get(
            str(message.chat.id)
        )


        if not group:

            return


        if not group.get(
            "active",
            False
        ):

            return


        # ------------------------------------------
        # آیا با «گوخور» صدا زده شده؟
        # ------------------------------------------

        called = (

            command.startswith(
                "گوخور"
            )

            or

            command.startswith(
                "گو خور"
            )
        )


        # ------------------------------------------
        # آیا روی پیام بات ریپلای شده؟
        # ------------------------------------------

        replied_to_bot = False


        if message.reply_to_message:

            replied = (
                message.reply_to_message
            )


            if replied.from_user:

                try:

                    me = bot.get_me()


                    replied_to_bot = (

                        replied.from_user.id
                        ==
                        me.id
                    )

                except Exception:

                    replied_to_bot = False


        # ------------------------------------------
        # فضول خاموش
        # ------------------------------------------

        if not group.get(
            "fozool",
            False
        ):

            if not called and not replied_to_bot:

                return


        # ------------------------------------------
        # AI
        # ------------------------------------------

        answer = ask_ai(

            text,

            serious=group.get(
                "serious",
                False
            )
        )


        bot.reply_to(

            message,

            answer
        )


    except Exception as e:

        print(
            "GROUP AI ERROR:",
            repr(e)
        )


# ============================================================
# CALLBACK BUTTONS
# ============================================================

@bot.callback_query_handler(
    func=lambda call: True
)
def callback_handler(call):

    try:

        data = call.data

        chat_id = call.message.chat.id

        user_id = call.from_user.id


        # ====================================================
        # COMMANDS
        # ====================================================

        if data == "commands":

            bot.answer_callback_query(
                call.id
            )


            bot.send_message(

                chat_id,

                commands_text()
            )

            return


        # ====================================================
        # CHAT
        # ====================================================

        if data == "chat":

            bot.answer_callback_query(

                call.id,

                "حاضرم 😂🐮"
            )


            bot.send_message(

                chat_id,

                "درود 😂🐮\n\n"
                "پیامت رو بفرست.\n"
                "من حاضرم."
            )

            return


        # ====================================================
        # SUPPORT
        # ====================================================

        if data == "support":

            bot.answer_callback_query(
                call.id
            )


            bot.send_message(

                chat_id,

                "📞 <b>پشتیبانی</b>\n\n"
                "پیامت رو همینجا بفرست."
            )

            return


        # ====================================================
        # PRODUCTS
        # ====================================================

        if data == "products":

            bot.answer_callback_query(
                call.id
            )


            bot.send_message(

                chat_id,

                "📦 <b>محصولات</b>\n\n"
                "فعلاً محصولی ثبت نشده."
            )

            return


        # ====================================================
        # SETTINGS
        # ====================================================

        if data == "settings":

            bot.answer_callback_query(
                call.id
            )


            if is_admin(
                user_id
            ):

                bot.send_message(

                    chat_id,

                    "⚙️ <b>تنظیمات مدیریت</b>\n\n"

                    "👑 شما ادمین اصلی "
                    "voidchater هستید.\n\n"

                    "برای مدیریت از دستورات "
                    "ادمین استفاده کن."
                )

            else:

                bot.send_message(

                    chat_id,

                    "⚙️ تنظیمات مخصوص ادمین‌هاست."
                )

            return


        # ====================================================
        # ADMIN STATUS
        # ====================================================

        if data == "admin_status":

            bot.answer_callback_query(
                call.id
            )


            if is_admin(
                user_id
            ):

                text = (
                    "👑 <b>وضعیت:</b>\n\n"
                    "شما ادمین اصلی "
                    "voidchater هستید. 😎"
                )

            else:

                text = (
                    "👤 شما ادمین اصلی نیستید."
                )


            bot.send_message(
                chat_id,
                text
            )

            return


        # ====================================================
        # FOZOOL STATUS
        # ====================================================

        if data == "fozool_status":

            bot.answer_callback_query(
                call.id
            )


            group = database[
                "groups"
            ].get(
                str(chat_id)
            )


            if not group:

                text = (
                    "❌ بات هنوز در این گروه فعال نشده."
                )

            else:

                status = (

                    "روشن 😈"

                    if group.get(
                        "fozool",
                        False
                    )

                    else

                    "خاموش 😇"
                )


                text = (
                    "😈 <b>حالت فضول:</b> "
                    + status
                )


            bot.send_message(
                chat_id,
                text
            )

            return


        # ====================================================
        # SERIOUS STATUS
        # ====================================================

        if data == "serious_status":

            bot.answer_callback_query(
                call.id
            )


            group = database[
                "groups"
            ].get(
                str(chat_id)
            )


            if not group:

                text = (
                    "❌ بات هنوز در این گروه فعال نشده."
                )

            else:

                status = (

                    "روشن 🧐"

                    if group.get(
                        "serious",
                        False
                    )

                    else

                    "خاموش 😂"
                )


                text = (
                    "🧐 <b>حالت جدی:</b> "
                    + status
                )


            bot.send_message(
                chat_id,
                text
            )

            return


    except Exception as e:

        print(
            "CALLBACK ERROR:",
            repr(e)
        )


# ============================================================
# BOT ADDED TO GROUP
# ============================================================

@bot.message_handler(
    content_types=[
        "new_chat_members"
    ]
)
def new_member_handler(message):

    try:

        me = bot.get_me()


        for user in message.new_chat_members:

            if user.id == me.id:

                bot.send_message(

                    message.chat.id,

                    "درود 😂🐮\n\n"

                    "من <b>voidchater</b> هستم.\n\n"

                    "برای فعال کردن من در این گروه، "
                    "یک ادمین بنویسه:\n\n"

                    "<code>فعال</code>\n\n"

                    "😎🐮"
                )


    except Exception as e:

        print(
            "NEW MEMBER ERROR:",
            repr(e)
        )


# ============================================================
# STARTUP
# ============================================================

try:

    me = bot.get_me()


    print()
    print("=" * 50)
    print("🐮 voidchater ONLINE")
    print("🤖 Username:", me.username)
    print("🧠 Model:", AI_MODEL)
    print("💾 Database:", DB_FILE)
    print("=" * 50)
    print()


except Exception as e:

    print(
        "BOT CONNECTION ERROR:",
        repr(e)
    )


# ============================================================
# POLLING
# ============================================================

while True:

    try:

        print(
            "🚀 Polling started..."
        )


        bot.infinity_polling(

            skip_pending=True,

            allowed_updates=[
                "message",
                "callback_query"
            ]
        )


    except Exception as e:

        print(
            "POLLING ERROR:",
            repr(e)
        )


        print(
            "⏳ Reconnecting in 5 seconds..."
        )


        time.sleep(5)
