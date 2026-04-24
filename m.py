import telebot
import threading
import time
import json
from datetime import datetime, timedelta

# =========================
# CONFIG
# =========================
TOKEN = "8226453895:AAGF8pUed9vTmc0LwW6blrT6R4fg_BOYobc".strip()
ADMIN_IDS = [6535069863]

bot = telebot.TeleBot(TOKEN)

# =========================
# DATA
# =========================
user_attacks = {}
user_cooldowns = {}
USER_PLANS = {}
APPROVED_USERS = set()

USER_PLANS_FILE = "user_plans.json"
APPROVED_USERS_FILE = "approved_users.json"

# =========================
# FILE HANDLING
# =========================
def load_data():
    global USER_PLANS, APPROVED_USERS
    try:
        with open(USER_PLANS_FILE, "r") as f:
            data = json.load(f)
            for uid, plan in data.items():
                USER_PLANS[int(uid)] = {
                    "plan": plan["plan"],
                    "expiry": datetime.fromisoformat(plan["expiry"]),
                    "approved": plan["approved"]
                }
    except:
        USER_PLANS = {}

    try:
        with open(APPROVED_USERS_FILE, "r") as f:
            APPROVED_USERS = set(json.load(f))
    except:
        APPROVED_USERS = set()

def save_data():
    data = {}
    for uid, plan in USER_PLANS.items():
        data[str(uid)] = {
            "plan": plan["plan"],
            "expiry": plan["expiry"].isoformat(),
            "approved": plan["approved"]
        }
    with open(USER_PLANS_FILE, "w") as f:
        json.dump(data, f)

    with open(APPROVED_USERS_FILE, "w") as f:
        json.dump(list(APPROVED_USERS), f)

load_data()

# =========================
# HELPERS
# =========================
def is_approved(user_id):
    if user_id in ADMIN_IDS:
        return True
    if user_id in USER_PLANS:
        plan = USER_PLANS[user_id]
        return plan["approved"] and plan["expiry"] > datetime.now()
    return user_id in APPROVED_USERS

def get_plan(user_id):
    if user_id in ADMIN_IDS:
        return "Admin"
    if user_id in USER_PLANS:
        return USER_PLANS[user_id]["plan"]
    return "Free"

# =========================
# COMMANDS
# =========================

@bot.message_handler(commands=['start'])
def start(msg):
    user_id = msg.from_user.id
    username = msg.from_user.username or msg.from_user.first_name

    status = "✅ Approved" if is_approved(user_id) else "❌ Not Approved"

    text = (
        f"👋 Hello @{username}\n\n"
        f"Status: {status}\n"
        f"Plan: {get_plan(user_id)}\n\n"
        f"/myinfo - Check info\n"
        f"/status - Bot status\n"
        f"/owner - Contact admin"
    )
    bot.reply_to(msg, text)

# =========================

@bot.message_handler(commands=['myinfo'])
def myinfo(msg):
    user_id = msg.from_user.id
    username = msg.from_user.username or msg.from_user.first_name

    text = (
        f"👤 User: @{username}\n"
        f"🆔 ID: {user_id}\n"
        f"📋 Plan: {get_plan(user_id)}\n"
        f"📊 Requests Today: {user_attacks.get(user_id, 0)}"
    )
    bot.reply_to(msg, text)

# =========================

@bot.message_handler(commands=['status'])
def status(msg):
    bot.reply_to(msg, "🤖 Bot is running smoothly!")

# =========================

@bot.message_handler(commands=['owner'])
def owner(msg):
    bot.reply_to(msg, f"👑 Admin ID: {ADMIN_IDS[0]}")

# =========================
# ADMIN
# =========================

@bot.message_handler(commands=['approve'])
def approve(msg):
    if msg.from_user.id not in ADMIN_IDS:
        return bot.reply_to(msg, "❌ Admin only")

    try:
        uid = int(msg.text.split()[1])

        USER_PLANS[uid] = {
            "plan": 300,
            "expiry": datetime.now() + timedelta(days=1),
            "approved": True
        }

        APPROVED_USERS.add(uid)
        save_data()

        bot.reply_to(msg, f"✅ Approved {uid}")
    except:
        bot.reply_to(msg, "Usage: /approve user_id")

# =========================
# MAIN
# =========================

print("Bot running...")

while True:
    try:
        bot.infinity_polling(skip_pending=True)
    except Exception as e:
        print("Error:", e)
        time.sleep(5)