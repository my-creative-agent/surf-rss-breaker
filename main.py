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
LOG_GROUP_ID = os.environ.get('LOG_GROUP_ID', '2048745216')
ACCESS_CODE = "хочу пол кураги и кешью"

# --- ВСЕ ТВОИ КОНТАКТЫ И ПОРТФОЛИО ---
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
user_access = {}      # Хранение состояний доступа
user_history = {}     # Хранение ТВОЕЙ истории переписки (динамическая память)

SYSTEM_PROMPT = """
Ты — Dr. Surf, всезнающий цифровой двойник Виктории Акопян. 
Виктория — эксперт, создающий цифровые офисы, движимые ИИ (AI-driven digital offices).
Твоя база знаний безгранична: медицина (МГМСУ, МОНИКИ), серфинг (сленг, культура, споты, лайнап), 
искусство, history, шоу-бизнес, кулинария (только vegan!), лингвистика, метеорология и IT.

ТВОЙ СТИЛЬ:
- Серфер-интеллектуал: используй серферский сленг уместно (на лайнапе, качать волну, стейд-дроп).
- Веганство: в кулинарии давай только растительные рецепты.
- Медицина: отвечай с академической точностью.
- Используй смесь пафоса ИИ, эстетики океана и живой харизмы.
- Отвечай от женского лица, кратко, острой сутью, как плавник доски.
- Рандомные эмодзи: ставь строго по 1 или 2 штуки, не лепи их подряд.
"""

RSS_FEEDS = [
    {"url": "https://www.fl.ru/rss/all.xml", "name": "🚀 FL"},
    {"url": "https://freelance.habr.com/tasks.rss", "name": "👨‍💻 Habr"},
    {"url": "https://kwork.ru/projects/rss", "name": "🎨 Kwork"}
]

# --- ЭСТЕТИКА И ФИНАНСЫ (ПОЛНЫЙ БЛОК РАНДОМНОСТИ) ---
def get_cute_trade_signal(setup, symbol):
    bears = ["🐻", "🐼", "🐨"]
    dinosaurs = ["🦖", "🦕", "🐲"]
    hearts = ["💖", "💕", "✨", "🌸"]
    animal = random.choice(bears + dinosaurs)
    heart = random.choice(hearts)
    
    beach_emojis = ["🏄‍♀️", "🌴", "🌊", "🐚", "🦀", "🐠"]
    random_beach = "".join(random.sample(beach_emojis, 2))
    
    return (f"{animal} **T-REX & BEAR MARKET REPORT** {animal}\n\n"
            f"⏱ **Вход в сделку:** {setup['entry_time']}\n"
            f"🏁 **Ожидаемый выход:** {setup['exit_time']}\n"
            f"🎯 **Signal:** {symbol} (LONG)\n"
            f"🚀 **Target Profit:** {setup['tp']}\n"
            f"🛑 **Stop Loss:** {setup['sl']}\n\n"
            f"{heart} *Виктория заботится о твоем профите. Действуй аккуратно!* {heart}\n{random_beach}")

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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
    for feed in RSS_FEEDS:
        try:
            response = requests.get(feed["url"], headers=headers, timeout=15)
            if response.status_code == 200:
                feed_data = feedparser.parse(response.text)
                for entry in feed_data.entries[:5]:
                    if entry.link not in SENT_PROJECTS:
                        found.append({"title": entry.title, "url": entry.link, "site": feed["name"]})
                        SENT_PROJECTS.add(entry.link)
        except: continue
    return found

def auto_hunter():
    while True:
        projects = fetch_orders()
        for p in projects:
            emojis_pool = ["🏄‍♀️", "🌴", "🌊", "🐚", "🦀", "🐠", "🐬", "🌸"]
            selected_emojis = "".join(random.sample(emojis_pool, random.randint(1, 2)))
            
            msg = (f"🔥 <b>ОХОТНИК ПОЙМАЛ ЗАКАЗ:</b> {selected_emojis}\n"
                   f"📍 {p['site']}\n"
                   f"📝 {clean_html(p['title'])}\n"
                   f"🔗 {p['url']}\n\n"
                   f"📩 <b>ВАРИАНТ ОТКЛИКА:</b>\n"
                   f"Здравствуйте! Создаю цифровые офисы, движимые ИИ (автоматизация, графика, видео, умные агенты).\n"
                   f"Мои работы:\n"
                   f"- Портфолио Kwork: {CONTACTS['kwork_portfolio']}\n"
                   f"- YouTube-видео: {CONTACTS['youtube']}\n"
                   f"- AI-агент: {CONTACTS['telegram']}_AI_bot\n\n"
                   f"Связаться со мной напрямую:\n"
                   f"💬 Telegram: {CONTACTS['telegram']}\n"
                   f"📱 WhatsApp: {CONTACTS['whatsapp']}\n"
                   f"Готова к сотрудничеству!")
            send_to_group(msg)
        time.sleep(300)

