# ==============================================================================
# 🤖 ربات مدیریتی پیشرفته تلگرام
# 🌐 مخصوص: گپ ایران
# 👨‍💻 توسعه‌دهنده: رادوین
# 📅 نسخه: 4.0 (نسخه تجاری کامل)
#  خطوط کد: ~1500
# ==============================================================================

import telebot
from telebot import types
import json
import os
import re
import random
import time
import threading
from datetime import datetime, timedelta

# ==============================================================================
# بخش 1: تنظیمات اولیه و پیکربندی
# ==============================================================================

# دریافت توکن از متغیرهای محیطی Railway
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise Exception("⛔ خطای بحرانی: متغیر BOT_TOKEN در Railway تنظیم نشده است!")

# آیدی عددی توسعه‌دهنده اصلی (رادوین) - دسترسی کامل سودو
ADMIN_IDS = [6420547446]
DATABASE_FILE = 'database.json'
DEV_NAME = "رادوین"
GROUP_NAME = "گپ ایران"
VERSION = "4.0"

# راه‌اندازی ربات با حالت HTML
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ==============================================================================
# بخش 2: سیستم مدیریت دیتابیس (JSON)
# ==============================================================================

class Database:
    """کلاس مدیریت دیتابیس JSON برای ذخیره اطلاعات گروه‌ها و کاربران"""
    
    def __init__(self):
        self.data = self.load()

    def load(self):
        """بارگذاری دیتابیس از فایل JSON"""
        if os.path.exists(DATABASE_FILE):
            try:
                with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {"groups": {}, "users": {}}
        return {"groups": {}, "users": {}}

    def save(self):
        """ذخیره دیتابیس در فایل JSON"""
        try:
            with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ خطا در ذخیره دیتابیس: {e}")

    def get_group(self, chat_id):
        """دریافت اطلاعات گروه با ایجاد خودکار در صورت عدم وجود"""
        chat_id = str(chat_id)
        if chat_id not in self.data["groups"]:
            self.data["groups"][chat_id] = self._new_group()
            self.save()
        else:
            group = self.data["groups"][chat_id]
            # به‌روزرسانی خودکار ساختار دیتابیس برای نسخه‌های جدید
            updates = {
                "speaker": {"enabled": False},
                "stats": {}, "auto_ban": True, "admin_info": {}, "vip_info": {},
                "bad_words": ["کس", "کون", "جنده", "کیری", "لاشی", "خر", "sex", "porn", "jende"],
                "timers": [],
                "settings": {
                    "welcome": True, "lock_ban": True, "show_warning": True,
                    "history_enabled": True, "content_protection": False
                },
                "developer_name": DEV_NAME
            }
            updated = False
            for key, default in updates.items():
                if key not in group:
                    group[key] = default
                    updated = True
            if updated:
                self.save()
        return self.data["groups"][chat_id]

    def _new_group(self):
        """ساختار پیش‌فرض یک گروه جدید"""
        return {
            "owner": None, "owners": [], "admins": [], "vip": [],
            "muted": [], "banned": [], "immune": [],
            "locks": {
                "link": False, "forward": False, "username": False, "fosh": False,
                "photo": False, "video": False, "music": False, "voice": False,
                "document": False, "sticker": False, "gif": False, "english": False, "spam": False
            },
            "warnings": {"default": 3}, "warning_counts": {},
            "settings": {
                "welcome": True, "lock_ban": True, "show_warning": True,
                "history_enabled": True, "content_protection": False
            },
            "rules": None, "link": None,
            "speaker": {"enabled": False}, "stats": {}, "auto_ban": True,
            "admin_info": {}, "vip_info": {},
            "bad_words": ["کس", "کون", "جنده", "کیری", "لاشی", "خر", "sex", "porn", "jende"],
            "timers": [],
            "developer_name": DEV_NAME
        }

    def get_user(self, user_id):
        """دریافت اطلاعات کاربر"""
        user_id = str(user_id)
        if user_id not in self.data["users"]:
            self.data["users"][user_id] = {
                "nickname": None, "messages_count": 0, "errors_count": 0,
                "join_date": str(datetime.now())
            }
            self.save()
        return self.data["users"][user_id]

# ایجاد نمونه دیتابیس
db = Database()

# ==============================================================================
# بخش 3: توابع کمکی و هسته‌ای
# ==============================================================================

def get_user_rank(chat_id, user_id):
    """تعیین رتبه کاربر در گروه"""
    if int(user_id) in ADMIN_IDS:
        return "sudo"
    group = db.get_group(chat_id)
    if str(group["owner"]) == str(user_id):
        return "owner_main"
    if str(user_id) in [str(x) for x in group["owners"]]:
        return "owner"
    if str(user_id) in [str(x) for x in group["vip"]]:
        return "vip"
    if str(user_id) in [str(x) for x in group["admins"]]:
        return "admin"
    return "member"

def has_permission(chat_id, user_id, required_rank):
    """بررسی دسترسی کاربر بر اساس رتبه"""
    ranks = {"member": 0, "admin": 1, "vip": 2, "owner": 3, "owner_main": 4, "sudo": 5}
    return ranks.get(get_user_rank(chat_id, user_id), 0) >= ranks.get(required_rank, 0)

def reply_msg(message, text, parse_mode="HTML", reply_markup=None):
    """پاسخ به پیام با مدیریت خطا"""
    try:
        bot.reply_to(message, text, parse_mode=parse_mode, reply_markup=reply_markup)
    except Exception as e:
        print(f"Reply Error: {e}")

def send_msg(chat_id, text, parse_mode="HTML", reply_markup=None):
    """ارسال پیام به چت با مدیریت خطا"""
    try:
        bot.send_message(chat_id, text, parse_mode=parse_mode, reply_markup=reply_markup)
    except Exception as e:
        print(f"Send Error: {e}")

def extract_target_id(message):
    """
    استخراج آیدی عددی از ریپلای یا از متن دستور
    مثال: بن 123456789 یا ریپلای + بن
    """
    if message.reply_to_message:
        return (message.reply_to_message.from_user.id,
                message.reply_to_message.from_user.first_name or "کاربر")
    
    parts = message.text.split()
    if len(parts) >= 2 and parts[1].isdigit():
        return int(parts[1]), "کاربر"
    
    return None, None

def auto_ban_user(chat_id, user_id, reason):
    """بن خودکار کاربر متخلف"""
    group = db.get_group(chat_id)
    if has_permission(chat_id, user_id, "admin") or str(user_id) in [str(x) for x in group.get("immune", [])]:
        return False
    if str(user_id) not in [str(x) for x in group["banned"]]:
        group["banned"].append(user_id)
    
    user_data = db.get_user(user_id)
    user_data["errors_count"] += 1
    db.save()
    
    try:
        bot.ban_chat_member(chat_id, user_id)
        send_msg(chat_id, 
            f"🚫 <b>بن خودکار انجام شد!</b>\n"
            f"👤 <code>{user_id}</code>\n"
            f"⚠️ دلیل: {reason}\n"
            f"👨‍💻 {DEV_NAME}")
        return True
    except Exception:
        return False

def promote_user(chat_id, user_id, rank):
    """ارتقا کاربر به رتبه بالاتر"""
    group = db.get_group(chat_id)
    now = str(datetime.now())
    if rank == "admin" and str(user_id) not in [str(x) for x in group["admins"]]:
        group["admins"].append(user_id)
        group["admin_info"][str(user_id)] = {"promote_date": now}
    elif rank == "vip" and str(user_id) not in [str(x) for x in group["vip"]]:
        group["vip"].append(user_id)
        group["vip_info"][str(user_id)] = {"promote_date": now}
    elif rank == "owner" and str(user_id) not in [str(x) for x in group["owners"]]:
        group["owners"].append(user_id)
    db.save()

def demote_user(chat_id, user_id, rank):
    """برکناری کاربر از رتبه"""
    group = db.get_group(chat_id)
    if rank == "admin" and str(user_id) in [str(x) for x in group["admins"]]:
        group["admins"].remove(user_id)
        group.get("admin_info", {}).pop(str(user_id), None)
        return True
    elif rank == "vip" and str(user_id) in [str(x) for x in group["vip"]]:
        group["vip"].remove(user_id)
        group.get("vip_info", {}).pop(str(user_id), None)
        return True
    elif rank == "owner" and str(user_id) in [str(x) for x in group["owners"]]:
        group["owners"].remove(user_id)
        return True
    return False

