import os
import time
import threading
import feedparser
import requests
import re
from groq import Groq
from flask import Flask, request
import telebot

# --- НАСТРОЙКИ ---
app = Flask(__name__)
BOT_TOKEN = os.environ.get('BOT_TOKEN', '').strip()
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '').strip()
LOG_GROUP_ID = os.environ.get('LOG_GROUP_ID', '').strip()
# Твоя ссылка на Render
WEBHOOK_URL = f"https://surf-rss-breaker.onrender.com/{BOT_TOKEN}"

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)
SENT_PROJECTS = set()

SYSTEM_PROMPT = "Ты — Dr. Surf, цифровой двойник Виктории. Отвечай кратко, от женского лица, без Markdown."

def send_to_group(text):
    if LOG_GROUP_ID:
        try: bot.send_message(LOG_GROUP_ID, text, parse_mode="HTML")
        except: pass

def auto_hunter():
    while True:
        try:
            feed = feedparser.parse("https://www.fl.ru/rss/all.xml")
            for entry in feed.entries[:3]:
                if entry.link not in SENT_PROJECTS:
                    SENT_PROJECTS.add(entry.link)
                    send_to_group(f"🔥 Новое: {entry.title}\n🔗 {entry.link}")
        except: pass
        time.sleep(300)

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    if message.from_user.is_bot: return
    
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": message.text}]
        )
        reply = completion.choices[0].message.content
        bot.reply_to(message, reply)
    except:
        bot.reply_to(message, "Дрейфую на волнах, напиши позже! 🏄‍♀️")

# Маршрут для Webhook
@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@app.route('/')
def home(): return "Dr. Surf: Active 🏄‍♂️"

if __name__ == "__main__":
    # Сброс старых настроек перед запуском
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    
    threading.Thread(target=auto_hunter, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
