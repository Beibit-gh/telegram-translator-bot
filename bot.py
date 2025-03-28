
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
import requests

# Токен бота
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Адрес Flask API
FLASK_API_URL = "https://kz2ru-telegram-bot-cd858c0d93cf.herokuapp.com/translate"  # Заменить на адрес вашего Heroku приложения

async def start(update: Update, context):
    await update.message.reply_text("Привет! Отправьте мне текст для перевода.")

async def handle_message(update: Update, context):
    original_text = update.message.text
    response = requests.post(FLASK_API_URL, json={"text": original_text})
    
    if response.status_code == 200:
        translated_text = response.json().get("translated_text", "")
        await update.message.reply_text(translated_text)
    else:
        await update.message.reply_text("Ошибка при переводе.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Бот запущен...")
    app.run_polling()
