import os
import time
import threading
import feedparser
import requests
import random
import re
from groq import Groq
from flask import Flask, request
import telebot

# --- НАСТРОЙКИ ---
app = Flask(__name__)
BOT_TOKEN = os.environ.get('BOT_TOKEN', '').strip()
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '').strip()
LOG_GROUP_ID = os.environ.get('LOG_GROUP_ID', '').strip()
WEBHOOK_URL = f"https://surf-rss-breaker.onrender.com/{BOT_TOKEN}"
ACCESS_CODE = "хочу пол кураги и кешью"

CONTACTS = {
    "instagram_dr": "https://instagram.com/dr.surf",
    "kwork_portfolio": "https://kwork.ru/user/dr_surf",
    "telegram": "https://t.me/Dr_Surf"
}

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)
SENT_PROJECTS = set()
user_access = {}

SYSTEM_PROMPT = "Ты — Dr. Surf, цифровой двойник Виктории. Отвечай от женского лица, серферский сленг, веганство. Эмодзи строго по 1-2."

RSS_FEEDS = [
    {"url": "https://www.fl.ru/rss/all.xml", "name": "🚀 FL"},
    {"url": "https://freelance.habr.com/tasks.rss", "name": "👨‍💻 Habr"},
    {"url": "https://kwork.ru/projects/rss", "name": "🎨 Kwork"}
]

def get_cute_trade_signal(symbol):
    bears = ["🐻", "🐼", "🐨"]
    dinosaurs = ["🦖", "🦕", "🐲"]
    animal = random.choice(bears + dinosaurs)
    return (f"{animal} **T-REX & BEAR MARKET REPORT** {animal}\n\n"
            f"🎯 Signal: {symbol} (LONG)\n"
            f"🚀 Target Profit: $67,800\n"
            f"🛑 Stop Loss: $64,150\n\n"
            f"✨ Виктория заботится о твоем профите! 🏄‍♀️")

def auto_hunter():
    while True:
        try:
            for feed in RSS_FEEDS:
                data = feedparser.parse(feed["url"])
                for entry in data.entries[:3]:
                    if entry.link not in SENT_PROJECTS:
                        SENT_PROJECTS.add(entry.link)
                        emojis = "".join(random.sample(["🌊", "🏄‍♀️", "🦀", "🐬", "🌸"], 2))
                        if LOG_GROUP_ID:
                            bot.send_message(LOG_GROUP_ID, f"🔥 {emojis} {feed['name']}: {entry.title}\n🔗 {entry.link}")
        except: pass
        time.sleep(300)

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    user_id = message.chat.id
    text = message.text.lower().strip()
    
    if text == ACCESS_CODE:
        user_access[user_id] = True
        bot.reply_to(message, "Доступ открыт, серфер! 🌊")
        return

    if "отчет" in text or "сигнал" in text:
        if user_access.get(user_id):
            bot.reply_to(message, get_cute_trade_signal("BTC/USDT"))
            user_access[user_id] = False
        else:
            bot.reply_to(message, "Кодовое слово, плиз! 🐚")
        return

    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": message.text}]
        )
        bot.reply_to(message, completion.choices[0].message.content)
    except:
        bot.reply_to(message, "Волна мыслей ушла в штиль. 🏄‍♀️")

@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == "__main__":
    bot.remove_webhook()
    # Сначала даем команду Telegram, куда слать данные
    bot.set_webhook(url=f"https://surf-rss-breaker.onrender.com/{BOT_TOKEN}")
    
    threading.Thread(target=auto_hunter, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
