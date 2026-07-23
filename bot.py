import telebot
from telebot import types
import json
import os
import re
import random
import time
from datetime import datetime

# ==================== تنظیمات اولیه ====================
TOKEN = '8519619369:AAEn08PiN-umkJqCyFpa-Re7860ct5wDbTg'
ADMIN_IDS = [6420547446]
DATABASE_FILE = 'database.json'

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ==================== لیست پاسخ‌های سخنگو ====================
SPEAKER_NAMES = ["باتی", "بات کچولو", "عزیزم", "ربات جان", "رفیق", "دوست من"]
SPEAKER_RESPONSES = {
    "سلام": ["سلام عزیزم! 😍", "به به! سلام رفیق 🌹"],
    "خوبی": ["ممنون عزیزم، تو خوبی؟ 😊", "عالی‌ام! 💫"],
    "چطوری": ["من خوبم، تو چطوری؟ 😊", "عالی‌ام! 💫"],
    "ممنون": ["خواهش می‌کنم 🌹", "قابلی نداره 💖"],
    "بای": ["خداحافظ عزیزم! 👋", "به امید دیدار 💖"],
    "default": ["جانم عزیزم؟ 😊", "بگو رفیق! 💫", "در خدمتم 🌹"]
}

# ==================== سیستم دیتابیس ====================
class Database:
    def __init__(self):
        self.data = self.load()

    def load(self):
        if os.path.exists(DATABASE_FILE):
            try:
                with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"groups": {}, "users": {}}
        return {"groups": {}, "users": {}}

    def save(self):
        with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def get_group(self, chat_id):
        chat_id = str(chat_id)
        if chat_id not in self.data["groups"]:
            self.data["groups"][chat_id] = self._new_group()
            self.save()
        else:
            group = self.data["groups"][chat_id]
            updates = {
                "speaker": {"enabled": False},
                "user_bot_names": {},
                "stats": {},
                "auto_ban": True,
                "admin_info": {},
                "vip_info": {},
                "bad_words": ["کس", "کون", "جنده", "کیری", "لاشی", "خر"]
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
        return {
            "owner": None, "owners": [], "admins": [], "vip": [],
            "muted": [], "banned": [], "immune": [], "kill_list": [],
            "locks": {
                "link": False, "forward": False, "username": False,
                "fosh": False, "gif": False, "photo": False, "video": False,
                "music": False, "voice": False, "document": False,
                "sticker": False, "english": False, "spam": False
            },
            "warnings": {"default": 5},
            "warning_counts": {},
            "settings": {"lock_ban": True, "show_warning": True, "welcome": True},
            "rules": None, "link": None,
            "speaker": {"enabled": False},
            "user_bot_names": {}, "stats": {}, "auto_ban": True,
            "admin_info": {}, "vip_info": {},
            "bad_words": ["کس", "کون", "جنده", "کیری", "لاشی", "خر"]
        }

    def get_user(self, user_id):
        user_id = str(user_id)
        if user_id not in self.data["users"]:
            self.data["users"][user_id] = {
                "nickname": None,
                "messages_count": 0, "errors_count": 0
            }
            self.save()
        return self.data["users"][user_id]

db = Database()

# ==================== توابع کمکی ====================
def get_user_rank(chat_id, user_id):
    if user_id in ADMIN_IDS:
        return "sudo"
    group = db.get_group(chat_id)
    if group["owner"] == user_id:
        return "owner_main"
    if user_id in group["owners"]:
        return "owner"
    if user_id in group["vip"]:
        return "vip"
    if user_id in group["admins"]:
        return "admin"
    return "member"

def has_permission(chat_id, user_id, required_rank):
    ranks = {"member": 0, "admin": 1, "vip": 2, "owner": 3, "owner_main": 4, "sudo": 5}
    return ranks.get(get_user_rank(chat_id, user_id), 0) >= ranks.get(required_rank, 0)

def reply_msg(message, text, parse_mode="HTML", reply_markup=None):
    try:
        bot.reply_to(message, text, parse_mode=parse_mode, reply_markup=reply_markup)
    except Exception as e:
        print(f"Error: {e}")

def send_msg(chat_id, text, parse_mode="HTML", reply_markup=None):
    try:
        bot.send_message(chat_id, text, parse_mode=parse_mode, reply_markup=reply_markup)
    except Exception as e:
        print(f"Error: {e}")

def promote_user(chat_id, user_id, rank):
    group = db.get_group(chat_id)
    now = str(datetime.now())
    if rank == "admin" and user_id not in group["admins"]:
        group["admins"].append(user_id)
        group["admin_info"][str(user_id)] = {"promote_date": now}
    elif rank == "vip" and user_id not in group["vip"]:
        group["vip"].append(user_id)
        group["vip_info"][str(user_id)] = {"promote_date": now}
    elif rank == "owner" and user_id not in group["owners"]:
        group["owners"].append(user_id)
    db.save()

def demote_user(chat_id, user_id, rank):
    group = db.get_group(chat_id)
    if rank == "admin" and user_id in group["admins"]:
        group["admins"].remove(user_id)
        group.get("admin_info", {}).pop(str(user_id), None)
        return True
    elif rank == "vip" and user_id in group["vip"]:
        group["vip"].remove(user_id)
        group.get("vip_info", {}).pop(str(user_id), None)
        return True
    elif rank == "owner" and user_id in group["owners"]:
        group["owners"].remove(user_id)
        return True
    return False

def auto_ban_user(chat_id, user_id, reason):
    group = db.get_group(chat_id)
    if has_permission(chat_id, user_id, "admin") or user_id in group.get("immune", []):
        return False
    if user_id not in group["banned"]:
        group["banned"].append(user_id)
    user_data = db.get_user(user_id)
    user_data["errors_count"] += 1
    db.save()
    try:
        bot.ban_chat_member(chat_id, user_id)
        send_msg(chat_id, f"🚫 <b>بن خودکار!</b>\n\n👤 <code>{user_id}</code>\n⚠️ {reason}")
        return True
    except:
        return False

# ==================== تابع تغییر وضعیت قفل ====================
def toggle_lock(chat_id, lock_name):
    """تغییر وضعیت قفل - اگر قفل است باز می‌کند، اگر باز است قفل می‌کند"""
    group = db.get_group(chat_id)
    
    # اگر قفل فعال است، غیرفعال کن
    if group["locks"].get(lock_name, False):
        group["locks"][lock_name] = False
        db.save()
        return False  # یعنی الان باز شد
    # اگر قفل غیرفعال است، فعال کن
    else:
        group["locks"][lock_name] = True
        db.save()
        return True  # یعنی الان قفل شد

# ==================== ساخت دکمه‌های شیشه‌ای ====================
def create_keyboard(rows, columns=2):
    keyboard = types.InlineKeyboardMarkup(row_width=columns)
    for row in rows:
        buttons = []
        for text, callback in row:
            buttons.append(types.InlineKeyboardButton(text=text, callback_data=callback))
        keyboard.add(*buttons)
    return keyboard

def main_menu(rank):
    rows = [
        [("📜 راهنما", "menu:help"), ("📊 آمار من", "menu:stats")],
        [("🆔 شناسه", "menu:id"), ("📋 قوانین", "menu:rules")],
    ]
    if rank in ["admin", "vip", "owner", "owner_main", "sudo"]:
        rows.append([("🛡️ پنل مدیریت", "menu:admin"), ("🔒 پنل قفل‌ها", "menu:locks")])
    if rank in ["owner", "owner_main", "sudo"]:
        rows.append([("⭐ پنل ارتقا", "menu:promote"), ("👑 پنل مالک", "menu:owner")])
    rows.append([("📊 لیست‌ها", "menu:lists"), ("🤖 سخنگو", "menu:speaker")])
    return create_keyboard(rows)

def admin_panel():
    return create_keyboard([
        [("✅ بن کاربر", "act:ban"), ("❌ انبن کاربر", "act:unban")],
        [("🔇 سکوت کاربر", "act:mute"), ("🔊 حذف سکوت", "act:unmute")],
        [("🚫 اخراج کاربر", "act:kick"), ("🔄 بازگشت", "menu:main")],
    ])

def promote_panel():
    return create_keyboard([
        [("🛡️ ادمین کن", "act:promote_admin"), ("⛔ برکناری ادمین", "act:demote_admin")],
        [("⭐ ویژه کن", "act:promote_vip"), ("⛔ برکناری ویژه", "act:demote_vip")],
        [("👑 مالک کن", "act:promote_owner"), ("⛔ برکناری مالک", "act:demote_owner")],
        [("🔄 بازگشت", "menu:main")],
    ])

def locks_panel(chat_id):
    """ساخت پنل قفل‌ها با نمایش وضعیت واقعی"""
    group = db.get_group(chat_id)
    locks = group["locks"]
    
    # تابع کمکی برای ساخت دکمه قفل
    def make_lock_button(lock_key, lock_name):
        # چک کردن وضعیت واقعی از دیتابیس
        is_locked = locks.get(lock_key, False)
        
        if is_locked:
            # اگر قفل است، دکمه "باز کردن" نمایش بده
            return (f"🔓 باز کردن {lock_name}", f"toggle:{lock_key}")
        else:
            # اگر باز است، دکمه "قفل کردن" نمایش بده
            return (f"🔒 قفل {lock_name}", f"toggle:{lock_key}")
    
    return create_keyboard([
        [make_lock_button("link", "لینک"), make_lock_button("forward", "فوروارد")],
        [make_lock_button("username", "یوزرنیم"), make_lock_button("fosh", "فحش")],
        [make_lock_button("photo", "عکس"), make_lock_button("video", "فیلم")],
        [make_lock_button("music", "موزیک"), make_lock_button("voice", "ویس")],
        [make_lock_button("sticker", "استیکر"), make_lock_button("gif", "گیف")],
        [make_lock_button("english", "انگلیسی"), make_lock_button("spam", "اسپم")],
        [("🔄 بازگشت", "menu:main")],
    ])

def owner_panel():
    return create_keyboard([
        [("✏️ تنظیم نام گروه", "act:set_title"), ("📜 تنظیم قوانین", "act:set_rules")],
        [("🗑️ پاکسازی لیست بن", "act:clear_ban"), ("🗑️ پاکسازی لیست ادمین", "act:clear_admin")],
        [("🔄 بازگشت", "menu:main")],
    ])

def lists_panel():
    return create_keyboard([
        [("🛡️ لیست ادمین", "list:admins"), ("⭐ لیست ویژه", "list:vips")],
        [("🚫 لیست بن", "list:banned"), ("🔇 لیست سکوت", "list:muted")],
        [("🔒 لیست قفل", "list:locks"), ("👑 لیست مالک", "list:owners")],
        [("🔄 بازگشت", "menu:main")],
    ])

def speaker_panel(chat_id):
    group = db.get_group(chat_id)
    if group["speaker"]["enabled"]:
        toggle_btn = ("❌ خاموش کردن", "act:speaker_off")
    else:
        toggle_btn = ("✅ فعال کردن", "act:speaker_on")
    keyboard = create_keyboard([
        [toggle_btn, ("🏷 تنظیم اسم بات", "act:set_bot_name")],
        [("🔄 بازگشت", "menu:main")],
    ])
    status = "✅ فعال" if group["speaker"]["enabled"] else "❌ خاموش"
    return keyboard, status

def back_button(target="menu:main"):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data=target))
    return keyboard