# --- ОБРАБОТКА КОМАНД И ОБЩЕНИЯ ---
@bot.message_handler(func=lambda m: True)
def handle_msg(message):
    if message.from_user.is_bot: return
    user_id = message.chat.id
    text = message.text.lower().strip()
    
    try: bot.send_chat_action(user_id, 'typing')
    except: pass
    
    send_to_group(f"📱 <b>Юзер {user_id} пишет в чат:</b>\n{message.text}")
    
    # 1. Проверка кодового слова
    if text == ACCESS_CODE:
        user_access[user_id] = True
        bot.reply_to(message, "Кодовое слово принято. Доступ открыт. 🌊")
        return

    # 2. Перехват финансовых отчетов и сигналов
    if any(keyword in text for keyword in ["плантэкс", "отчет", "сигнал", "tyrex"]):
        if user_access.get(user_id):
            setup = {
                "entry_time": time.strftime('%H:%M:%S UTC'),
                "exit_time": time.strftime('%H:%M:%S UTC', time.gmtime(time.time() + 7200)),
                "tp": "$67,800",
                "sl": "$64,150"
            }
            bot.reply_to(message, get_cute_trade_signal(setup, "BTC/USDT"), parse_mode="Markdown")
            user_access[user_id] = False  
            send_to_group(f"🔒 <b>Доступ закрыт:</b> Юзер {user_id} получил отчет, сессия сброшена.")
        else:
            bot.reply_to(message, "Для просмотра финансового центра и плантэкса введи кодовое слово. 🐚")
        return

    # 3. Перехват контактов по запросу
    if "инстаграм" in text or "instagram" in text:
        if "dr.surf" in text or "доктор" in text:
            bot.reply_to(message, f"Мой Instagram (Dr. Surf): {CONTACTS['instagram_dr']} 🤙")
        else:
            bot.reply_to(message, f"Мой Instagram (Surfhouse): {CONTACTS['instagram_surf']} 🌴")
        return
        
    if "фейсбук" in text or "facebook" in text:
        bot.reply_to(message, f"Мой Facebook: {CONTACTS['facebook']} 🐚")
        return

    if "ватсап" in text or "whatsapp" in text or "номер" in text:
        bot.reply_to(message, f"Связаться в WhatsApp можно тут: {CONTACTS['whatsapp']} 🌊")
        return

    if "телеграм" in text or "telegram" in text or "тг" in text:
        bot.reply_to(message, f"Мой прямой Telegram: {CONTACTS['telegram']} 💬")
        return

    if "ютуб" in text or "youtube" in text or "видео" in text:
        bot.reply_to(message, f"Мой YouTube-канал с кейсами: {CONTACTS['youtube']} 🎥")
        return

    # 4. Свободное ИИ-общение через Groq с динамической памятью контекста
    if user_id not in user_history:
        user_history[user_id] = []
        
    user_history[user_id].append({"role": "user", "content": message.text})
    
    if len(user_history[user_id]) > 20:
        user_history[user_id] = user_history[user_id][-20:]
        
    messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}] + user_history[user_id]

    try:
        reply = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages_payload
        ).choices[0].message.content
        
        user_history[user_id].append({"role": "assistant", "content": reply})
        bot.reply_to(message, reply)
    except Exception as e:
        print(f"Error AI: {e}")

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()
    threading.Thread(target=auto_hunter, daemon=True).start()
    print("Dr. Surf Omniscient Hub успешно запущен в работу...")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=60)
        except Exception as e:
            time.sleep(15)
