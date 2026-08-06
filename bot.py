import subprocess, sys

print("🔧 شروع نصب...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "telethon"])

print("\n🔐 لطفاً شماره و کد خود را وارد کنید:\n")
from telethon import TelegramClient
client = TelegramClient("personal_session", 2040, "b18441a1ff607e10a989891a5462e627")
client.start()
print("\n✅ فایل personal_session.session ساخته شد!")