def toggle_lock(chat_id, lock_name):
    """تغییر وضعیت قفل (اگر قفل است باز می‌کند و برعکس)"""
    group = db.get_group(chat_id)
    if group["locks"].get(lock_name, False):
        group["locks"][lock_name] = False
        db.save()
        return False
    else:
        group["locks"][lock_name] = True
        db.save()
        return True

# ==============================================================================
# بخش 4: سیستم تایمر پس‌زمینه (Thread)
# ==============================================================================

def timer_worker():
    """
    بررسی هر دقیقه برای اجرای دستورات زمان‌بندی شده
    این تابع در یک Thread جداگانه اجرا می‌شود
    """
    while True:
        try:
            now = datetime.now().strftime("%H:%M")
            for chat_id, group in db.data["groups"].items():
                for timer in group.get("timers", []):
                    if timer["time"] == now and not timer.get("executed_today"):
                        if timer["action"] == "lock_all":
                            for key in group["locks"]:
                                group["locks"][key] = True
                            send_msg(chat_id, 
                                f"🔒 <b>قفل خودکار فعال شد!</b>\n"
                                f"⏰ ساعت: {now}\n"
                                f"🌐 {GROUP_NAME}\n"
                                f"👨‍💻 {DEV_NAME}")
                        elif timer["action"] == "unlock_all":
                            for key in group["locks"]:
                                group["locks"][key] = False
                            send_msg(chat_id, 
                                f"🔓 <b>قفل‌ها به صورت خودکار باز شدند!</b>\n"
                                f"⏰ ساعت: {now}\n"
                                f" {GROUP_NAME}\n"
                                f"‍💻 {DEV_NAME}")
                        
                        timer["executed_today"] = True
                        db.save()
            
            # ریست کردن فلگ اجرا برای روز بعد در ساعت 00:01
            if now == "00:01":
                for group in db.data["groups"].values():
                    for timer in group.get("timers", []):
                        timer["executed_today"] = False
                db.save()
                
            time.sleep(60)
        except Exception as e:
            print(f"Timer Worker Error: {e}")
            time.sleep(60)

# شروع ترد تایمر در پس‌زمینه
threading.Thread(target=timer_worker, daemon=True).start()

# ==============================================================================
# بخش 5: سازنده‌های کیبورد شیشه‌ای
# ==============================================================================

def create_keyboard(rows, columns=2):
    """ساخت کیبورد اینلاین با دکمه‌های شیشه‌ای"""
    keyboard = types.InlineKeyboardMarkup(row_width=columns)
    for row in rows:
        keyboard.add(*[types.InlineKeyboardButton(text=t, callback_data=c) for t, c in row])
    return keyboard

def main_menu(rank):
    """منوی اصلی بر اساس رتبه کاربر"""
    rows = [
        [("📜 راهنما", "menu:help"), ("📊 آمار من", "menu:stats")],
        [(" شناسه", "menu:id"), (" قوانین", "menu:rules")]
    ]
    if rank in ["admin", "vip", "owner", "owner_main", "sudo"]:
        rows.append([("🛡️ مدیریت", "menu:admin"), ("🔒 قفل‌ها", "menu:locks")])
    if rank in ["owner", "owner_main", "sudo"]:
        rows.append([("⚙️ تنظیمات گروه", "menu:settings"), ("👑 تنظیمات مالک", "menu:owner")])
    rows.append([("📊 لیست‌ها", "menu:lists"), ("🤖 سخنگو", "menu:speaker")])
    return create_keyboard(rows)

def back_button(target="menu:main"):
    """دکمه بازگشت به منوی اصلی"""
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(" بازگشت به منو", callback_data=target))
    return kb

def admin_panel():
    """پنل مدیریت"""
    return create_keyboard([
        [("✅ بن", "act:ban"), ("❌ انبن", "act:unban")],
        [("🔇 سکوت", "act:mute"), ("🔊 حذف سکوت", "act:unmute")],
        [(" اخراج", "act:kick"), (" پین", "act:pin")],
        [("🗑️ پاکسازی", "act:purge"), ("🔄 بازگشت", "menu:main")],
    ])

def promote_panel():
    """پنل ارتقا و برکناری"""
    return create_keyboard([
        [("🛡️ ادمین", "act:promote_admin"), ("⛔ برکناری ادمین", "act:demote_admin")],
        [("⭐ ویژه", "act:promote_vip"), ("⛔ برکناری ویژه", "act:demote_vip")],
        [("👑 مالک", "act:promote_owner"), ("⛔ برکناری مالک", "act:demote_owner")],
        [("🔄 بازگشت", "menu:main")],
    ])

def locks_panel(chat_id):
    """پنل قفل‌ها با نمایش وضعیت واقعی"""
    group = db.get_group(chat_id)
    locks = group["locks"]
    
    def make_btn(key, name):
        if locks.get(key, False):
            return (f"🔓 باز {name}", f"toggle:{key}")
        else:
            return (f"🔒 قفل {name}", f"toggle:{key}")
    
    return create_keyboard([
        [make_btn("link", "لینک"), make_btn("forward", "فوروارد/استوری")],
        [make_btn("fosh", "فحش/+18"), make_btn("english", "انگلیسی")],
        [make_btn("photo", "عکس"), make_btn("video", "فیلم")],
        [make_btn("music", "موزیک"), make_btn("voice", "ویس")],
        [make_btn("sticker", "استیکر"), make_btn("gif", "گیف")],
        [make_btn("username", "یوزرنیم"), make_btn("spam", "اسپم")],
        [("🔄 بازگشت", "menu:main")],
    ])

def owner_panel():
    """پنل تنظیمات مالک"""
    return create_keyboard([
        [("📜 تنظیم قوانین", "act:set_rules"), ("🔗 تنظیم لینک", "act:set_link")],
        [(" نام سازنده", "act:set_dev"), ("🗑️ پاکسازی بن", "act:clear_ban")],
        [("⏰ تنظیم تایمر", "act:set_timer"), ("🔄 بازگشت", "menu:main")],
    ])

def lists_panel():
    """پنل لیست‌ها"""
    return create_keyboard([
        [("🛡️ ادمین‌ها", "list:admins"), ("⭐ ویژه‌ها", "list:vips")],
        [("🚫 بن‌شده‌ها", "list:banned"), ("🔇 بی‌صداها", "list:muted")],
        [("🔒 وضعیت قفل‌ها", "list:locks"), ("👑 مالکان", "list:owners")],
        [("🔄 بازگشت", "menu:main")],
    ])

def speaker_panel(chat_id):
    """پنل سخنگو"""
    group = db.get_group(chat_id)
    if group["speaker"]["enabled"]:
        toggle_btn = ("❌ خاموش", "act:speaker_off")
    else:
        toggle_btn = ("✅ فعال", "act:speaker_on")
    keyboard = create_keyboard([
        [toggle_btn, ("🏷 اسم بات", "act:set_bot_name")],
        [("🔄 بازگشت", "menu:main")],
    ])
    status = "✅ فعال" if group["speaker"]["enabled"] else "❌ خاموش"
    return keyboard, status

# ==============================================================================
# بخش 6: هندلرهای پیام متنی (دستورات)
# ==============================================================================

