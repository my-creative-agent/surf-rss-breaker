# Используем стабильную версию Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем всё содержимое папки проекта в контейнер
COPY . .

# Устанавливаем библиотеки
RUN pip install --no-cache-dir -r requirements.txt

# Указываем порт 10000 (должен совпадать с кодом в main.py)
EXPOSE 10000

# Запускаем бота
CMD ["python", "main.py"]
