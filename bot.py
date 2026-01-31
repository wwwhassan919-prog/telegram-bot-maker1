import telebot
from telebot import types
import sqlite3
import subprocess
import os

# 🔴 ضع توكن البوت الأساسي هنا فقط
TOKEN = "8210570293:AAEJXZQ2wO9DmnH_PlktisXhgKSKqVj69CU"

bot = telebot.TeleBot(TOKEN)

# ───────────── حالات المستخدم ─────────────
user_state = {}

# ───────────── قاعدة البيانات ─────────────
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    chat_id INTEGER PRIMARY KEY,
    token TEXT,
    language TEXT
)
""")
conn.commit()

# ───────────── start ─────────────
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🤖 إنشاء بوت", "🌍 اللغة", "ℹ️ معلومات")
    bot.send_message(
        message.chat.id,
        "🌍 أهلاً بك في صانع البوتات العالمي\nاختر من القائمة:",
        reply_markup=markup
    )

# ───────────── معلومات ─────────────
@bot.message_handler(func=lambda m: m.text == "ℹ️ معلومات")
def info(message):
    bot.send_message(
        message.chat.id,
        "🤖 صانع بوتات عالمي\n"
        "✅ مجاني 100%\n"
        "🚀 سريع\n"
        "🌍 يعمل للجميع\n"
        "🚫 بدون إعلانات"
    )

# ───────────── إنشاء بوت ─────────────
@bot.message_handler(func=lambda m: m.text == "🤖 إنشاء بوت")
def create_bot(message):
    user_state[message.chat.id] = "waiting_token"
    bot.send_message(
        message.chat.id,
        "📩 أرسل توكن البوت الذي أنشأته من @BotFather"
    )

# ───────────── استقبال التوكن + إنشاء بوت جديد ─────────────
@bot.message_handler(func=lambda m: m.chat.id in user_state and user_state[m.chat.id] == "waiting_token")
def get_token(message):
    token = message.text.strip()
    chat_id = message.chat.id

    if ":" not in token or len(token) < 20:
        bot.send_message(chat_id, "❌ التوكن غير صالح، حاول مرة أخرى")
        return

    # حفظ التوكن
    cursor.execute(
        "INSERT OR REPLACE INTO users (chat_id, token, language) VALUES (?, ?, ?)",
        (chat_id, token, "ar")
    )
    conn.commit()
    user_state.pop(chat_id)

    # اسم ملف البوت الجديد
    bot_filename = f"user_bot_{chat_id}.py"

    # كود البوت الجديد
    bot_code = f'''
import telebot

TOKEN = "{token}"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🤖 هذا بوتك الخاص يعمل بنجاح ✅")

@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.reply_to(message, message.text)

bot.infinity_polling(skip_pending=True, timeout=10)
'''

    # إنشاء الملف
    with open(bot_filename, "w") as f:
        f.write(bot_code)

    # تشغيل البوت الجديد
    subprocess.Popen(["python", bot_filename])

    bot.send_message(
        chat_id,
        "🎉 تم إنشاء وتشغيل البوت بنجاح!\n"
        "📌 افتح البوت الجديد واكتب /start"
    )

# ───────────── اللغة (أساس) ─────────────
@bot.message_handler(func=lambda m: m.text == "🌍 اللغة")
def language(message):
    bot.send_message(
        message.chat.id,
        "🌍 دعم لغات متعددة (قريباً)"
    )

# ───────────── رسائل أخرى (خفيف وسريع) ─────────────
@bot.message_handler(func=lambda m: m.text not in ["🤖 إنشاء بوت", "🌍 اللغة", "ℹ️ معلومات"])
def other_messages(message):
    bot.send_message(
        message.chat.id,
        "❓ استخدم الأزرار أو اكتب /start"
    )

# ───────────── تشغيل البوت ─────────────
bot.infinity_polling(skip_pending=True)