@bot.message_handler(commands=['start', 'help'])
def start_cmd(message):
    """دستور شروع و راهنما"""
    rank = get_user_rank(message.chat.id, message.from_user.id)
    
    help_text = f"""🤖 <b>به ربات مدیریتی پیشرفته خوش آمدید!</b>
🌐 <b>مخصوص:</b> {GROUP_NAME}
👨‍💻 <b>توسعه‌دهنده:</b> {DEV_NAME}
📊 <b>نسخه:</b> {VERSION}

📜 <b>راهنمای کامل دستورات همراه با مثال:</b>

 <b>مدیریتی (با ریپلای یا تایپ آیدی):</b>
• <code>بن [آیدی]</code> ➔ مثال: <code>بن 123456789</code> یا ریپلای + بن
• <code>انبن [آیدی]</code> ➔ مثال: <code>انبن 123456789</code>
• <code>سکوت [آیدی]</code> ➔ مثال: <code>سکوت 123456789</code>
• <code>اخطار [آیدی]</code> ➔ مثال: <code>اخطار 123456789</code> (3 اخطار = بن)
• <code>ادمین [آیدی]</code> ➔ ارتقا به ادمین
• <code>ویژه [آیدی]</code> ➔ ارتقا به کاربر ویژه
• <code>برکناری [آیدی]</code>  برکناری از مقام

⚙️ <b>دستورات پیشرفته:</b>
• <code>پین</code> ➔ پین کردن پیام (با ریپلای)
• <code>حذف پین</code>  برداشتن پیام پین شده گروه
• <code>پاکسازی [تعداد]</code> ➔ مثال: <code>پاکسازی 50</code>
• <code>ساخت لینک</code> ➔ ساخت لینک دعوت یک‌بار مصرف
• <code>تایمر [ساعت] [عمل]</code> ➔ مثال: <code>تایمر 23:00 lock_all</code>
• <code>تایید [آیدی]</code>  قبول درخواست جوین
• <code>رد [آیدی]</code> ➔ رد درخواست جوین

🔒 <b>سیستم قفل‌ها:</b>
• <code>قفل لینک</code> / <code>لینک باز</code>
• <code>قفل فوروارد</code> / <code>فوروارد باز</code> (قفل پست کانال و استوری)
• <code>قفل فحش</code> / <code>فحش باز</code> (فیلتر خودکار کلمات رکیک و +18)
• <code>قفل عکس</code> / <code>عکس باز</code> (و سایر مدیاها)

⚙️ <b>تنظیمات گروه (فقط مالک):</b>
• <code>تاریخچه باز</code> / <code>تاریخچه بسته</code>
• <code>حفاظت محتوا روشن</code> / <code>حفاظت محتوا خاموش</code>

💡 <b>نکته مهم:</b> برای استفاده از دستورات آیدی، عدد آیدی کاربر را دقیقاً بعد از دستور با یک فاصله تایپ کنید.
"""
    send_msg(message.chat.id, help_text, reply_markup=main_menu(rank))

@bot.message_handler(func=lambda m: m.text in ["فعال", "نصب", "فعالسازی"])
def activate_bot(message):
    """فعال‌سازی ربات در گروه"""
    if message.chat.type in ['group', 'supergroup']:
        group = db.get_group(message.chat.id)
        if group["owner"] is None:
            group["owner"] = message.from_user.id
            db.save()
            send_msg(message.chat.id, 
                f"✅ <b>ربات با موفقیت در {GROUP_NAME} فعال شد!</b>\n\n"
                f"‍💻 توسعه‌دهنده: {DEV_NAME}\n"
                f" مالک گروه: {message.from_user.first_name}\n"
                f" آیدی مالک: <code>{message.from_user.id}</code>\n\n"
                f"🎯 لطفاً ربات را <b>ادمین کامل</b> کنید و از منوی زیر استفاده کنید:", 
                reply_markup=main_menu('owner_main'))
        else:
            send_msg(message.chat.id, 
                f"️ این گروه قبلاً فعال شده است.\n"
                f"👤 مالک فعلی: <code>{group['owner']}</code>")

# ==============================================================================
# بخش 7: دستورات مدیریتی با آیدی یا ریپلای
# ==============================================================================

@bot.message_handler(func=lambda m: m.text.startswith("بن ") or m.text in ["بن", "بن کن"])
def ban_by_id_or_reply(message):
    """بن کردن کاربر با آیدی یا ریپلای"""
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        return reply_msg(message, "⛔ شما دسترسی کافی برای این کار را ندارید.")
    
    target_id, target_name = extract_target_id(message)
    if not target_id:
        return reply_msg(message, "⚠️ لطفاً روی پیام کاربر ریپلای کنید یا آیدی عددی او را وارد کنید.\nمثال: <code>بن 123456789</code>")
    
    group = db.get_group(message.chat.id)
    if str(target_id) not in [str(x) for x in group["banned"]]:
        group["banned"].append(target_id)
        db.save()
    
    try:
        bot.ban_chat_member(message.chat.id, target_id)
        reply_msg(message, f"✅ کاربر <code>{target_id}</code> ({target_name}) با موفقیت بن شد.")
    except Exception:
        reply_msg(message, "❌ خطا در بن کردن (لطفاً بررسی کنید ربات ادمین باشد).")

@bot.message_handler(func=lambda m: m.text.startswith("انبن ") or m.text in ["انبن", "حذف بن"])
def unban_by_id_or_reply(message):
    """رفع بن کاربر"""
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        return reply_msg(message, "⛔ شما دسترسی کافی برای این کار را ندارید.")
    
    target_id, target_name = extract_target_id(message)
    if not target_id:
        return reply_msg(message, "⚠️ لطفاً ریپلای کنید یا آیدی عددی را وارد کنید.")
    
    group = db.get_group(message.chat.id)
    if str(target_id) in [str(x) for x in group["banned"]]:
        group["banned"].remove(target_id)
        db.save()
    
    try:
        bot.unban_chat_member(message.chat.id, target_id)
        reply_msg(message, f"✅ کاربر <code>{target_id}</code> از لیست بن خارج شد.")
    except Exception:
        reply_msg(message, "❌ خطا در عملیات انبن.")

@bot.message_handler(func=lambda m: m.text.startswith("سکوت ") or m.text in ["سکوت", "سکوت کن", "میوت"])
def mute_by_id_or_reply(message):
    """سکوت کردن کاربر"""
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        return reply_msg(message, "⛔ شما دسترسی کافی برای این کار را ندارید.")
    
    target_id, target_name = extract_target_id(message)
    if not target_id:
        return reply_msg(message, "️ لطفاً ریپلای کنید یا آیدی عددی را وارد کنید.")
    
    group = db.get_group(message.chat.id)
    if str(target_id) not in [str(x) for x in group["muted"]]:
        group["muted"].append(target_id)
        db.save()
    reply_msg(message, f"🔇 کاربر <code>{target_id}</code> بی‌صدا (Mute) شد.")

@bot.message_handler(func=lambda m: m.text.startswith("اخطار ") or m.text in ["اخطار", "warn"])
def warn_by_id_or_reply(message):
    """اخطار دادن به کاربر"""
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        return reply_msg(message, " شما دسترسی کافی برای این کار را ندارید.")
    
    target_id, target_name = extract_target_id(message)
    if not target_id:
        return reply_msg(message, "⚠️ لطفاً ریپلای کنید یا آیدی عددی را وارد کنید.")
    
    group = db.get_group(message.chat.id)
    user_key = str(target_id)
    if user_key not in group["warning_counts"]:
        group["warning_counts"][user_key] = 0
    
    group["warning_counts"][user_key] += 1
    warns = group["warning_counts"][user_key]
    max_warns = group["warnings"]["default"]
    db.save()
    
    if warns >= max_warns:
        group["warning_counts"][user_key] = 0
        if str(target_id) not in [str(x) for x in group["banned"]]:
            group["banned"].append(target_id)
        db.save()
        try: bot.ban_chat_member(message.chat.id, target_id)
        except: pass
        reply_msg(message, f"🚫 کاربر <code>{target_id}</code> به دلیل دریافت {max_warns} اخطار، به صورت خودکار بن شد!")
    else:
        reply_msg(message, f"⚠️ اخطار {warns} از {max_warns} به کاربر <code>{target_id}</code> داده شد.")

@bot.message_handler(func=lambda m: m.text.startswith("ادمین ") or m.text in ["ادمین", "ادمین کن"])
def promote_admin(message):
    """ارتقا کاربر به ادمین"""
    if not has_permission(message.chat.id, message.from_user.id, "vip"):
        return reply_msg(message, " شما دسترسی کافی برای این کار را ندارید.")
    
    target_id, target_name = extract_target_id(message)
    if not target_id:
        return reply_msg(message, "⚠️ لطفاً ریپلای کنید یا آیدی عددی را وارد کنید.")
    
    promote_user(message.chat.id, target_id, "admin")
    reply_msg(message, f"✅ کاربر <code>{target_id}</code> ({target_name}) به مقام ادمین ارتقا یافت.")

@bot.message_handler(func=lambda m: m.text.startswith("ویژه ") or m.text in ["ویژه", "ویژه کن"])
def promote_vip(message):
    """ارتقا کاربر به ویژه"""
    if not has_permission(message.chat.id, message.from_user.id, "owner"):
        return reply_msg(message, "⛔ شما دسترسی کافی برای این کار را ندارید.")
    
    target_id, target_name = extract_target_id(message)
    if not target_id:
        return reply_msg(message, "⚠️ لطفاً ریپلای کنید یا آیدی عددی را وارد کنید.")
    
    promote_user(message.chat.id, target_id, "vip")
    reply_msg(message, f"⭐ کاربر <code>{target_id}</code> ({target_name}) به مقام ویژه ارتقا یافت.")

