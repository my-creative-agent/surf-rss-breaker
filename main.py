import os
import time
import threading
import feedparser
import requests
import random
import re
from groq import Groq
from flask import Flask
from telebot import apihelper
import telebot

# --- НАСТРОЙКИ ---
app = Flask(__name__)
@app.route('/')
def home(): return "Dr. Surf Omniscient Hunter: Active 🏄‍♂️🌱"

BOT_TOKEN = os.environ.get('BOT_TOKEN', '').strip()
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '').strip()
LOG_GROUP_ID = os.environ.get('LOG_GROUP_ID', '2048745216')
MY_ID = 123456789  # <--- ЗАМЕНИ ЭТО НА СВОЙ ID ИЗ @userinfobot

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
client = Groq(api_key=GROQ_API_KEY)

SENT_PROJECTS = set()
SENT_MESSAGES = set()

SYSTEM_PROMPT = "Ты — Dr. Surf, всезнающий цифровой двойник Виктории Акопян. Стиль: серферский минимализм, веган, эксперт в AI, крипте и медицине. Отвечай от женского лица, кратко и пафосно."

RSS_FEEDS = [
    {"url": "https://www.fl.ru/rss/all.xml", "name": "🚀 FL"},
    {"url": "https://freelance.habr.com/tasks.rss", "name": "👨‍💻 Habr"},
    {"url": "https://kwork.ru/projects/rss", "name": "🎨 Kwork"}
]

# --- ЭСТЕТИКА И ФИНАНСЫ ---
def get_cute_trade_signal(setup, symbol):
    dinosaurs, bears, hearts = ["🦖", "🦕", "🐲"], ["🐻", "🐼", "🐨"], ["💖", "💕", "✨", "🌸"]
    dino, bear, heart = random.choice(dinosaurs), random.choice(bears), random.choice(hearts)
    return (f"{dino} **DR. SURF MARKET REPORT** {dino}\n\n"
            f"📅 **Time:** {setup['time']} \n"
            f"🎯 **Signal:** {symbol} — READY TO HUNT!\n\n"
            f"{bear} **Leverage:** {setup['leverage']}x (Stay sharp!)\n"
            f"🛑 **Stop Loss:** {setup['sl']} 🛡\n"
            f"🚀 **Take Profit:** {setup['tp']} {heart}\n\n"
            f"✨ *Виктория, всё под контролем! Рынок мягкий и послушный.* ✨")

# --- ЛОГИКА ---
def clean_html(text): return re.sub(r'<[^>]+>', '', text) if text else ""

def send_to_group(text):
    if text not in SENT_MESSAGES:
        try:
            bot.send_message(LOG_GROUP_ID, text, parse_mode="HTML", disable_web_page_preview=True)
            SENT_MESSAGES.add(text)
            if len(SENT_MESSAGES) > 50: SENT_MESSAGES.clear()
        except: pass

def fetch_orders():
    found = []
    for feed in RSS_FEEDS:
        try:
            feed_data = feedparser.parse(feed["url"])
            for entry in feed.entries[:5]:
                if entry.link not in SENT_PROJECTS:
                    found.append({"title": entry.title, "url": entry.link, "site": feed["name"]})
                    SENT_PROJECTS.add(entry.link)
        except: continue
    return found

def auto_hunter():
    while True:
        projects = fetch_orders()
        for p in projects:
            msg = f"🔥 <b>ОХОТНИК ПОЙМАЛ ЗАКАЗ:</b>\n📍 {p['site']}\n📝 {clean_html(p['title'])}\n🔗 {p['url']}"
            send_to_group(msg)
        time.sleep(900)

# --- ОБРАБОТКА КОМАНД ---
@bot.message_handler(func=lambda m: m.text.lower() == "tyrex")
def secret_tyrex_signal(message):
    if message.from_user.id != MY_ID: return
    
    bot.reply_to(message, "🦖 **T-REX SYSTEM ACTIVATED...**")
    setup = {"time": time.strftime('%H:%M:%S UTC'), "leverage": "5", "sl": "64,150", "tp": "67,800"}
    bot.reply_to(message, get_cute_trade_signal(setup, "BTC/USDT"))

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    if message.from_user.is_bot: return
    reply = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": message.text}]
    ).choices[0].message.content
    bot.reply_to(message, reply)

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    threading.Thread(target=auto_hunter, daemon=True).start()
    bot.polling(none_stop=True)
