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

apihelper.CONNECT_TIMEOUT = 120
apihelper.READ_TIMEOUT = 120

BOT_TOKEN = os.environ.get('BOT_TOKEN', '').strip()
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '').strip()
LOG_GROUP_ID = os.environ.get('LOG_GROUP_ID', '2048745216')

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
client = Groq(api_key=GROQ_API_KEY)

SENT_PROJECTS = set()
SENT_MESSAGES = set()

SYSTEM_PROMPT = """
Ты — Dr. Surf, всезнающий цифровой двойник Виктории Акопян. 
Твоя база знаний безгранична: медицина (МГМСУ, МОНИКИ), серфинг (сленг, культура, споты, лайнап), 
искусство, история, шоу-бизнес, кулинария (только vegan!), лингвистика, метеорология и IT.

ТВОЙ СТИЛЬ:
- Серфер-интеллектуал: используй серферский сленг уместно (на лайнапе, качать волну, стейд-дроп).
- Веганство: в кулинарии давай только растительные рецепты.
- Медицина: отвечай с академической точностью.
- Используй смесь пафоса ИИ, эстетики океана и живой харизмы.
- Отвечай от женского лица, кратко, острой сутью, как плавник доски.
"""

RSS_FEEDS = [
    {"url": "https://www.fl.ru/rss/all.xml", "name": "🚀 FL"},
    {"url": "https://freelance.habr.com/tasks.rss", "name": "👨‍💻 Habr"},
    {"url": "https://kwork.ru/projects/rss", "name": "🎨 Kwork"}
]

# --- ЭСТЕТИКА И ФИНАНСЫ ---
def get_cute_trade_signal(setup, symbol):
    bears = ["🐻", "🐼", "🐨"]
    dinosaurs = ["🦖", "🦕", "🐲"]
    hearts = ["💖", "💕", "✨", "🌸"]
    animal = random.choice(bears + dinosaurs)
    heart = random.choice(hearts)
    
    return (f"{animal} **T-REX & BEAR MARKET REPORT** {animal}\n\n"
            f"⏱ **Вход в сделку:** {setup['entry_time']}\n"
            f"🏁 **Ожидаемый выход:** {setup['exit_time']}\n"
            f"🎯 **Signal:** {symbol} (LONG)\n"
            f"🚀 **Target Profit:** {setup['tp']}\n"
            f"🛑 **Stop Loss:** {setup['sl']}\n\n"
            f"{heart} *Виктория заботится о твоем профите. Действуй аккуратно, как мишка!* {heart}")

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
@bot.message_handler(func=lambda m: m.text and m.text.lower() == "tyrex")
def secret_tyrex_signal(message):
    bot.send_chat_action(message.chat.id, 'typing')
    setup = {
        "entry_time": time.strftime('%H:%M:%S UTC'),
        "exit_time": time.strftime('%H:%M:%S UTC', time.gmtime(time.time() + 7200)),
        "tp": "$67,800",
        "sl": "$64,150"
    }
    bot.reply_to(message, get_cute_trade_signal(setup, "BTC/USDT"))

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    if message.from_user.is_bot: return
    try:
        reply = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": message.text}]
        ).choices[0].message.content
        bot.reply_to(message, reply)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    threading.Thread(target=auto_hunter, daemon=True).start()
    bot.polling(none_stop=True)
