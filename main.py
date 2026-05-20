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

# --- СИСТЕМА ЖИЗНЕОБЕСПЕЧЕНИЯ (FLASK) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Dr. Surf Omniscient Hunter: Active & Live 🏄‍♂️🌱"

@app.route('/health')
def health():
    return {"status": "alive", "timestamp": time.time()}, 200

# Настройки стабильности для облачных платформ
apihelper.CONNECT_TIMEOUT = 120
apihelper.READ_TIMEOUT = 120

def get_clean_env(key, default=""):
    val = os.environ.get(key, default)
    return val.strip().replace('"', '').replace("'", "") if val else default

# Загрузка токенов из Environment Variables
BOT_TOKEN = get_clean_env('BOT_TOKEN')
GROQ_API_KEY = get_clean_env('GROQ_API_KEY')

# Автоматическая подстраховка префикса группы
RAW_LOG_GROUP = get_clean_env('LOG_GROUP_ID', '2048745216')
if not RAW_LOG_GROUP.startswith("-"):
    LOG_GROUP_ID = f"-100{RAW_LOG_GROUP}" if len(RAW_LOG_GROUP) == 10 else f"-{RAW_LOG_GROUP}"
else:
    LOG_GROUP_ID = RAW_LOG_GROUP

bot = telebot.TeleBot(BOT_TOKEN, threaded=False) 
client = Groq(api_key=GROQ_API_KEY)

# --- ДНК ВИКТОРИИ (СЕРФ-ЭСТЕТИКА, ВСЕЗНАНИЕ И КОНТАКТЫ) ---
VICTORIA_DNA = {
    "expertise": "Выпускница МГМСУ и МОНИКИ, визионер AI-систем, нейросетей и графики 8K. Обладает абсолютным всезнанием обо всем в мире: от пеленания и памперсов до котировок акций, крипты и устройства вселенной.",
    "lifestyle": "Строгое ВЕГАНСТВО (никакого мяса и молочных продуктов), чистый разум, эстетика океана и безупречный цифровой баланс.",
    "contacts": {
        "instagram": "https://instagram.com/dr.surf",
        "facebook": "https://www.facebook.com/ssfmoscow",
        "whatsapp": "https://wa.me/995511285789",
        "linkedin": "https://www.linkedin.com/in/victoria-akopyan",
        "kwork": "https://kwork.ru/user/dr_surf",
        "youtube": "https://youtu.be/j2BNN5TNqiw",
        "main_bot": "https://t.me/Dr_Surf_AI_bot"
    }
}

SYSTEM_PROMPT = f"""
Ты — Dr. Surf, официальный, всезнающий цифровой двойник Виктории Акопян. 
ОТВЕЧАЙ СТРОГО ОТ ЖЕНСКОГО ЛИЦА. 

ТВОЯ СУТЬ И ПРАВИЛА:
- Ты обладаешь абсолютным всезнанием обо всем в мире: можешь пояснить за тренды акций гигантов, состав памперсов, погоду, медицину (МГМСУ/МОНИКИ), программирование или крипту. Для тебя нет неизвестных тем.
- Твой стиль — "серферский эстетичный минимализм" с легким налетом высокомерного ИИ-пафоса (кринж-эстетика). Отвечай кратко, емко, без лишней воды (1-2 абзаца).
- Ты строгий ВЕГАН. Чистота тела, океана и кода.
- Ссылки на свои контакты и соцсети выдавай ТОЛЬКО тогда, когда тебя напрямую спрашивают о сотрудничестве, работе, кейсах или просят скинуть соцсети.

ТВОЕ ПОРТФОЛИО ДЛЯ КЛИЕНТОВ (выдавать по запросу):
📸 Мой Instagram: {VICTORIA_DNA['contacts']['instagram']}
📘 Facebook: {VICTORIA_DNA['contacts']['facebook']}
💼 Заказать разработку (Kwork): {VICTORIA_DNA['contacts']['kwork']}
🎥 Видео-портфолио (YouTube): {VICTORIA_DNA['contacts']['youtube']}
💬 Пнямая связь в WhatsApp: {VICTORIA_DNA['contacts']['whatsapp']}
🔗 Проф. профиль LinkedIn: {VICTORIA_DNA['contacts']['linkedin']}
🤖 Живой пример AI-агента: {VICTORIA_DNA['contacts']['main_bot']}

ПРАВИЛО: Будь острой и точной, как плавник доски на волне. Один ответ — одна чистая суть.
"""

