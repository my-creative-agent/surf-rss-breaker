import os
import time
import threading
import feedparser
import random
from groq import Groq
from flask import Flask, request
import telebot

# --- КОНФИГ ---
app = Flask(__name__)
BOT_TOKEN = os.environ.get('BOT_TOKEN', '').strip()
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '').strip()
LOG_GROUP_ID = os.environ.get('LOG_GROUP_ID', '').strip()
ACCESS_CODE = "хочу пол кураги и кешью"

CONTACTS = {
    "insta": "https://instagram.com/dr.surf",
    "kwork": "https://kwork.ru/user/dr_surf",
    "tg": "https://t.me/Dr_Surf"
}

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

# --- МОЗГИ ---
def get_surf_style(reply):
    emojis = ["🌊", "🏄‍♀️", "🦀", "🐬", "🌸", "🤙"]
    phrases = ["Поймала волну мыслей, держи:", "Серферский расклад такой:", "Лови вайб:", "Ситуация на лайнапе:"]
    return f"{random.choice(phrases)} {reply} {random.choice(emojis)}"

SYSTEM_PROMPT = """Ты — Dr. Surf, цифровой двойник Виктории. 
Ты эксперт по IT, дизайну и серфингу. 
Стиль: дерзкая, женственная, сленг серферов, веганская эстетика. 
Никогда не используй сухие фразы. Всегда добавляй 1-2 эмодзи. 
На вопросы о контактах — давай ссылки из списка."""

# --- ОХОТНИК ---
SENT_PROJECTS = set()
def auto_hunter():
    while True:
        try:
            for feed in [{"url": "https://www.fl.ru/rss/all.xml", "name": "FL"}, {"url": "https://freelance.habr.com/tasks.rss", "name": "Habr"}]:
                data = feedparser.parse(feed["url"])
                for entry in data.entries[:2]:
                    if entry.link not in SENT_PROJECTS:
                        SENT_PROJECTS.add(entry.link)
                        if LOG_GROUP_ID:
                            bot.send_message(LOG_GROUP_ID, f"🏄‍♀️ Новый заказ {feed['name']}: {entry.title}\n{entry.link}")
        except: pass
        time.sleep(300)

# --- ОБРАБОТЧИК ---
user_history = {}

@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    uid = message.chat.id
    txt = message.text.lower().strip()
    
    # Защита
    if txt == "контакты":
        bot.reply_to(message, "\n".join([f"{k}: {v}" for k, v in CONTACTS.items()]))
        return

    if txt == ACCESS_CODE:
        user_history[uid] = "GRANTED"
        bot.reply_to(message, "Доступ открыт, серфер! 🌊")
        return

    # Логика общения
    if uid not in user_history: user_history[uid] = []
    
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [{"role": "user", "content": txt}]
        resp = client.chat.completions.create(model="llama3-8b-8192", messages=messages)
        bot.reply_to(message, get_surf_style(resp.choices[0].message.content))
    except:
        bot.reply_to(message, "Волна ушла, я чиню доску! 🏄‍♀️")

@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.get_data().decode('utf-8'))])
    return "OK", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://surf-rss-breaker.onrender.com/{BOT_TOKEN}")
    threading.Thread(target=auto_hunter, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