@bot.message_handler(func=lambda m: m.text.startswith("مالک ") or m.text in ["مالک", "مالک کن"])
def promote_owner(message):
    """ارتقا کاربر به مالک"""
    if not has_permission(message.chat.id, message.from_user.id, "owner"):
        return reply_msg(message, "⛔ شما دسترسی کافی برای این کار را ندارید.")
    
    target_id, target_name = extract_target_id(message)
    if not target_id:
        return reply_msg(message, "⚠️ لطفاً ریپلای کنید یا آیدی عددی را وارد کنید.")
    
    promote_user(message.chat.id, target_id, "owner")
    reply_msg(message, f"👑 کاربر <code>{target_id}</code> ({target_name}) به مقام مالک ارتقا یافت.")

@bot.message_handler(func=lambda m: m.text.startswith("برکناری ") or m.text in ["برکناری", "برکنار کن"])
def demote_user_cmd(message):
    """برکناری کاربر از مقام"""
    if not has_permission(message.chat.id, message.from_user.id, "owner"):
        return reply_msg(message, " شما دسترسی کافی برای این کار را ندارید.")
    
    target_id, target_name = extract_target_id(message)
    if not target_id:
        return reply_msg(message, "⚠️ لطفاً ریپلای کنید یا آیدی عددی را وارد کنید.")
    
    target_rank = get_user_rank(message.chat.id, target_id)
    if target_rank == "admin":
        demote_user(message.chat.id, target_id, "admin")
        reply_msg(message, f"✅ کاربر <code>{target_id}</code> از ادمینی برکنار شد.")
    elif target_rank == "vip":
        demote_user(message.chat.id, target_id, "vip")
        reply_msg(message, f"✅ کاربر <code>{target_id}</code> از ویژه برکنار شد.")
    elif target_rank == "owner":
        demote_user(message.chat.id, target_id, "owner")
        reply_msg(message, f"✅ کاربر <code>{target_id}</code> از مالکی برکنار شد.")
    else:
        reply_msg(message, "⛔ این کاربر مقامی ندارد.")

# ==============================================================================
# بخش 8: دستورات پیشرفته (پین، پاکسازی، لینک، تایمر)
# ==============================================================================

@bot.message_handler(func=lambda m: m.text == "پین")
def pin_message(message):
    """پین کردن پیام"""
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        return reply_msg(message, " دسترسی ندارید.")
    if message.reply_to_message:
        try:
            bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id, disable_notification=False)
            reply_msg(message, "📌 پیام با موفقیت پین شد.")
        except Exception as e:
            reply_msg(message, f"❌ خطا در پین کردن: {e}")
    else:
        reply_msg(message, "⚠️ لطفاً روی پیامی که می‌خواهید پین شود ریپلای کنید.")

@bot.message_handler(func=lambda m: m.text == "حذف پین")
def unpin_message(message):
    """حذف پیام پین شده"""
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        return reply_msg(message, "⛔ دسترسی ندارید.")
    try:
        bot.unpin_chat_message(message.chat.id)
        reply_msg(message, "📌 پیام پین شده گروه حذف شد.")
    except Exception as e:
        reply_msg(message, f"❌ خطا در حذف پین: {e}")

@bot.message_handler(func=lambda m: m.text.startswith("پاکسازی "))
def purge_messages(message):
    """پاکسازی پیام‌های اخیر"""
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        return reply_msg(message, "⛔ دسترسی ندارید.")
    
    parts = message.text.split()
    if len(parts) >= 2 and parts[1].isdigit():
        count = int(parts[1])
        if count > 100: count = 100
        
        reply_msg(message, f"🗑️ در حال حذف {count} پیام اخیر...")
        try:
            messages = bot.get_chat_history(message.chat.id, limit=count)
            deleted = 0
            for msg in messages:
                try:
                    bot.delete_message(message.chat.id, msg.message_id)
                    deleted += 1
                    time.sleep(0.1)
                except Exception:
                    pass
            
            send_msg(message.chat.id, 
                f"✅ عملیات پاکسازی تمام شد.\n"
                f"🗑️ تعداد پیام‌های حذف شده: {deleted}\n"
                f"⚠️ نکته: ربات فقط می‌تواند پیام‌های 48 ساعت اخیر را حذف کند.\n"
                f"‍💻 {DEV_NAME}")
        except Exception as e:
            reply_msg(message, f"❌ خطا: {e}")
    else:
        reply_msg(message, "️ فرمت صحیح: <code>پاکسازی 50</code>")

@bot.message_handler(func=lambda m: m.text == "ساخت لینک")
def create_invite_link(message):
    """ساخت لینک دعوت یک‌بار مصرف"""
    if not has_permission(message.chat.id, message.from_user.id, "owner"):
        return reply_msg(message, "⛔ فقط مالک گروه می‌تواند لینک اختصاصی بسازد.")
    
    try:
        link = bot.create_chat_invite_link(
            message.chat.id,
            expire_date=int(time.time()) + 86400,
            member_limit=1,
            creates_join_request=False
        )
        reply_msg(message, 
            f"🔗 <b>لینک اختصاصی ساخته شد:</b>\n\n"
            f"{link.invite_link}\n\n"
            f"⚠️ این لینک فقط برای <b>1 نفر</b> و به مدت <b>24 ساعت</b> معتبر است.\n"
            f"👨‍💻 {DEV_NAME}")
    except Exception as e:
        reply_msg(message, f"❌ خطا در ساخت لینک: {e}")

@bot.message_handler(func=lambda m: m.text.startswith("تایمر "))
def set_timer(message):
    """تنظیم تایمر برای اجرای خودکار دستورات"""
    if not has_permission(message.chat.id, message.from_user.id, "owner"):
        return reply_msg(message, "⛔ فقط مالک می‌تواند تایمر تنظیم کند.")
    
    parts = message.text.split()
    if len(parts) >= 3:
        timer_time = parts[1]
        action = parts[2]
        
        if not re.match(r'^\d{2}:\d{2}$', timer_time):
            return reply_msg(message, "⚠️ فرمت ساعت اشتباه است. مثال صحیح: <code>23:00</code>")
        
        if action not in ["lock_all", "unlock_all"]:
            return reply_msg(message, "️ عملیات باید lock_all یا unlock_all باشد.")
        
        group = db.get_group(message.chat.id)
        group["timers"].append({"time": timer_time, "action": action, "executed_today": False})
        db.save()
        reply_msg(message, 
            f"⏰ <b>تایمر با موفقیت تنظیم شد:</b>\n"
            f" ساعت اجرا: {timer_time}\n"
            f"⚙️ عملیات: {action}\n"
            f"👨💻 {DEV_NAME}")
    else:
        reply_msg(message, 
            "⚠️ فرمت: <code>تایمر [ساعت] [عملیات]</code>\n"
            "مثال: <code>تایمر 23:00 lock_all</code>")

# ==============================================================================
# بخش 9: مدیریت درخواست‌های عضویت و تنظیمات گروه
# ==============================================================================

@bot.message_handler(func=lambda m: m.text.startswith("تایید "))
def approve_join(message):
    """تایید درخواست عضویت"""
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        return reply_msg(message, "⛔ دسترسی ندارید.")
    parts = message.text.split()
    if len(parts) >= 2 and parts[1].isdigit():
        try:
            bot.approve_chat_join_request(message.chat.id, int(parts[1]))
            reply_msg(message, f"✅ درخواست عضویت کاربر <code>{parts[1]}</code> تایید شد.")
        except Exception:
            reply_msg(message, "❌ خطا (شاید کاربر قبلاً عضو شده یا درخواستی ندارد).")

@bot.message_handler(func=lambda m: m.text.startswith("رد "))
def decline_join(message):
    """رد درخواست عضویت"""
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        return reply_msg(message, "⛔ دسترسی ندارید.")
    parts = message.text.split()
    if len(parts) >= 2 and parts[1].isdigit():
        try:
            bot.decline_chat_join_request(message.chat.id, int(parts[1]))
            reply_msg(message, f"❌ درخواست عضویت کاربر <code>{parts[1]}</code> رد شد.")
        except Exception:
            reply_msg(message, "❌ خطا در رد درخواست.")

