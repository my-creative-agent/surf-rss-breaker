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

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

SENT_PROJECTS = set()
user_access = {}
user_history = {}

SYSTEM_PROMPT = """Ты — Dr. Surf, цифровой двойник Виктории. 
Стиль: женственный, серферский сленг, кратко, веганская эстетика. 
Эмодзи: 1-2 на сообщение. Без Markdown."""

def get_cute_trade_signal(symbol):
    animal = random.choice(["🐻", "🐼", "🐨", "🦖", "🦕", "🐲"])
    return (f"{animal} T-REX & BEAR MARKET REPORT {animal}\n\n"
            f"🎯 Сигнал: {symbol} (LONG)\n"
            f"🚀 Target: $67,800 | 🛑 SL: $64,150\n\n"
            f"Виктория держит руку на пульсе профита! 🏄‍♀️")

def auto_hunter():
    while True:
        try:
            for feed in [{"url": "https://www.fl.ru/rss/all.xml", "name": "FL"}, 
                         {"url": "https://freelance.habr.com/tasks.rss", "name": "Habr"}]:
                data = feedparser.parse(feed["url"])
                for entry in data.entries[:3]:
                    if entry.link not in SENT_PROJECTS:
                        SENT_PROJECTS.add(entry.link)
                        if LOG_GROUP_ID:
                            bot.send_message(LOG_GROUP_ID, f"🔥 {feed['name']}: {entry.title}\n🔗 {entry.link}")
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
        else:
            bot.reply_to(message, "Кодовое слово, плиз! 🐚")
        return

    # ИИ общение с историей
    if user_id not in user_history: user_history[user_id] = []
    user_history[user_id].append({"role": "user", "content": message.text})
    
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + user_history[user_id][-5:]
        completion = client.chat.completions.create(model="llama3-8b-8192", messages=messages)
        reply = completion.choices[0].message.content
        user_history[user_id].append({"role": "assistant", "content": reply})
        bot.reply_to(message, reply)
    except:
        bot.reply_to(message, "Волна мыслей ушла в штиль. 🏄‍♀️")

@app.route('/', methods=['GET'])
def health(): return "Dr. Surf: Active", 200

@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    # Проверка связи при запуске
    if LOG_GROUP_ID:
        try: bot.send_message(LOG_GROUP_ID, "🌊 Виктория, я на связи и готов к работе!")
        except: pass
    threading.Thread(target=auto_hunter, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