# ==================== Callback Handler (دکمه‌های شیشه‌ای) ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    rank = get_user_rank(chat_id, user_id)
    data = call.data

    try:
        # ========== منوها ==========
        if data == "menu:main":
            bot.answer_callback_query(call.id, "🏠 منوی اصلی")
            bot.edit_message_text(
                f"🤖 <b>منوی اصلی ربات</b>\n\n👤 مقام شما: <b>{rank}</b>\n\nدستور مورد نظر را انتخاب کنید:",
                chat_id, call.message.message_id, parse_mode="HTML", reply_markup=main_menu(rank))

        elif data == "menu:help":
            bot.answer_callback_query(call.id, "📜 راهنما")
            text = get_commands_text(rank)
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())

        elif data == "menu:stats":
            bot.answer_callback_query(call.id, "📊 آمار")
            text = get_stats_text(chat_id, user_id, call.from_user)
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())

        elif data == "menu:id":
            bot.answer_callback_query(call.id, "🆔 شناسه")
            rank_fa = {"sudo": "🔱 سودو", "owner_main": "👑 مالک اصلی", "owner": "👑 مالک", "vip": "⭐ ویژه", "admin": "🛡️ ادمین", "member": "👤 کاربر"}.get(rank, "👤 کاربر")
            text = f"🆔 <b>شناسه شما:</b>\n\n👤 نام: {call.from_user.first_name or ''}\n🆔 آیدی: <code>{user_id}</code>\n🏅 مقام: {rank_fa}"
            if call.from_user.username: text += f"\n🔗 یوزرنیم: @{call.from_user.username}"
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())

        elif data == "menu:rules":
            bot.answer_callback_query(call.id, "📋 قوانین")
            group = db.get_group(chat_id)
            text = f"📜 <b>قوانین گروه:</b>\n\n{group['rules']}" if group["rules"] else "⚠️ هنوز قوانینی تنظیم نشده است."
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())

        elif data == "menu:admin":
            if not has_permission(chat_id, user_id, "admin"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            bot.answer_callback_query(call.id, "🛡️ پنل مدیریت")
            bot.edit_message_text("🛡️ <b>پنل مدیریت</b>\n\n⚠️ برای عملیات ابتدا روی پیام کاربر ریپلای کنید.", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=admin_panel())

        elif data == "menu:promote":
            if not has_permission(chat_id, user_id, "owner"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            bot.answer_callback_query(call.id, "⭐ پنل ارتقا")
            bot.edit_message_text("⭐ <b>پنل ارتقا و برکناری</b>\n\n⚠️ برای عملیات ابتدا روی پیام کاربر ریپلای کنید.", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=promote_panel())

        elif data == "menu:locks":
            if not has_permission(chat_id, user_id, "admin"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            bot.answer_callback_query(call.id, "🔒 پنل قفل‌ها")
            bot.edit_message_text("🔒 <b>پنل قفل‌ها</b>\n\n⚠️ سرپیچی = <b>بن خودکار!</b>", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=locks_panel(chat_id))

        elif data == "menu:owner":
            if not has_permission(chat_id, user_id, "owner"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            bot.answer_callback_query(call.id, "👑 پنل مالک")
            bot.edit_message_text("👑 <b>پنل مالک</b>", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=owner_panel())

        elif data == "menu:lists":
            bot.answer_callback_query(call.id, "📊 لیست‌ها")
            bot.edit_message_text("📊 <b>لیست‌های گروه</b>", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=lists_panel())

        elif data == "menu:speaker":
            if not has_permission(chat_id, user_id, "vip"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            bot.answer_callback_query(call.id, "🤖 پنل سخنگو")
            keyboard, status = speaker_panel(chat_id)
            bot.edit_message_text(f"🤖 <b>پنل سخنگو</b>\n\n📊 وضعیت: {status}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=keyboard)

        # ========== تغییر وضعیت قفل (مهم‌ترین بخش) ==========
        elif data.startswith("toggle:"):
            if not has_permission(chat_id, user_id, "admin"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            
            # استخراج نام قفل
            lock_name = data.replace("toggle:", "")
            
            # تغییر وضعیت قفل
            is_now_locked = toggle_lock(chat_id, lock_name)
            
            # نمایش پیام مناسب
            if is_now_locked:
                msg_text = f"🔒 قفل <b>{lock_name}</b> فعال شد!"
            else:
                msg_text = f"🔓 قفل <b>{lock_name}</b> غیرفعال شد!"
            
            bot.answer_callback_query(call.id, msg_text, show_alert=True)
            
            # رفرش کردن پنل قفل‌ها با وضعیت جدید
            bot.edit_message_text("🔒 <b>پنل قفل‌ها</b>\n\n⚠️ سرپیچی = <b>بن خودکار!</b>", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=locks_panel(chat_id))

        # ========== عملیات مدیریتی ==========
        elif data == "act:ban":
            if not has_permission(chat_id, user_id, "admin"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            if not call.message.reply_to_message:
                bot.answer_callback_query(call.id, "⚠️ روی پیام کاربر ریپلای کنید", show_alert=True); return
            target = call.message.reply_to_message.from_user
            group = db.get_group(chat_id)
            if target.id not in group["banned"]: group["banned"].append(target.id); db.save()
            try:
                bot.ban_chat_member(chat_id, target.id)
                bot.edit_message_text(f"✅ <b>کاربر بن شد!</b>\n\n👤 {target.first_name}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())
            except: bot.answer_callback_query(call.id, "❌ خطا در بن", show_alert=True)

        elif data == "act:unban":
            if not has_permission(chat_id, user_id, "admin"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            if not call.message.reply_to_message:
                bot.answer_callback_query(call.id, "⚠️ روی پیام کاربر ریپلای کنید", show_alert=True); return
            target = call.message.reply_to_message.from_user
            group = db.get_group(chat_id)
            if target.id in group["banned"]: group["banned"].remove(target.id); db.save()
            try:
                bot.unban_chat_member(chat_id, target.id)
                bot.edit_message_text(f"✅ <b>کاربر از بن خارج شد!</b>\n\n👤 {target.first_name}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())
            except: bot.answer_callback_query(call.id, "❌ خطا", show_alert=True)

        elif data == "act:mute":
            if not has_permission(chat_id, user_id, "admin"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            if not call.message.reply_to_message:
                bot.answer_callback_query(call.id, "⚠️ روی پیام کاربر ریپلای کنید", show_alert=True); return
            target = call.message.reply_to_message.from_user
            group = db.get_group(chat_id)
            if target.id not in group["muted"]: group["muted"].append(target.id); db.save()
            bot.edit_message_text(f"🔇 <b>کاربر بی‌صدا شد!</b>\n\n👤 {target.first_name}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())

        elif data == "act:unmute":
            if not has_permission(chat_id, user_id, "admin"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            if not call.message.reply_to_message:
                bot.answer_callback_query(call.id, "⚠️ روی پیام کاربر ریپلای کنید", show_alert=True); return
            target = call.message.reply_to_message.from_user
            group = db.get_group(chat_id)
            if target.id in group["muted"]: group["muted"].remove(target.id); db.save()
            bot.edit_message_text(f"🔊 <b>کاربر از بی‌صدا خارج شد!</b>\n\n👤 {target.first_name}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())

        elif data == "act:kick":
            if not has_permission(chat_id, user_id, "admin"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            if not call.message.reply_to_message:
                bot.answer_callback_query(call.id, "⚠️ روی پیام کاربر ریپلای کنید", show_alert=True); return
            target = call.message.reply_to_message.from_user
            try:
                bot.kick_chat_member(chat_id, target.id, until_date=int(time.time()) + 60)
                bot.edit_message_text(f"🚫 <b>کاربر اخراج شد!</b>\n\n👤 {target.first_name}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())
            except: bot.answer_callback_query(call.id, "❌ خطا", show_alert=True)

        elif data == "act:promote_admin":
            if not has_permission(chat_id, user_id, "vip"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            if not call.message.reply_to_message:
                bot.answer_callback_query(call.id, "⚠️ روی پیام کاربر ریپلای کنید", show_alert=True); return
            target = call.message.reply_to_message.from_user
            promote_user(chat_id, target.id, "admin")
            bot.edit_message_text(f"✅ <b>کاربر ادمین شد!</b>\n\n👤 {target.first_name}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())

        elif data == "act:demote_admin":
            if not has_permission(chat_id, user_id, "owner"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            if not call.message.reply_to_message:
                bot.answer_callback_query(call.id, "⚠️ روی پیام کاربر ریپلای کنید", show_alert=True); return
            target = call.message.reply_to_message.from_user
            if demote_user(chat_id, target.id, "admin"):
                bot.edit_message_text(f"⛔ <b>کاربر از ادمینی برکنار شد!</b>\n\n👤 {target.first_name}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())
            else: bot.answer_callback_query(call.id, "⚠️ این کاربر ادمین نیست", show_alert=True)

        elif data == "act:promote_vip":
            if not has_permission(chat_id, user_id, "owner"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            if not call.message.reply_to_message:
                bot.answer_callback_query(call.id, "⚠️ روی پیام کاربر ریپلای کنید", show_alert=True); return
            target = call.message.reply_to_message.from_user
            promote_user(chat_id, target.id, "vip")
            bot.edit_message_text(f"⭐ <b>کاربر ویژه شد!</b>\n\n👤 {target.first_name}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())

        elif data == "act:demote_vip":
            if not has_permission(chat_id, user_id, "owner"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            if not call.message.reply_to_message:
                bot.answer_callback_query(call.id, "⚠️ روی پیام کاربر ریپلای کنید", show_alert=True); return
            target = call.message.reply_to_message.from_user
            if demote_user(chat_id, target.id, "vip"):
                bot.edit_message_text(f"⛔ <b>کاربر از ویژه برکنار شد!</b>\n\n👤 {target.first_name}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())
            else: bot.answer_callback_query(call.id, "⚠️ این کاربر ویژه نیست", show_alert=True)

        elif data == "act:promote_owner":
            if not has_permission(chat_id, user_id, "owner"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            if not call.message.reply_to_message:
                bot.answer_callback_query(call.id, "⚠️ روی پیام کاربر ریپلای کنید", show_alert=True); return
            target = call.message.reply_to_message.from_user
            promote_user(chat_id, target.id, "owner")
            bot.edit_message_text(f"👑 <b>کاربر مالک شد!</b>\n\n👤 {target.first_name}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())

        elif data == "act:demote_owner":
            if not has_permission(chat_id, user_id, "owner_main"):
                bot.answer_callback_query(call.id, "⛔ فقط مالک اصلی", show_alert=True); return
            if not call.message.reply_to_message:
                bot.answer_callback_query(call.id, "⚠️ روی پیام کاربر ریپلای کنید", show_alert=True); return
            target = call.message.reply_to_message.from_user
            if demote_user(chat_id, target.id, "owner"):
                bot.edit_message_text(f"⛔ <b>کاربر از مالکی برکنار شد!</b>\n\n👤 {target.first_name}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button())
            else: bot.answer_callback_query(call.id, "⚠️ این کاربر مالک نیست", show_alert=True)

        elif data == "act:speaker_on":
            if not has_permission(chat_id, user_id, "vip"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            group = db.get_group(chat_id)
            group["speaker"]["enabled"] = True; db.save()
            bot.answer_callback_query(call.id, "✅ سخنگو فعال شد", show_alert=True)
            keyboard, status = speaker_panel(chat_id)
            bot.edit_message_text(f"🤖 <b>پنل سخنگو</b>\n\n📊 وضعیت: {status}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=keyboard)

        elif data == "act:speaker_off":
            if not has_permission(chat_id, user_id, "vip"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            group = db.get_group(chat_id)
            group["speaker"]["enabled"] = False; db.save()
            bot.answer_callback_query(call.id, "❌ سخنگو خاموش شد", show_alert=True)
            keyboard, status = speaker_panel(chat_id)
            bot.edit_message_text(f"🤖 <b>پنل سخنگو</b>\n\n📊 وضعیت: {status}", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=keyboard)

        elif data == "list:admins":
            group = db.get_group(chat_id)
            text = "🛡️ <b>لیست ادمین‌ها:</b>\n\n"
            if group["admins"]:
                for i, admin_id in enumerate(group["admins"], 1):
                    admin_data = db.get_user(admin_id)
                    nickname = admin_data.get("nickname") or "بدون لقب"
                    text += f"{i}. <code>{admin_id}</code>\n   💫 {nickname}\n\n"
            else: text += "⚠️ هیچ ادمینی وجود ندارد."
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button("menu:lists"))

        elif data == "list:vips":
            group = db.get_group(chat_id)
            text = "⭐ <b>لیست ویژه‌ها:</b>\n\n"
            if group["vip"]:
                for i, vip_id in enumerate(group["vip"], 1):
                    vip_data = db.get_user(vip_id)
                    nickname = vip_data.get("nickname") or "بدون لقب"
                    text += f"{i}. <code>{vip_id}</code>\n   💫 {nickname}\n\n"
            else: text += "⚠️ هیچ کاربر ویژه‌ای وجود ندارد."
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button("menu:lists"))

        elif data == "list:banned":
            group = db.get_group(chat_id)
            text = "🚫 <b>لیست بن شده‌ها:</b>\n\n"
            if group["banned"]:
                for i, user_id_ban in enumerate(group["banned"], 1): text += f"{i}. <code>{user_id_ban}</code>\n"
            else: text += "⚠️ هیچ کاربر بن شده‌ای وجود ندارد."
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button("menu:lists"))

        elif data == "list:muted":
            group = db.get_group(chat_id)
            text = "🔇 <b>لیست بی‌صداها:</b>\n\n"
            if group["muted"]:
                for i, user_id_mute in enumerate(group["muted"], 1): text += f"{i}. <code>{user_id_mute}</code>\n"
            else: text += "⚠️ هیچ کاربر بی‌صدایی وجود ندارد."
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button("menu:lists"))

        elif data == "list:owners":
            group = db.get_group(chat_id)
            text = "👑 <b>لیست مالکان:</b>\n\n"
            text += f"👑 مالک اصلی: <code>{group['owner']}</code>\n\n"
            if group["owners"]:
                for i, owner_id in enumerate(group["owners"], 1): text += f"{i}. <code>{owner_id}</code>\n"
            else: text += "⚠️ هیچ مالک دیگری وجود ندارد."
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button("menu:lists"))

        elif data == "list:locks":
            group = db.get_group(chat_id)
            text = "🔒 <b>وضعیت قفل‌ها:</b>\n\n"
            lock_names = {"link": "لینک", "forward": "فوروارد", "username": "یوزرنیم", "photo": "عکس", "video": "فیلم", "music": "موزیک", "voice": "ویس", "document": "فایل", "sticker": "استیکر", "gif": "گیف", "english": "انگلیسی", "spam": "اسپم", "fosh": "فحش"}
            for key, name in lock_names.items():
                status = "🔒" if group["locks"].get(key, False) else "🔓"
                text += f"• {name}: {status}\n"
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button("menu:lists"))

        elif data == "act:clear_ban":
            if not has_permission(chat_id, user_id, "owner"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            group = db.get_group(chat_id)
            group["banned"] = []; db.save()
            bot.answer_callback_query(call.id, "✅ لیست بن پاکسازی شد", show_alert=True)
            bot.edit_message_text("✅ <b>لیست بن پاکسازی شد!</b>", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button("menu:owner"))

        elif data == "act:clear_admin":
            if not has_permission(chat_id, user_id, "owner"):
                bot.answer_callback_query(call.id, "⛔ دسترسی ندارید", show_alert=True); return
            group = db.get_group(chat_id)
            group["admins"] = []; group["admin_info"] = {}; db.save()
            bot.answer_callback_query(call.id, "✅ لیست ادمین پاکسازی شد", show_alert=True)
            bot.edit_message_text("✅ <b>لیست ادمین پاکسازی شد!</b>", chat_id, call.message.message_id, parse_mode="HTML", reply_markup=back_button("menu:owner"))

        else:
            bot.answer_callback_query(call.id, "❓ دستور ناشناخته")

    except Exception as e:
        print(f"Callback error: {e}")

# ==================== توابع متن ====================
def get_commands_text(rank):
    text = "📜 <b>راهنمای کامل دستورات</b>\n\n"
    text += "👨‍💻 <b>ساخته شده برای گپ پدرام</b>\n\n"
    text += "👤 <b>عمومی:</b>\n• <code>پنل من</code> - باز شدن منوی شیشه‌ای\n• <code>آمار</code> - آمار شما\n• <code>ایدی</code> - شناسه شما\n• <code>قوانین</code> - قوانین گروه\n• <code>تنظیم لقب [لقب]</code>\n\n"
    if rank in ["admin", "vip", "owner", "owner_main", "sudo"]:
        text += "🛡️ <b>مدیریتی (با ریپلای یا دکمه):</b>\n• <code>بن</code> / <code>انبن</code>\n• <code>سکوت</code> / <code>حذف سکوت</code>\n\n"
    if rank in ["owner", "owner_main", "sudo"]:
        text += "⭐ <b>ارتقا/برکناری (با ریپلای یا دکمه):</b>\n• <code>ادمین</code> / <code>برکناری ادمین</code>\n• <code>ویژه</code> / <code>برکناری ویژه</code>\n• <code>مالک</code> / <code>برکناری مالک</code>\n\n"
    text += "🔒 <b>قفل‌ها:</b>\n• <code>قفل فحش</code> / <code>فحش باز</code>\n• <code>قفل لینک</code> / <code>لینک باز</code>\n"
    text += f"\n💡 <b>نکته:</b> سرپیچی از قفل = بن خودکار!"
    return text

def get_stats_text(chat_id, user_id, user):
    group = db.get_group(chat_id)
    user_data = db.get_user(user_id)
    rank = get_user_rank(chat_id, user_id)
    rank_fa = {"sudo": "🔱 سودو", "owner_main": "👑 مالک اصلی", "owner": "👑 مالک", "vip": "⭐ ویژه", "admin": "🛡️ ادمین", "member": "👤 کاربر"}.get(rank, "👤 کاربر")
    user_key = str(user_id)
    group_stats = group.get("stats", {}).get(user_key, {"messages": 0, "warnings": 0})
    text = f"📊 <b>آمار شما:</b>\n\n👤 نام: {user.first_name or 'ندارد'}\n🆔 آیدی: <code>{user_id}</code>\n🏅 مقام: {rank_fa}\n"
    if user_data.get("nickname"): text += f"💫 لقب: {user_data['nickname']}\n"
    text += f"\n📨 پیام‌ها: <b>{group_stats.get('messages', 0)}</b>\n⚠️ اخطارها: <b>{group_stats.get('warnings', 0)}</b>\n❌ خطاها: <b>{user_data.get('errors_count', 0)}</b>"
    return text

# ==================== سیستم فعال‌سازی و دستورات متنی ====================

@bot.message_handler(func=lambda m: m.text == "پنل من")
def my_panel(message):
    rank = get_user_rank(message.chat.id, message.from_user.id)
    send_msg(message.chat.id, 
        f"🤖 <b>پنل اختصاصی شما</b>\n\n👤 مقام: <b>{rank}</b>\n\nدستور مورد نظر را انتخاب کنید:", 
        reply_markup=main_menu(rank))

@bot.message_handler(func=lambda m: m.text in ["فعال", "نصب", "فعالسازی"])
def activate_bot(message):
    if message.chat.type in ['group', 'supergroup']:
        group = db.get_group(message.chat.id)
        if group["owner"] is None:
            group["owner"] = message.from_user.id; db.save()
            rank = 'owner_main'
        else:
            rank = get_user_rank(message.chat.id, message.from_user.id)
        send_msg(message.chat.id,
            f"✅ <b>ربات فعال شد!</b>\n\n"
            f"👤 <b>مالک:</b> {message.from_user.first_name}\n"
            f"🆔 <b>آیدی:</b> <code>{message.from_user.id}</code>\n\n"
            f"🎯 از منوی زیر استفاده کنید:",
            reply_markup=main_menu(rank))

@bot.message_handler(commands=['start', 'help'])
def start_cmd(message):
    rank = get_user_rank(message.chat.id, message.from_user.id)
    send_msg(message.chat.id,
        f"🤖 <b>به ربات مدیریتی خوش آمدید!</b>\n\n"
        f"👨‍💻 <b>ساخته شده برای گپ پدرام</b>\n\n"
        f"🎯 از منوی زیر استفاده کنید:",
        reply_markup=main_menu(rank))

@bot.message_handler(func=lambda m: m.text == "راهنما")
def help_cmd(message):
    rank = get_user_rank(message.chat.id, message.from_user.id)
    reply_msg(message, get_commands_text(rank), reply_markup=back_button())

# ==================== دستورات متنی قفل‌ها (هماهنگ با دکمه‌ها) ====================

@bot.message_handler(func=lambda m: m.text == "قفل لینک")
def lock_link_text(message):
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        reply_msg(message, "⛔ دسترسی ندارید."); return
    is_locked = toggle_lock(message.chat.id, "link")
    reply_msg(message, f"🔒 قفل لینک {'فعال' if is_locked else 'غیرفعال'} شد.")

@bot.message_handler(func=lambda m: m.text == "لینک باز")
def unlock_link_text(message):
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        reply_msg(message, "⛔ دسترسی ندارید."); return
    group = db.get_group(message.chat.id)
    group["locks"]["link"] = False; db.save()
    reply_msg(message, "🔓 قفل لینک غیرفعال شد.")

@bot.message_handler(func=lambda m: m.text == "قفل فحش")
def lock_fosh_text(message):
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        reply_msg(message, "⛔ دسترسی ندارید."); return
    is_locked = toggle_lock(message.chat.id, "fosh")
    reply_msg(message, f"🔒 قفل فحش {'فعال' if is_locked else 'غیرفعال'} شد.")

@bot.message_handler(func=lambda m: m.text == "فحش باز")
def unlock_fosh_text(message):
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        reply_msg(message, "⛔ دسترسی ندارید."); return
    group = db.get_group(message.chat.id)
    group["locks"]["fosh"] = False; db.save()
    reply_msg(message, "🔓 قفل فحش غیرفعال شد.")

@bot.message_handler(func=lambda m: m.text == "قفل فوروارد")
def lock_forward_text(message):
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        reply_msg(message, "⛔ دسترسی ندارید."); return
    is_locked = toggle_lock(message.chat.id, "forward")
    reply_msg(message, f"🔒 قفل فوروارد {'فعال' if is_locked else 'غیرفعال'} شد.")

@bot.message_handler(func=lambda m: m.text == "فوروارد باز")
def unlock_forward_text(message):
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        reply_msg(message, "⛔ دسترسی ندارید."); return
    group = db.get_group(message.chat.id)
    group["locks"]["forward"] = False; db.save()
    reply_msg(message, "🔓 قفل فوروارد غیرفعال شد.")

@bot.message_handler(func=lambda m: m.text == "قفل عکس")
def lock_photo_text(message):
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        reply_msg(message, "⛔ دسترسی ندارید."); return
    is_locked = toggle_lock(message.chat.id, "photo")
    reply_msg(message, f"🔒 قفل عکس {'فعال' if is_locked else 'غیرفعال'} شد.")

@bot.message_handler(func=lambda m: m.text == "عکس باز")
def unlock_photo_text(message):
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        reply_msg(message, "⛔ دسترسی ندارید."); return
    group = db.get_group(message.chat.id)
    group["locks"]["photo"] = False; db.save()
    reply_msg(message, "🔓 قفل عکس غیرفعال شد.")

@bot.message_handler(func=lambda m: m.text == "قفل فیلم")
def lock_video_text(message):
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        reply_msg(message, "⛔ دسترسی ندارید."); return
    is_locked = toggle_lock(message.chat.id, "video")
    reply_msg(message, f"🔒 قفل فیلم {'فعال' if is_locked else 'غیرفعال'} شد.")

@bot.message_handler(func=lambda m: m.text == "فیلم باز")
def unlock_video_text(message):
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        reply_msg(message, "⛔ دسترسی ندارید."); return
    group = db.get_group(message.chat.id)
    group["locks"]["video"] = False; db.save()
    reply_msg(message, "🔓 قفل فیلم غیرفعال شد.")

@bot.message_handler(func=lambda m: m.text == "قفل استیکر")
def lock_sticker_text(message):
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        reply_msg(message, "⛔ دسترسی ندارید."); return
    is_locked = toggle_lock(message.chat.id, "sticker")
    reply_msg(message, f"🔒 قفل استیکر {'فعال' if is_locked else 'غیرفعال'} شد.")

@bot.message_handler(func=lambda m: m.text == "استیکر باز")
def unlock_sticker_text(message):
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        reply_msg(message, "⛔ دسترسی ندارید."); return
    group = db.get_group(message.chat.id)
    group["locks"]["sticker"] = False; db.save()
    reply_msg(message, "🔓 قفل استیکر غیرفعال شد.")

@bot.message_handler(func=lambda m: m.text == "قفل انگلیسی")
def lock_english_text(message):
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        reply_msg(message, "⛔ دسترسی ندارید."); return
    is_locked = toggle_lock(message.chat.id, "english")
    reply_msg(message, f"🔒 قفل انگلیسی {'فعال' if is_locked else 'غیرفعال'} شد.")

@bot.message_handler(func=lambda m: m.text == "انگلیسی باز")
def unlock_english_text(message):
    if not has_permission(message.chat.id, message.from_user.id, "admin"):
        reply_msg(message, "⛔ دسترسی ندارید."); return
    group = db.get_group(message.chat.id)
    group["locks"]["english"] = False; db.save()
    reply_msg(message, "🔓 قفل انگلیسی غیرفعال شد.")

@bot.message_handler(func=lambda m: m.text == "لیست قفل")
def lock_list_text(message):
    group = db.get_group(message.chat.id)
    text = "🔒 <b>وضعیت قفل‌ها:</b>\n\n"
    lock_names = {"link": "لینک", "forward": "فوروارد", "username": "یوزرنیم", "photo": "عکس", "video": "فیلم", "music": "موزیک", "voice": "ویس", "document": "فایل", "sticker": "استیکر", "gif": "گیف", "english": "انگلیسی", "spam": "اسپم", "fosh": "فحش"}
    for key, name in lock_names.items():
        status = "🔒" if group["locks"].get(key, False) else "🔓"
        text += f"• {name}: {status}\n"
    reply_msg(message, text)

# ==================== دستورات متنی پشتیبانی ====================

@bot.message_handler(func=lambda m: m.text in ["بن", "بن کن"])
def ban_text(message):
    if not message.reply_to_message: reply_msg(message, "⚠️ روی پیام کاربر ریپلای کنید."); return
    if not has_permission(message.chat.id, message.from_user.id, "admin"): reply_msg(message, "⛔ دسترسی ندارید."); return
    target = message.reply_to_message.from_user
    group = db.get_group(message.chat.id)
    if target.id not in group["banned"]: group["banned"].append(target.id); db.save()
    try: bot.ban_chat_member(message.chat.id, target.id); reply_msg(message, f"✅ {target.first_name} بن شد.")
    except: reply_msg(message, "❌ خطا")

@bot.message_handler(func=lambda m: m.text in ["انبن", "حذف بن"])
def unban_text(message):
    if not message.reply_to_message: reply_msg(message, "⚠️ روی پیام کاربر ریپلای کنید."); return
    if not has_permission(message.chat.id, message.from_user.id, "admin"): reply_msg(message, "⛔ دسترسی ندارید."); return
    target = message.reply_to_message.from_user
    group = db.get_group(message.chat.id)
    if target.id in group["banned"]: group["banned"].remove(target.id); db.save()
    try: bot.unban_chat_member(message.chat.id, target.id); reply_msg(message, f"✅ {target.first_name} از بن خارج شد.")
    except: reply_msg(message, "❌ خطا")

@bot.message_handler(func=lambda m: m.text in ["سکوت", "سکوت کن"])
def mute_text(message):
    if not message.reply_to_message: reply_msg(message, "⚠️ روی پیام کاربر ریپلای کنید."); return
    if not has_permission(message.chat.id, message.from_user.id, "admin"): reply_msg(message, "⛔ دسترسی ندارید."); return
    target = message.reply_to_message.from_user
    group = db.get_group(message.chat.id)
    if target.id not in group["muted"]: group["muted"].append(target.id); db.save()
    reply_msg(message, f"🔇 {target.first_name} بی‌صدا شد.")

@bot.message_handler(func=lambda m: m.text in ["حذف سکوت", "انمیوت"])
def unmute_text(message):
    if not message.reply_to_message: reply_msg(message, "⚠️ روی پیام کاربر ریپلای کنید."); return
    if not has_permission(message.chat.id, message.from_user.id, "admin"): reply_msg(message, "⛔ دسترسی ندارید."); return
    target = message.reply_to_message.from_user
    group = db.get_group(message.chat.id)
    if target.id in group["muted"]: group["muted"].remove(target.id); db.save()
    reply_msg(message, f"🔊 {target.first_name} از بی‌صدا خارج شد.")

@bot.message_handler(func=lambda m: m.text in ["ادمین", "ادمین کن"])
def promote_admin_text(message):
    if not message.reply_to_message: reply_msg(message, "⚠️ روی پیام کاربر ریپلای کنید."); return
    if not has_permission(message.chat.id, message.from_user.id, "vip"): reply_msg(message, "⛔ دسترسی ندارید."); return
    target = message.reply_to_message.from_user
    promote_user(message.chat.id, target.id, "admin")
    reply_msg(message, f"✅ {target.first_name} ادمین شد.")

@bot.message_handler(func=lambda m: m.text in ["ویژه", "ویژه کن"])
def promote_vip_text(message):
    if not message.reply_to_message: reply_msg(message, "⚠️ روی پیام کاربر ریپلای کنید."); return
    if not has_permission(message.chat.id, message.from_user.id, "owner"): reply_msg(message, "⛔ دسترسی ندارید."); return
    target = message.reply_to_message.from_user
    promote_user(message.chat.id, target.id, "vip")
    reply_msg(message, f"⭐ {target.first_name} ویژه شد.")

@bot.message_handler(func=lambda m: m.text in ["مالک", "مالک کن"])
def promote_owner_text(message):
    if not message.reply_to_message: reply_msg(message, "⚠️ روی پیام کاربر ریپلای کنید."); return
    if not has_permission(message.chat.id, message.from_user.id, "owner"): reply_msg(message, "⛔ دسترسی ندارید."); return
    target = message.reply_to_message.from_user
    promote_user(message.chat.id, target.id, "owner")
    reply_msg(message, f"👑 {target.first_name} مالک شد.")

@bot.message_handler(func=lambda m: m.text in ["برکناری", "برکنار کن"])
def demote_text(message):
    if not message.reply_to_message: reply_msg(message, "⚠️ روی پیام کاربر ریپلای کنید."); return
    if not has_permission(message.chat.id, message.from_user.id, "owner"): reply_msg(message, "⛔ دسترسی ندارید."); return
    target = message.reply_to_message.from_user
    target_rank = get_user_rank(message.chat.id, target.id)
    if target_rank == "admin": demote_user(message.chat.id, target.id, "admin"); reply_msg(message, f"✅ {target.first_name} از ادمینی برکنار شد.")
    elif target_rank == "vip": demote_user(message.chat.id, target.id, "vip"); reply_msg(message, f"✅ {target.first_name} از ویژه برکنار شد.")
    elif target_rank == "owner": demote_user(message.chat.id, target.id, "owner"); reply_msg(message, f"✅ {target.first_name} از مالکی برکنار شد.")
    else: reply_msg(message, "⛔ این کاربر مقامی ندارد.")

@bot.message_handler(func=lambda m: m.text in ["آمار", "آمار من", "انفو"])
def stats_text(message):
    reply_msg(message, get_stats_text(message.chat.id, message.from_user.id, message.from_user))

@bot.message_handler(func=lambda m: m.text == "ایدي")
def id_text(message):
    rank = get_user_rank(message.chat.id, message.from_user.id)
    rank_fa = {"sudo": "🔱 سودو", "owner_main": "👑 مالک اصلی", "owner": "👑 مالک", "vip": "⭐ ویژه", "admin": "🛡️ ادمین", "member": "👤 کاربر"}.get(rank, "👤 کاربر")
    reply_msg(message, f"🆔 <b>شناسه شما:</b> <code>{message.from_user.id}</code>\n👤 نام: {message.from_user.first_name or ''}\n🏅 مقام: {rank_fa}")

@bot.message_handler(func=lambda m: m.text.startswith("تنظیم لقب"))
def set_nickname_text(message):
    parts = message.text.split(" ", 2)
    if len(parts) < 3: reply_msg(message, "⚠️ فرمت: <code>تنظیم لقب [لقب]</code>"); return
    nickname = parts[2].strip()
    if message.reply_to_message and has_permission(message.chat.id, message.from_user.id, "vip"):
        target = message.reply_to_message.from_user
        user_data = db.get_user(target.id)
        user_data["nickname"] = nickname; db.save()
        reply_msg(message, f"✅ لقب برای {target.first_name} تنظیم شد: <b>{nickname}</b>")
    else:
        user_data = db.get_user(message.from_user.id)
        user_data["nickname"] = nickname; db.save()
        reply_msg(message, f"✅ لقب شما به <b>{nickname}</b> تغییر یافت.")

@bot.message_handler(func=lambda m: m.text.startswith("افزودن فحش"))
def add_bad_word(message):
    if not has_permission(message.chat.id, message.from_user.id, "owner"):
        reply_msg(message, "⛔ فقط مالک می‌تواند."); return
    parts = message.text.split(" ", 1)
    if len(parts) < 2: reply_msg(message, "⚠️ فرمت: افزودن فحش [کلمه]"); return
    word = parts[1].strip()
    group = db.get_group(message.chat.id)
    if word not in group["bad_words"]:
        group["bad_words"].append(word)
        db.save()
        reply_msg(message, f"✅ کلمه <b>{word}</b> به لیست فحش اضافه شد.")
    else:
        reply_msg(message, "⚠️ این کلمه قبلاً در لیست وجود دارد.")

@bot.message_handler(func=lambda m: m.text.startswith("حذف فحش"))
def remove_bad_word(message):
    if not has_permission(message.chat.id, message.from_user.id, "owner"):
        reply_msg(message, "⛔ فقط مالک می‌تواند."); return
    parts = message.text.split(" ", 1)
    if len(parts) < 2: reply_msg(message, "⚠️ فرمت: حذف فحش [کلمه]"); return
    word = parts[1].strip()
    group = db.get_group(message.chat.id)
    if word in group["bad_words"]:
        group["bad_words"].remove(word)
        db.save()
        reply_msg(message, f"✅ کلمه <b>{word}</b> از لیست فحش حذف شد.")
    else:
        reply_msg(message, "⚠️ این کلمه در لیست وجود ندارد.")

# ==================== بررسی پیام‌ها ====================
@bot.message_handler(func=lambda m: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'sticker', 'animation'])
def check_message(message):
    if message.chat.type not in ['group', 'supergroup']: return
    
    if message.new_chat_members:
        group = db.get_group(message.chat.id)
        if group["settings"].get("welcome", True):
            for new_member in message.new_chat_members:
                if not new_member.is_bot:
                    send_msg(message.chat.id, f"👋 <b>خوش آمدید!</b>\n\n👤 {new_member.first_name}\n👨‍💻 ساخته شده برای گپ پدرام")
        return

    group = db.get_group(message.chat.id)
    user_id = message.from_user.id
    user_data = db.get_user(user_id)
    user_data["messages_count"] += 1
    user_key = str(user_id)
    if user_key not in group["stats"]: group["stats"][user_key] = {"messages": 0, "warnings": 0}
    group["stats"][user_key]["messages"] += 1
    db.save()
    
    if user_id in group["muted"]:
        try: bot.delete_message(message.chat.id, message.message_id)
        except: pass
        return
    if user_id in group["banned"]:
        try: bot.ban_chat_member(message.chat.id, user_id)
        except: pass
        return
    if has_permission(message.chat.id, user_id, "admin") or user_id in group.get("immune", []):
        _handle_speaker(message, group); return
        
    violated = False; reason = ""
    
    if message.text and group["locks"]["link"] and re.search(r'(https?://|www\.|t\.me)', message.text): 
        violated, reason = True, "ارسال لینک"
    elif message.text and group["locks"]["username"] and re.search(r'@[\w_]{3,}', message.text): 
        violated, reason = True, "ارسال یوزرنیم"
    elif message.text and group["locks"]["fosh"]:
        bad_words = group.get("bad_words", [])
        if any(w in message.text for w in bad_words): 
            violated, reason = True, "ارسال فحش"
    elif message.text and group["locks"]["english"] and re.search(r'[a-zA-Z]{3,}', message.text): 
        violated, reason = True, "متن انگلیسی"
    elif group["locks"]["forward"] and message.forward_date: 
        violated, reason = True, "فوروارد"
    elif group["locks"]["photo"] and message.photo: violated, reason = True, "عکس"
    elif group["locks"]["video"] and message.video: violated, reason = True, "فیلم"
    elif group["locks"]["music"] and message.audio: violated, reason = True, "موزیک"
    elif group["locks"]["voice"] and message.voice: violated, reason = True, "ویس"
    elif group["locks"]["document"] and message.document: violated, reason = True, "فایل"
    elif group["locks"]["sticker"] and message.sticker: violated, reason = True, "استیکر"
    elif group["locks"]["gif"] and message.animation: violated, reason = True, "گیف"
    
    if violated:
        try: bot.delete_message(message.chat.id, message.message_id)
        except: pass
        if group.get("auto_ban", True): 
            auto_ban_user(message.chat.id, user_id, reason)
        else:
            if user_key not in group["warning_counts"]: group["warning_counts"][user_key] = {}
            group["warning_counts"][user_key][reason] = group["warning_counts"][user_key].get(reason, 0) + 1
            group["stats"][user_key]["warnings"] += 1; db.save()
            send_msg(message.chat.id, f"⚠️ اخطار! دلیل: {reason}")
        return
    _handle_speaker(message, group)

def _handle_speaker(message, group):
    if not group["speaker"]["enabled"] or not message.text: return
    text = message.text.strip()
    user_key = str(message.from_user.id)
    bot_custom_name = group.get("user_bot_names", {}).get(user_key, None)
    call_names = ["بات", "ربات", "باتی", "بات کچولو"]
    if bot_custom_name: call_names.append(bot_custom_name)
    if not any(name in text for name in call_names) and random.random() > 0.10: return
    response = None
    for key in SPEAKER_RESPONSES:
        if key != "default" and key in text:
            response = random.choice(SPEAKER_RESPONSES[key]); break
    if not response: response = random.choice(SPEAKER_RESPONSES["default"])
    try: bot.reply_to(message, f"{response}\n\n~ {random.choice(SPEAKER_NAMES)} 🤖")
    except: pass

# ==================== شروع ربات ====================
if __name__ == "__main__":
    print("=" * 50)
    print("🤖 ربات مدیریتی تلگرام - نسخه نهایی")
    print("=" * 50)
    print("✅ قفل‌ها کار می‌کنند!")
    print("✅ دکمه‌های شیشه‌ای + دستورات متنی هماهنگ")
    print("✅ تمام باگ‌ها رفع شده")
    print("=" * 50)
    bot.infinity_polling()