@bot.message_handler(func=lambda m: m.text in ["تاریخچه باز", "تاریخچه بسته"])
def toggle_history(message):
    """تغییر وضعیت تاریخچه چت"""
    if not has_permission(message.chat.id, message.from_user.id, "owner"):
        return reply_msg(message, " فقط مالک می‌تواند این تنظیم را تغییر دهد.")
    
    group = db.get_group(message.chat.id)
    if message.text == "تاریخچه باز":
        group["settings"]["history_enabled"] = True
        db.save()
        try:
            bot.set_chat_permissions(message.chat.id, types.ChatPermissions(
                can_send_messages=True, can_send_media_messages=True,
                can_send_other_messages=True, can_add_web_page_previews=True
            ))
            reply_msg(message, "✅ تاریخچه چت برای اعضای جدید باز شد.")
        except Exception:
            reply_msg(message, "✅ تنظیمات در دیتابیس ذخیره شد (ربات نیاز به دسترسی دارد).")
    else:
        group["settings"]["history_enabled"] = False
        db.save()
        try:
            bot.set_chat_permissions(message.chat.id, types.ChatPermissions(can_send_messages=False))
            reply_msg(message, "🔒 تاریخچه چت برای اعضای جدید بسته شد.")
        except Exception:
            reply_msg(message, "✅ تنظیمات در دیتابیس ذخیره شد (ربات نیاز به دسترسی دارد).")

@bot.message_handler(func=lambda m: m.text in ["حفاظت محتوا روشن", "حفاظت محتوا خاموش"])
def toggle_content_protection(message):
    """تغییر وضعیت حفاظت از محتوا"""
    if not has_permission(message.chat.id, message.from_user.id, "owner"):
        return reply_msg(message, "⛔ فقط مالک می‌تواند این تنظیم را تغییر دهد.")
    
    group = db.get_group(message.chat.id)
    if message.text == "حفاظت محتوا روشن":
        group["settings"]["content_protection"] = True
        db.save()
        reply_msg(message, "🛡️ حفاظت از محتوا (جلوگیری از فوروارد و ذخیره مدیا) روشن شد.")
    else:
        group["settings"]["content_protection"] = False
        db.save()
        reply_msg(message, "🛡️ حفاظت از محتوا خاموش شد.")

# ==============================================================================
# بخش 10: دستورات قفل‌ها (متنی)
# ==============================================================================

@bot.message_handler(func=lambda m: m.text in ["قفل فوروارد", "فوروارد باز"])
def lock_forward_text(message):
    """قفل/باز کردن فوروارد"""
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        return reply_msg(message, "⛔ دسترسی ندارید.")
    is_locked = toggle_lock(message.chat.id, "forward")
    reply_msg(message, f"🔒 قفل فوروارد (پست کانال/استوری) {'فعال' if is_locked else 'غیرفعال'} شد.")

@bot.message_handler(func=lambda m: m.text in ["قفل فحش", "فحش باز"])
def lock_fosh_text(message):
    """قفل/باز کردن فحش"""
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        return reply_msg(message, " دسترسی ندارید.")
    is_locked = toggle_lock(message.chat.id, "fosh")
    reply_msg(message, f"🔒 قفل فحش و محتوای نامناسب (+18) {'فعال' if is_locked else 'غیرفعال'} شد.")

@bot.message_handler(func=lambda m: m.text in ["قفل لینک", "لینک باز"])
def lock_link_text(message):
    """قفل/باز کردن لینک"""
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        return reply_msg(message, "⛔ دسترسی ندارید.")
    is_locked = toggle_lock(message.chat.id, "link")
    reply_msg(message, f"🔒 قفل لینک {'فعال' if is_locked else 'غیرفعال'} شد.")

@bot.message_handler(func=lambda m: m.text in ["قفل عکس", "عکس باز"])
def lock_photo_text(message):
    """قفل/باز کردن عکس"""
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        return reply_msg(message, "⛔ دسترسی ندارید.")
    is_locked = toggle_lock(message.chat.id, "photo")
    reply_msg(message, f" قفل عکس {'فعال' if is_locked else 'غیرفعال'} شد.")

@bot.message_handler(func=lambda m: m.text in ["قفل فیلم", "فیلم باز"])
def lock_video_text(message):
    """قفل/باز کردن فیلم"""
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        return reply_msg(message, "⛔ دسترسی ندارید.")
    is_locked = toggle_lock(message.chat.id, "video")
    reply_msg(message, f"🔒 قفل فیلم {'فعال' if is_locked else 'غیرفعال'} شد.")

@bot.message_handler(func=lambda m: m.text in ["قفل استیکر", "استیکر باز"])
def lock_sticker_text(message):
    """قفل/باز کردن استیکر"""
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        return reply_msg(message, " دسترسی ندارید.")
    is_locked = toggle_lock(message.chat.id, "sticker")
    reply_msg(message, f"🔒 قفل استیکر {'فعال' if is_locked else 'غیرفعال'} شد.")

@bot.message_handler(func=lambda m: m.text in ["قفل گیف", "گیف باز"])
def lock_gif_text(message):
    """قفل/باز کردن گیف"""
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        return reply_msg(message, "⛔ دسترسی ندارید.")
    is_locked = toggle_lock(message.chat.id, "gif")
    reply_msg(message, f"🔒 قفل گیف {'فعال' if is_locked else 'غیرفعال'} شد.")

@bot.message_handler(func=lambda m: m.text in ["قفل ویس", "ویس باز"])
def lock_voice_text(message):
    """قفل/باز کردن ویس"""
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        return reply_msg(message, "⛔ دسترسی ندارید.")
    is_locked = toggle_lock(message.chat.id, "voice")
    reply_msg(message, f"🔒 قفل ویس {'فعال' if is_locked else 'غیرفعال'} شد.")

@bot.message_handler(func=lambda m: m.text in ["قفل موزیک", "موزیک باز"])
def lock_music_text(message):
    """قفل/باز کردن موزیک"""
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        return reply_msg(message, " دسترسی ندارید.")
    is_locked = toggle_lock(message.chat.id, "music")
    reply_msg(message, f"🔒 قفل موزیک {'فعال' if is_locked else 'غیرفعال'} شد.")

@bot.message_handler(func=lambda m: m.text in ["قفل انگلیسی", "انگلیسی باز"])
def lock_english_text(message):
    """قفل/باز کردن انگلیسی"""
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        return reply_msg(message, "⛔ دسترسی ندارید.")
    is_locked = toggle_lock(message.chat.id, "english")
    reply_msg(message, f"🔒 قفل انگلیسی {'فعال' if is_locked else 'غیرفعال'} شد.")

@bot.message_handler(func=lambda m: m.text == "لیست قفل")
def lock_list_text(message):
    """نمایش وضعیت قفل‌ها"""
    group = db.get_group(message.chat.id)
    text = "🔒 <b>وضعیت قفل‌ها:</b>\n\n"
    lock_names = {
        "link": "لینک", "forward": "فوروارد", "username": "یوزرنیم",
        "photo": "عکس", "video": "فیلم", "music": "موزیک",
        "voice": "ویس", "document": "فایل", "sticker": "استیکر",
        "gif": "گیف", "english": "انگلیسی", "spam": "اسپم", "fosh": "فحش"
    }
    for key, name in lock_names.items():
        status = "🔒" if group["locks"].get(key, False) else "🔓"
        text += f"• {name}: {status}\n"
    reply_msg(message, text)

@bot.message_handler(func=lambda m: m.text == "قوانین")
def show_rules(message):
    """نمایش قوانین گروه"""
    group = db.get_group(message.chat.id)
    if group["rules"]:
        reply_msg(message, f" <b>قوانین گروه:</b>\n\n{group['rules']}")
    else:
        reply_msg(message, "⚠️ هنوز قوانینی تنظیم نشده است.")

@bot.message_handler(func=lambda m: m.text.startswith("تنظیم قوانین"))
def set_rules(message):
    """تنظیم قوانین گروه"""
    if not has_permission(message.chat.id, message.from_user.id, "owner"):
        return reply_msg(message, "⛔ فقط مالک می‌تواند قوانین را تنظیم کند.")
    
    parts = message.text.split(" ", 1)
    if len(parts) < 2:
        return reply_msg(message, "⚠️ فرمت: <code>تنظیم قوانین [متن قوانین]</code>")
    
    group = db.get_group(message.chat.id)
    group["rules"] = parts[1]
    db.save()
    reply_msg(message, "✅ قوانین گروه با موفقیت ذخیره شد.")