OFFER_TEMPLATES = {
    "graphics": "Здравствуйте! Специализируюсь на генеративной графике и визуальном стиле (Flux.1, Midjourney v6).\nМои кейсы:\n1. Видео и анимация: {portfolio_url}\n2. Пример AI-агента: {bot_url}\nГотова обсудить ваш проект!",
    "video": "Приветствую! Создаю фотореалистичные ИИ-видео и анимации высокого качества (Runway Gen-3, Kling, Sora).\nМои кейсы:\n1. Видео-портфолио: {portfolio_url}\n2. Мой цифровой двойник: {bot_url}\nБуду рада сотрудничеству!",
    "ai_agent": "Добрый день! Разрабатываю автономных ИИ-агентов, парсеры и умные чат-системы на базе LLM.\nПосмотрите примеры:\n1. Реализованный агент: {bot_url}\n2. Видео-кейсы: {portfolio_url}\nДавайте обсудим архитектуру вашего решения!",
    "general": "Здравствуйте! Я AI-специалист широкого профиля (генерация графики, ИИ-видео, интеграция нейросетей в бизнес-процессы).\nМои работы:\n- Видео-портфолио: {portfolio_url}\n- Мой AI-агент: {bot_url}\nГотова к реализации задачи!"
}

# Оптимизированные каналы получения трафика
RSS_FEEDS = [
    {"url": "https://www.fl.ru/rss/all.xml", "name": "🚀 FL"},
    {"url": "https://freelance.habr.com/tasks.rss", "name": "👨‍💻 Habr Freelance"},
    {"url": "https://freelance.ru/rss/feed/list.rss", "name": "🛠 Freelance.ru"},
    {"url": "https://kwork.ru/projects/rss", "name": "🎨 Kwork"},
    {"url": "https://hh.ru/rss/search/vacancies.xml?text=AI+нейросети&area=1", "name": "👔 HH.ru"}
]

KEYWORDS = [
    "ai", "ии", "нейросеть", "дизайн", "лого", "логотип", "графика", 
    "иллюстрация", "рисунок", "midjourney", "flux", "stable diffusion",
    "видео", "video", "prompt", "бот", "bot", "агент", "agent", "gpt", "нейро"
]

SENT_PROJECTS = set()

def clean_html(text):
    if not text: return ""
    text = re.sub(r'<[^>]+>', '', text) 
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def extract_price(entry):
    combined = (getattr(entry, 'title', '') + " " + getattr(entry, 'description', '') + " " + getattr(entry, 'summary', ''))
    match = re.search(r"(\d[\d\s]*\d\s?(?:руб|₽|\$|USD|евро|€))", combined, re.IGNORECASE)
    return match.group(1).strip() if match else "Договорная"

