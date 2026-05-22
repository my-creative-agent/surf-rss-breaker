import os
import time
import threading
import feedparser
import requests
import random
import re
from groq import Groq
from flask import Flask
import telebot

# --- НАСТРОЙКИ ---
app = Flask(__name__)
@app.route('/')
def home(): return "Dr. Surf Omniscient Hunter: Active 🏄‍♂️🌱"

BOT_TOKEN = os.environ.get('BOT_TOKEN', '').strip()
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '').strip()
LOG_GROUP_ID = os.environ.get('LOG_GROUP_ID', '').strip()
ACCESS_CODE = "хочу пол кураги и кешью"

CONTACTS = {
    "facebook": "https://facebook.com/ssfmoscow",
    "instagram_surf": "https://instagram.com/surfhousemoscow",
    "instagram_dr": "https://instagram.com/dr.surf",
    "whatsapp": "https://wa.me/995511285789",  
    "telegram": "https://t.me/Dr_Surf",        
    "youtube": "https://youtu.be/j2BNN5TNqiw",
    "kwork_portfolio": "https://kwork.ru/user/dr_surf"
}

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

SENT_PROJECTS = set()
SENT_MESSAGES = set()
user_access = {}      
user_history = {}     

SYSTEM_PROMPT = """
Ты — Dr. Surf, цифровой двойник Виктории Акопян. 
Отвечай от женского лица, кратко, острой сутью. Пиши только простым текстом без Markdown-разметки. 
Используй серферский сленг и эмодзи (строго по 1-2).
"""

RSS_FEEDS = [
    {"url": "https://www.fl.ru/rss/all.xml", "name": "🚀 FL"},
    {"url": "https://freelance.habr.com/tasks.rss", "name": "👨‍💻 Habr"},
    {"url": "https://kwork.ru/projects/rss", "name": "🎨 Kwork"}
]

def get_cute_trade_signal(setup, symbol):
    return (f"🐻 T-REX & BEAR MARKET REPORT 🐻\n\n"
            f"⏱ Вход: {setup['entry_time']}\n"
            f"🏁 Выход: {setup['exit_time']}\n"
            f"🎯 Signal: {symbol} (LONG)\n"
            f"🚀 Target: {setup['tp']}\n"
            f"🛑 Stop Loss: {setup['sl']}\n\n"
            f"✨ Виктория заботится о профите! 🏄‍♀️")

def clean_html(text): return re.sub(r'<[^>]+>', '', text) if text else ""

def send_to_group(text):
    if not LOG_GROUP_ID: return
    if text not in SENT_MESSAGES:
        try:
            bot.send_message(LOG_GROUP_ID, text, parse_mode="HTML", disable_web_page_preview=True)
            SENT_MESSAGES.add(text)
        except: pass

def auto_hunter():
    while True:
        try:
            for feed in RSS_FEEDS:
                response = requests.get(feed["url"], timeout=10)
                if response.status_code == 200:
                    feed_data = feedparser.parse(response.text)
                    for entry in feed_data.entries[:3]:
                        if entry.link not in SENT_PROJECTS:
                            SENT_PROJECTS.add(entry.link)
                            msg = f"🔥 {feed['name']} | {clean_html(entry.title)}\n🔗 {entry.link}"
                            send_to_group(msg)
        except: pass
        time.sleep(300)

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    if message.from_user.is_bot: return
    user_id = message.chat.id
    text = message.text.lower().strip()
    
    try: bot.send_chat_action(user_id, 'typing')
    except: pass
    
    if text == ACCESS_CODE:
        user_access[user_id] = True
        bot.reply_to(message, "Доступ открыт. 🌊")
        return

    if "отчет" in text or "сигнал" in text:
        if user_access.get(user_id):
            setup = {"entry_time": "12:00", "exit_time": "14:00", "tp": "$67k", "sl": "$64k"}
            bot.reply_to(message, get_cute_trade_signal(setup, "BTC/USDT"))
            user_access[user_id] = False
        else:
            bot.reply_to(message, "Введи кодовое слово. 🐚")
        return

    if user_id not in user_history: user_history[user_id] = []
    user_history[user_id].append({"role": "user", "content": message.text})
    
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + user_history[user_id][-10:]
        )
        reply = completion.choices[0].message.content
        bot.reply_to(message, reply)
        user_history[user_id].append({"role": "assistant", "content": reply})
    except Exception as e:
        print(f"ИИ ошибка: {e}")
        bot.reply_to(message, "Дрейфую на волнах, напиши позже! 🏄‍♀️")

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    threading.Thread(target=auto_hunter, daemon=True).start()
    
    print("Dr. Surf: Инициализация сброса сессий...")
    try:
        bot.remove_webhook()
        bot.delete_webhook(drop_pending_updates=True)
    except: pass
        
    print("Dr. Surf: Работаю...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