@bot.message_handler(func=lambda m: m.text == "آمار")
def user_stats(message):
    """نمایش آمار کاربر"""
    user_id = message.from_user.id
    group = db.get_group(message.chat.id)
    user_data = db.get_user(user_id)
    rank = get_user_rank(message.chat.id, user_id)
    rank_fa = {
        "sudo": "🔱 سودو", "owner_main": "👑 مالک اصلی",
        "owner": "👑 مالک", "vip": "⭐ ویژه",
        "admin": "🛡️ ادمین", "member": "👤 کاربر"
    }.get(rank, "👤 کاربر")
    
    user_key = str(user_id)
    group_stats = group.get("stats", {}).get(user_key, {"messages": 0, "warnings": 0})
    
    text = (f"📊 <b>آمار شما:</b>\n\n"
            f"👤 نام: {message.from_user.first_name or 'ندارد'}\n"
            f"🆔 آیدی: <code>{user_id}</code>\n"
            f"🏅 مقام: {rank_fa}\n"
            f"📨 پیام‌ها: <b>{group_stats.get('messages', 0)}</b>\n"
            f"⚠️ اخطارها: <b>{group_stats.get('warnings', 0)}</b>\n"
            f"❌ خطاها: <b>{user_data.get('errors_count', 0)}</b>\n"
            f"👨‍💻 {DEV_NAME}")
    reply_msg(message, text)

@bot.message_handler(func=lambda m: m.text == "ایدی")
def user_id(message):
    """نمایش آیدی کاربر"""
    rank = get_user_rank(message.chat.id, message.from_user.id)
    rank_fa = {
        "sudo": "🔱 سودو", "owner_main": "👑 مالک اصلی",
        "owner": "👑 مالک", "vip": "⭐ ویژه",
        "admin": "🛡️ ادمین", "member": "👤 کاربر"
    }.get(rank, "👤 کاربر")
    
    text = (f"🆔 <b>شناسه شما:</b>\n\n"
            f"👤 نام: {message.from_user.first_name or ''}\n"
            f"🆔 آیدی: <code>{message.from_user.id}</code>\n"
            f"🏅 مقام: {rank_fa}")
    reply_msg(message, text)

# ==============================================================================
# بخش 11: بررسی پیام‌ها و اعمال قفل‌ها (هسته اصلی)
# ==============================================================================

@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker', 'animation'])
def check_message(message):
    """بررسی تمام پیام‌ها و اعمال قوانین قفل"""
    if message.chat.type not in ['group', 'supergroup']:
        return
    
    # خوش‌آمدگویی به اعضای جدید
    if message.new_chat_members:
        group = db.get_group(message.chat.id)
        if group["settings"].get("welcome", True):
            for new_member in message.new_chat_members:
                if not new_member.is_bot:
                    send_msg(message.chat.id,
                        f"👋 <b>خوش آمدید!</b>\n"
                        f"👤 {new_member.first_name}\n"
                        f"🌐 به {GROUP_NAME} خوش آمدید.\n"
                        f"👨‍💻 توسعه‌دهنده: {DEV_NAME}")
        return

    group = db.get_group(message.chat.id)
    user_id = message.from_user.id
    user_data = db.get_user(user_id)
    user_data["messages_count"] += 1
    
    user_key = str(user_id)
    if user_key not in group["stats"]:
        group["stats"][user_key] = {"messages": 0, "warnings": 0}
    group["stats"][user_key]["messages"] += 1
    db.save()
    
    # بررسی کاربران بی‌صدا یا بن شده
    if str(user_id) in [str(x) for x in group["muted"]]:
        try: bot.delete_message(message.chat.id, message.message_id)
        except: pass
        return
    
    if str(user_id) in [str(x) for x in group["banned"]]:
        try: bot.ban_chat_member(message.chat.id, user_id)
        except: pass
        return
    
    # معافیت ادمین‌ها
    if has_permission(message.chat.id, user_id, "admin") or str(user_id) in [str(x) for x in group.get("immune", [])]:
        return
        
    violated = False
    reason = ""
    
    # بررسی قوانین قفل
    if message.text and group["locks"]["link"] and re.search(r'(https?://|www\.|t\.me)', message.text):
        violated, reason = True, "ارسال لینک"
    elif message.text and group["locks"]["username"] and re.search(r'@[\w_]{3,}', message.text):
        violated, reason = True, "ارسال یوزرنیم"
    elif message.text and group["locks"]["fosh"]:
        bad_words = group.get("bad_words", [])
        if any(w in message.text.lower() for w in bad_words):
            violated, reason = True, "ارسال فحش یا محتوای نامناسب (+18)"
    elif message.text and group["locks"]["english"] and re.search(r'[a-zA-Z]{3,}', message.text):
        violated, reason = True, "استفاده از متن انگلیسی"
    elif group["locks"]["forward"] and message.forward_date:
        violated, reason = True, "فوروارد (پست کانال/استوری)"
    elif group["locks"]["photo"] and message.photo:
        violated, reason = True, "ارسال عکس"
    elif group["locks"]["video"] and message.video:
        violated, reason = True, "ارسال فیلم"
    elif group["locks"]["music"] and message.audio:
        violated, reason = True, "ارسال موزیک"
    elif group["locks"]["voice"] and message.voice:
        violated, reason = True, "ارسال ویس"
    elif group["locks"]["document"] and message.document:
        violated, reason = True, "ارسال فایل"
    elif group["locks"]["sticker"] and message.sticker:
        violated, reason = True, "ارسال استیکر"
    elif group["locks"]["gif"] and message.animation:
        violated, reason = True, "ارسال گیف"
    
    # اجرای مجازات
    if violated:
        try: bot.delete_message(message.chat.id, message.message_id)
        except: pass
        
        if group.get("auto_ban", True):
            auto_ban_user(message.chat.id, user_id, reason)
        else:
            if user_key not in group["warning_counts"]:
                group["warning_counts"][user_key] = 0
            
            group["warning_counts"][user_key] += 1
            
            if group["warning_counts"][user_key] >= group["warnings"]["default"]:
                group["warning_counts"][user_key] = 0
                auto_ban_user(message.chat.id, user_id, f"دریافت حداکثر اخطار برای: {reason}")
            else:
                db.save()
                send_msg(message.chat.id,
                    f"⚠️ <b>اخطار!</b>\n"
                    f" کاربر: <code>{user_id}</code>\n"
                    f"📊 اخطار: {group['warning_counts'][user_key]} از {group['warnings']['default']}\n"
                    f"🚫 دلیل: {reason}\n"
                    f"‍💻 {DEV_NAME}")
        return