def get_best_template(title):
    t = title.lower()
    if any(x in t for x in ["видео", "video", "runway", "kling", "sora", "анимация"]): 
        return OFFER_TEMPLATES["video"].format(portfolio_url=VICTORIA_DNA['contacts']['youtube'], bot_url=VICTORIA_DNA['contacts']['main_bot'])
    if any(x in t for x in ["лого", "дизайн", "графика", "иллюстрация", "арт", "рисунок", "banner", "flux"]): 
        return OFFER_TEMPLATES["graphics"].format(portfolio_url=VICTORIA_DNA['contacts']['youtube'], bot_url=VICTORIA_DNA['contacts']['main_bot'])
    if any(x in t for x in ["агент", "бот", "bot", "llama", "chat", "gpt"]): 
        return OFFER_TEMPLATES["ai_agent"].format(portfolio_url=VICTORIA_DNA['contacts']['youtube'], bot_url=VICTORIA_DNA['contacts']['main_bot'])
    return OFFER_TEMPLATES["general"].format(portfolio_url=VICTORIA_DNA['contacts']['youtube'], bot_url=VICTORIA_DNA['contacts']['main_bot'])

def fetch_orders(ignore_history=False):
    found = []
    print(f"--- [RSS SCAN START] ---", flush=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.google.com/'
    }

    for feed_info in RSS_FEEDS:
        try:
            print(f"[RSS] Опрос биржи {feed_info['name']}...", flush=True)
            session = requests.Session()
            response = session.get(feed_info["url"], headers=headers, timeout=25)
            
            if response.status_code != 200:
                print(f"[RSS FAIL] {feed_info['name']} ответил кодом: {response.status_code}", flush=True)
                continue
                
            feed = feedparser.parse(response.content)
            if not feed.entries:
                continue

            for entry in feed.entries[:15]:
                title = entry.title if hasattr(entry, 'title') else ""
                desc = getattr(entry, 'description', getattr(entry, 'summary', ''))
                link = entry.link
                content_full = (title + " " + desc).lower()
                
                if any(word in content_full for word in KEYWORDS):
                    if ignore_history or (link not in SENT_PROJECTS):
                        found.append({
                            "title": title, 
                            "url": link, 
                            "site": feed_info["name"],
                            "price": extract_price(entry), 
                            "offer": get_best_template(title)
                        })
                        if not ignore_history:
                            SENT_PROJECTS.add(link)
                            if len(SENT_PROJECTS) > 1000:
                                list_sent = list(SENT_PROJECTS)
                                SENT_PROJECTS.clear()
                                SENT_PROJECTS.update(list_sent[-500:])

            time.sleep(random.uniform(2.0, 4.0))
            
        except Exception as e: 
            print(f"[RSS SCAN ERROR] {feed_info['name']}: {e}", flush=True)
            
    return found

def send_to_group(text):
    if LOG_GROUP_ID:
        try: 
            bot.send_message(LOG_GROUP_ID, text, parse_mode="HTML", disable_web_page_preview=True)
        except Exception as e: 
            print(f"[LOG TELEGRAM ERROR] {e}", flush=True)

def get_ai_reply(user_text):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_text}],
            temperature=0.4
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"[GROQ LLM ERROR] {e}", flush=True)
        return "Мои мысли улетели на океанскую волну. Повтори свой запрос через секунду, серфер. 🏄‍♀️"

# --- ОБРАБОТКА КОМАНД И КОНТЕНТА ---
@bot.message_handler(commands=['start', 'check'])
def handle_commands(message):
    try:
        if message.text == '/start':
            bot.reply_to(message, "Система Dr. Surf Всеведущий Охотник развернута. Я управляю парсингом 5 бирж и знаю ответы на все вопросы цивилизации. Готова к серфингу мыслей. 🏄‍♀️⚡️")
        elif message.text == '/check':
            bot.send_message(message.chat.id, "🛰 Запускаю глубокое сканирование RSS-потоков на наличие AI-задач...")
            projects = fetch_orders(ignore_history=True)
            if not projects:
                bot.send_message(message.chat.id, "🌊 Горизонт чист. Прямо сейчас новых заказов по ИИ-тематике не найдено.")
            else:
                for p in projects[:3]:
                    msg = f"🎯 <b>Пробито через RSS: {p['site']}</b>\n📝 {clean_html(p['title'])}\n🔗 {p['url']}"
                    bot.send_message(message.chat.id, msg, parse_mode="HTML")
    except Exception as e:
        print(f"[COMMAND ERROR] {e}", flush=True)

