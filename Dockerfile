FROM python:3.10-slim

# Установка зависимостей системы
RUN apt-get update && apt-get install -y gcc libpq-dev && apt-get clean

# Установка рабочей директории
WORKDIR /app

# Копируем зависимости
COPY requirements.txt .

# Установка Python-зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Запуск бота
CMD ["python", "main.py"]