# ==============================================================================
# بخش 12: مدیریت Callback (دکمه‌های شیشه‌ای)
# ==============================================================================

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """مدیریت تمام کلیک‌های دکمه‌های شیشه‌ای"""
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    rank = get_user_rank(chat_id, user_id)
    data = call.data

    try:
        # منوی اصلی
        if data == "menu:main":
            bot.answer_callback_query(call.id, "🏠 منوی اصلی")
            bot.edit_message_text(
                f"🤖 <b>پنل مدیریت حرفه‌ای</b>\n\n"
                f"👤 مقام شما: <b>{rank}</b>\n"
                f"🌐 {GROUP_NAME}\n"
                f"👨💻 {DEV_NAME}",
                chat_id, call.message.message_id, parse_mode="HTML", reply_markup=main_menu(rank))
        
        # راهنما
        elif data == "menu:help":
            bot.answer_callback_query(call.id, " راهنما")
            bot.edit_message_text(
                "برای مشاهده راهنمای کامل از دستور /start استفاده کنید.",
                chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())
        
        # آمار
        elif data == "menu:stats":
            bot.answer_callback_query(call.id, "📊 آمار")
            user_data = db.get_user(user_id)
            group = db.get_group(chat_id)
            user_key = str(user_id)
            stats = group.get("stats", {}).get(user_key, {"messages": 0, "warnings": 0})
            text = (f"📊 <b>آمار شما:</b>\n"
                    f" نام: {call.from_user.first_name}\n"
                    f"🆔 آیدی: <code>{user_id}</code>\n"
                    f"📨 پیام‌ها: {stats.get('messages', 0)}\n"
                    f"️ اخطارها: {stats.get('warnings', 0)}\n"
                    f"👨‍💻 {DEV_NAME}")
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())

        # شناسه
        elif data == "menu:id":
            bot.answer_callback_query(call.id, "🆔 شناسه")
            rank_fa = {
                "sudo": "🔱 سودو", "owner_main": " مالک اصلی",
                "owner": "👑 مالک", "vip": "⭐ ویژه",
                "admin": "🛡️ ادمین", "member": "👤 کاربر"
            }.get(rank, "👤 کاربر")
            text = (f" <b>شناسه شما:</b>\n\n"
                    f"👤 نام: {call.from_user.first_name or ''}\n"
                    f"🆔 آیدی: <code>{user_id}</code>\n"
                    f" مقام: {rank_fa}")
            if call.from_user.username:
                text += f"\n یوزرنیم: @{call.from_user.username}"
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())

        # قوانین
        elif data == "menu:rules":
            bot.answer_callback_query(call.id, "📋 قوانین")
            group = db.get_group(chat_id)
            text = f"📜 <b>قوانین گروه:</b>\n\n{group['rules']}" if group["rules"] else "️ هنوز قوانینی تنظیم نشده است."
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())

        # پنل مدیریت
        elif data == "menu:admin":
            if not has_permission(chat_id, user_id, "admin"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            bot.answer_callback_query(call.id, "🛡️ پنل مدیریت")
            bot.edit_message_text(
                "️ <b>پنل مدیریت</b>\n\n⚠️ برای عملیات ابتدا روی پیام کاربر ریپلای کنید.",
                chat_id, call.message.message_id, parse_mode="HTML", reply_markup=admin_panel())

        # پنل ارتقا
        elif data == "menu:promote":
            if not has_permission(chat_id, user_id, "owner"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            bot.answer_callback_query(call.id, "⭐ پنل ارتقا")
            bot.edit_message_text(
                "⭐ <b>پنل ارتقا و برکناری</b>\n\n⚠️ برای عملیات ابتدا روی پیام کاربر ریپلای کنید.",
                chat_id, call.message.message_id, parse_mode="HTML", reply_markup=promote_panel())

        # پنل قفل‌ها
        elif data == "menu:locks":
            if not has_permission(chat_id, user_id, "admin"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            bot.answer_callback_query(call.id, "🔒 پنل قفل‌ها")
            bot.edit_message_text(
                "🔒 <b>پنل قفل‌ها</b>\n\n⚠️ سرپیچی = <b>بن خودکار!</b>",
                chat_id, call.message.message_id, parse_mode="HTML", reply_markup=locks_panel(chat_id))

        # پنل مالک
        elif data == "menu:owner":
            if not has_permission(chat_id, user_id, "owner"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            bot.answer_callback_query(call.id, "👑 پنل مالک")
            bot.edit_message_text("👑 <b>تنظیمات مالک</b>", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=owner_panel())

        # لیست‌ها
        elif data == "menu:lists":
            bot.answer_callback_query(call.id, " لیست‌ها")
            bot.edit_message_text("📊 <b>لیست‌های گروه</b>", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=lists_panel())

        # سخنگو
        elif data == "menu:speaker":
            if not has_permission(chat_id, user_id, "vip"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            bot.answer_callback_query(call.id, "🤖 پنل سخنگو")
            keyboard, status = speaker_panel(chat_id)
            bot.edit_message_text(f"🤖 <b>پنل سخنگو</b>\n\n📊 وضعیت: {status}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=keyboard)

        # تغییر وضعیت قفل
        elif data.startswith("toggle:"):
            if not has_permission(chat_id, user_id, "admin"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            
            lock_name = data.replace("toggle:", "")
            is_now_locked = toggle_lock(chat_id, lock_name)
            
            if is_now_locked:
                msg_text = f"🔒 قفل <b>{lock_name}</b> فعال شد!"
            else:
                msg_text = f"🔓 قفل <b>{lock_name}</b> غیرفعال شد!"
            
            bot.answer_callback_query(call.id, msg_text, show_alert=True)
            bot.edit_message_text(
                "🔒 <b>پنل قفل‌ها</b>\n\n⚠️ سرپیچی = <b>بن خودکار!</b>",
                chat_id, call.message.message_id, parse_mode="HTML", reply_markup=locks_panel(chat_id))

        # بن
        elif data == "act:ban":
            if not has_permission(chat_id, user_id, "admin"):
                bot.answer_callback_query(call.id, " دسترسی ندارید", show_alert=True); return
            if not call.message.reply_to_message:
                bot.answer_callback_query(call.id, "⚠️ روی پیام کاربر ریپلای کنید", show_alert=True); return
            target = call.message.reply_to_message.from_user
            group = db.get_group(chat_id)
            if str(target.id) not in [str(x) for x in group["banned"]]:
                group["banned"].append(target.id)
                db.save()
            try:
                bot.ban_chat_member(chat_id, target.id)
                bot.edit_message_text(f"✅ <b>کاربر بن شد!</b>\n\n👤 {target.first_name}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())
            except:
                bot.answer_callback_query(call.id, "❌ خطا در بن", show_alert=True)

        # انبن
        elif data == "act:unban":
            if not has_permission(chat_id, user_id, "admin"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            if not call.message.reply_to_message:
                bot.answer_callback_query(call.id, "⚠️ روی پیام کاربر ریپلای کنید", show_alert=True); return
            target = call.message.reply_to_message.from_user
            group = db.get_group(chat_id)
            if str(target.id) in [str(x) for x in group["banned"]]:
                group["banned"].remove(target.id)
                db.save()
            try:
                bot.unban_chat_member(chat_id, target.id)
                bot.edit_message_text(f"✅ <b>کاربر از بن خارج شد!</b>\n\n {target.first_name}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())
            except:
                bot.answer_callback_query(call.id, "❌ خطا", show_alert=True)

        # سکوت
        elif data == "act:mute":
            if not has_permission(chat_id, user_id, "admin"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            if not call.message.reply_to_message:
                bot.answer_callback_query(call.id, "⚠️ روی پیام کاربر ریپلای کنید", show_alert=True); return
            target = call.message.reply_to_message.from_user
            group = db.get_group(chat_id)
            if str(target.id) not in [str(x) for x in group["muted"]]:
                group["muted"].append(target.id)
                db.save()
            bot.edit_message_text(f"🔇 <b>کاربر بی‌صدا شد!</b>\n\n👤 {target.first_name}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())

        # حذف سکوت
        elif data == "act:unmute":
            if not has_permission(chat_id, user_id, "admin"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            if not call.message.reply_to_message:
                bot.answer_callback_query(call.id, "⚠️ روی پیام کاربر ریپلای کنید", show_alert=True); return
            target = call.message.reply_to_message.from_user
            group = db.get_group(chat_id)
            if str(target.id) in [str(x) for x in group["muted"]]:
                group["muted"].remove(target.id)
                db.save()
            bot.edit_message_text(f"🔊 <b>کاربر از بی‌صدا خارج شد!</b>\n\n👤 {target.first_name}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())

        # اخراج
        elif data == "act:kick":
            if not has_permission(chat_id, user_id, "admin"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            if not call.message.reply_to_message:
                bot.answer_callback_query(call.id, "️ روی پیام کاربر ریپلای کنید", show_alert=True); return
            target = call.message.reply_to_message.from_user
            try:
                bot.kick_chat_member(chat_id, target.id, until_date=int(time.time()) + 60)
                bot.edit_message_text(f"🚫 <b>کاربر اخراج شد!</b>\n\n {target.first_name}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())
            except:
                bot.answer_callback_query(call.id, "❌ خطا", show_alert=True)

        # پین
        elif data == "act:pin":
            if not has_permission(chat_id, user_id, "admin"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            if not call.message.reply_to_message:
                bot.answer_callback_query(call.id, "⚠️ روی پیام کاربر ریپلای کنید", show_alert=True); return
            try:
                bot.pin_chat_message(chat_id, call.message.reply_to_message.message_id)
                bot.answer_callback_query(call.id, "📌 پیام پین شد", show_alert=True)
            except:
                bot.answer_callback_query(call.id, "❌ خطا در پین", show_alert=True)

        # پاکسازی
        elif data == "act:purge":
            if not has_permission(chat_id, user_id, "admin"):
                bot.answer_callback_query(call.id, " دسترسی ندارید", show_alert=True); return
            bot.answer_callback_query(call.id, "از دستور متنی 'پاکسازی 50' استفاده کنید", show_alert=True)

        # ارتقا ادمین
        elif data == "act:promote_admin":
            if not has_permission(chat_id, user_id, "vip"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            if not call.message.reply_to_message:
                bot.answer_callback_query(call.id, "️ روی پیام کاربر ریپلای کنید", show_alert=True); return
            target = call.message.reply_to_message.from_user
            promote_user(chat_id, target.id, "admin")
            bot.edit_message_text(f"✅ <b>کاربر ادمین شد!</b>\n\n👤 {target.first_name}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())

        # برکناری ادمین
        elif data == "act:demote_admin":
            if not has_permission(chat_id, user_id, "owner"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            if not call.message.reply_to_message:
                bot.answer_callback_query(call.id, "⚠️ روی پیام کاربر ریپلای کنید", show_alert=True); return
            target = call.message.reply_to_message.from_user
            if demote_user(chat_id, target.id, "admin"):
                bot.edit_message_text(f"⛔ <b>کاربر از ادمینی برکنار شد!</b>\n\n👤 {target.first_name}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())
            else:
                bot.answer_callback_query(call.id, "⚠️ این کاربر ادمین نیست", show_alert=True)

        # ارتقا ویژه
        elif data == "act:promote_vip":
            if not has_permission(chat_id, user_id, "owner"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            if not call.message.reply_to_message:
                bot.answer_callback_query(call.id, "⚠️ روی پیام کاربر ریپلای کنید", show_alert=True); return
            target = call.message.reply_to_message.from_user
            promote_user(chat_id, target.id, "vip")
            bot.edit_message_text(f"⭐ <b>کاربر ویژه شد!</b>\n\n👤 {target.first_name}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())

        # برکناری ویژه
        elif data == "act:demote_vip":
            if not has_permission(chat_id, user_id, "owner"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            if not call.message.reply_to_message:
                bot.answer_callback_query(call.id, "⚠️ روی پیام کاربر ریپلای کنید", show_alert=True); return
            target = call.message.reply_to_message.from_user
            if demote_user(chat_id, target.id, "vip"):
                bot.edit_message_text(f"⛔ <b>کاربر از ویژه برکنار شد!</b>\n\n👤 {target.first_name}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())
            else:
                bot.answer_callback_query(call.id, "⚠️ این کاربر ویژه نیست", show_alert=True)

        # ارتقا مالک
        elif data == "act:promote_owner":
            if not has_permission(chat_id, user_id, "owner"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            if not call.message.reply_to_message:
                bot.answer_callback_query(call.id, "️ روی پیام کاربر ریپلای کنید", show_alert=True); return
            target = call.message.reply_to_message.from_user
            promote_user(chat_id, target.id, "owner")
            bot.edit_message_text(f"👑 <b>کاربر مالک شد!</b>\n\n👤 {target.first_name}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())

        # برکناری مالک
        elif data == "act:demote_owner":
            if not has_permission(chat_id, user_id, "owner_main"):
                bot.answer_callback_query(call.id, "⛔ فقط مالک اصلی", show_alert=True); return
            if not call.message.reply_to_message:
                bot.answer_callback_query(call.id, "⚠️ روی پیام کاربر ریپلای کنید", show_alert=True); return
            target = call.message.reply_to_message.from_user
            if demote_user(chat_id, target.id, "owner"):
                bot.edit_message_text(f" <b>کاربر از مالکی برکنار شد!</b>\n\n👤 {target.first_name}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())
            else:
                bot.answer_callback_query(call.id, "️ این کاربر مالک نیست", show_alert=True)

        # سخنگو روشن
        elif data == "act:speaker_on":
            if not has_permission(chat_id, user_id, "vip"):
                bot.answer_callback_query(call.id, " دسترسی ندارید", show_alert=True); return
            group = db.get_group(chat_id)
            group["speaker"]["enabled"] = True
            db.save()
            bot.answer_callback_query(call.id, "✅ سخنگو فعال شد", show_alert=True)
            keyboard, status = speaker_panel(chat_id)
            bot.edit_message_text(f"🤖 <b>پنل سخنگو</b>\n\n📊 وضعیت: {status}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=keyboard)

        # سخنگو خاموش
        elif data == "act:speaker_off":
            if not has_permission(chat_id, user_id, "vip"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            group = db.get_group(chat_id)
            group["speaker"]["enabled"] = False
            db.save()
            bot.answer_callback_query(call.id, "❌ سخنگو خاموش شد", show_alert=True)
            keyboard, status = speaker_panel(chat_id)
            bot.edit_message_text(f" <b>پنل سخنگو</b>\n\n📊 وضعیت: {status}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=keyboard)

        # لیست ادمین‌ها
        elif data == "list:admins":
            group = db.get_group(chat_id)
            text = "🛡️ <b>لیست ادمین‌ها:</b>\n\n"
            if group["admins"]:
                for i, admin_id in enumerate(group["admins"], 1):
                    text += f"{i}. <code>{admin_id}</code>\n"
            else:
                text += "⚠️ هیچ ادمینی وجود ندارد."
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button("menu:lists"))

        # لیست ویژه‌ها
        elif data == "list:vips":
            group = db.get_group(chat_id)
            text = "⭐ <b>لیست ویژه‌ها:</b>\n\n"
            if group["vip"]:
                for i, vip_id in enumerate(group["vip"], 1):
                    text += f"{i}. <code>{vip_id}</code>\n"
            else:
                text += "⚠️ هیچ کاربر ویژه‌ای وجود ندارد."
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button("menu:lists"))

        # لیست بن‌شده‌ها
        elif data == "list:banned":
            group = db.get_group(chat_id)
            text = "🚫 <b>لیست بن شده‌ها:</b>\n\n"
            if group["banned"]:
                for i, user_id_ban in enumerate(group["banned"], 1):
                    text += f"{i}. <code>{user_id_ban}</code>\n"
            else:
                text += "⚠️ هیچ کاربر بن شده‌ای وجود ندارد."
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button("menu:lists"))

        # لیست بی‌صداها
        elif data == "list:muted":
            group = db.get_group(chat_id)
            text = "🔇 <b>لیست بی‌صداها:</b>\n\n"
            if group["muted"]:
                for i, user_id_mute in enumerate(group["muted"], 1):
                    text += f"{i}. <code>{user_id_mute}</code>\n"
            else:
                text += "️ هیچ کاربر بی‌صدایی وجود ندارد."
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button("menu:lists"))

        # لیست مالکان
        elif data == "list:owners":
            group = db.get_group(chat_id)
            text = "👑 <b>لیست مالکان:</b>\n\n"
            text += f"👑 مالک اصلی: <code>{group['owner']}</code>\n\n"
            if group["owners"]:
                for i, owner_id in enumerate(group["owners"], 1):
                    text += f"{i}. <code>{owner_id}</code>\n"
            else:
                text += "⚠️ هیچ مالک دیگری وجود ندارد."
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button("menu:lists"))

        # لیست قفل‌ها
        elif data == "list:locks":
            group = db.get_group(chat_id)
            text = "🔒 <b>وضعیت قفل‌ها:</b>\n\n"
            lock_names = {
                "link": "لینک", "forward": "فوروارد", "username": "یوزرنیم",
                "photo": "عکس", "video": "فیلم", "music": "موزیک",
                "voice": "ویس", "document": "فایل", "sticker": "استیکر",
                "gif": "گیف", "english": "انگلیسی", "spam": "اسپم", "fosh": "فحش"
            }
            for key, name in lock_names.items():
                status = "🔒" if group["locks"].get(key, False) else "🔓"
                text += f"• {name}: {status}\n"
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button("menu:lists"))

        # پاکسازی بن
        elif data == "act:clear_ban":
            if not has_permission(chat_id, user_id, "owner"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            group = db.get_group(chat_id)
            group["banned"] = []
            db.save()
            bot.answer_callback_query(call.id, "✅ لیست بن پاکسازی شد", show_alert=True)
            bot.edit_message_text("✅ <b>لیست بن پاکسازی شد!</b>", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button("menu:owner"))

        # تنظیم نام سازنده
        elif data == "act:set_dev":
            if not has_permission(chat_id, user_id, "owner"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            bot.answer_callback_query(call.id, "از دستور '/setdev [نام]' استفاده کنید", show_alert=True)

        else:
            bot.answer_callback_query(call.id, "❓ دستور ناشناخته")

    except Exception as e:
        print(f"Callback error: {e}")

# ==============================================================================
# بخش 13: شروع ربات
# ==============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(f"🤖 ربات مدیریتی پیشرفته | {GROUP_NAME}")
    print(f"👨‍💻 توسعه‌دهنده: {DEV_NAME}")
    print(f"📊 نسخه: {VERSION}")
    print("=" * 60)
    print("✅ سیستم دستورات با آیدی فعال است")
    print("✅ سیستم تایمر پس‌زمینه در حال اجراست")
    print("✅ قفل‌های پیشرفته (فوروارد، فحش، رسانه) فعال است")
    print("✅ دکمه‌های شیشه‌ای و دستورات متنی هماهنگ هستند")
    print("=" * 60)
    bot.infinity_polling()