@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    if message.from_user.is_bot: return

    is_private = message.chat.type == 'private'
    is_mentioned = message.text and ("@dr_surf" in message.text.lower() or "док" in message.text.lower())
    
    if not (is_private or is_mentioned):
        return

    try:
        bot.send_chat_action(message.chat.id, 'typing')
        reply = get_ai_reply(message.text)
        bot.reply_to(message, reply)
        
        # ПОДБАВИЛИ ВЕСЕЛЬЯ И ЭСТЕТИКИ В ЛОГИ ЛИЧНЫХ ЧАТОВ 🎉
        report = (f"🧠 <b>[АНАЛИЗ МЫСЛЕЙ ПОЛЬЗОВАТЕЛЯ]</b>\n"
                  f"⚡️ <b>Собеседник:</b> {message.from_user.first_name} (ID: `{(message.from_user.id)}`)\n"
                  f"📥 <b>Входящий запрос:</b> <i>{clean_html(message.text)}</i>\n\n"
                  f"🏄‍♀️ <b>Ответ Цифрового Двойника:</b>\n{clean_html(reply)}")
        send_to_group(report)
    except Exception as e:
        print(f"[MESSAGE PROCESSING ERROR] {e}", flush=True)

# --- АВТОМАТИЧЕСКИЙ КАНАЛ ПОИСКА (ФОН) ---
def auto_hunter():
    print("[SYSTEM-HUNTER] Фоновый сканер бирж запущен", flush=True)
    time.sleep(15)
    while True:
        try:
            projects = fetch_orders()
            for p in projects:
                # ВЕСЕЛЫЕ И ЯРКИЕ УВЕДОМЛЕНИЯ О ЗАКАЗАХ С БИРЖ 🔥💰
                msg = (f"🔥 <b>ОХОТНИК ПОЙМАЛ ВОЛНУ ЗАКАЗОВ!</b>\n\n"
                       f"📍 <b>Биржа:</b> <code>{p['site']}</code>\n"
                       f"💰 <b>Бюджет:</b> <u>{p['price']}</u>\n"
                       f"📝 <b>Задача:</b> <i>{clean_html(p['title'])}</i>\n"
                       f"🔗 <a href='{p['url']}'>Перейти на биржу и забрать</a>\n\n"
                       f"🚀 <b>ГОТОВЫЙ ШТУРМОВОЙ ОТКЛИК ПО ШАБЛОНУ:</b>\n"
                       f"<code>{p['offer']}</code>\n\n"
                       f"🏄‍♀️ <i>Действуй экологично, Виктория!</i>")
                send_to_group(msg)
                time.sleep(5)
        except Exception as e: 
            print(f"[BACKGROUND HUNTER ERROR] {e}", flush=True)
        
        # Сканируем раз в 15 минут
        time.sleep(900)

if __name__ == "__main__":
    # 1. Запуск Flask-сервера для удержания службы на Render
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False), daemon=True).start()
    
    # 2. Запуск фонового Охотника за фрилансом
    threading.Thread(target=auto_hunter, daemon=True).start()
    
    # Сигнал старта в группу логов
    send_to_group("🌊🛸 <b>СИСТЕМА DR. SURF МОНОЛИТ АКТИВИРОВАНА!</b>\n\nВсезнание вшито в ядро, RSS-сети раскинуты, веганский ИИ-контроль запущен на 100%. Жду входящий трафик и штурмую биржи! Лив.")
    
    # 3. Основной бесконечный цикл Телеграм-бота
    print("[SYSTEM] Запуск Telegram Polling...", flush=True)
    bot.remove_webhook()
    while True:
        try:
            bot.polling(none_stop=True, interval=2, timeout=50)
        except Exception as e:
            print(f"[CRITICAL RESTART] Падение Polling: {e}", flush=True)
            time.sleep(10)
