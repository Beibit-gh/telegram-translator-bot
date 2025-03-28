import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, MessageHandler, CommandHandler, ContextTypes, filters
import openai
import asyncio

# Настройки
openai.api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MODEL_NAME = "ft:gpt-3.5-turbo-1106:personal:firstbig:BG1zioJE"
SYSTEM_PROMPT = (
    "You are a professional translator from Kazakh, Turkish, and English to Russian. "
    "Always translate precisely and naturally. No additions. No omissions."
)

# Инициализация Flask и Telegram
app = Flask(__name__)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = Dispatcher(bot=bot, update_queue=None)

# Обработка текста
def split_text_smart(text, max_chars=1000):
    chunks = []
    current_chunk = ""

    while len(text) > max_chars:
        split_point = text.rfind(" ", 0, max_chars)
        if split_point == -1:
            split_point = max_chars
        chunks.append(text[:split_point].strip())
        text = text[split_point:].strip()

    if text:
        chunks.append(text)

    return chunks

async def translate_text_with_progress(text: str, update: Update) -> str:
    parts = split_text_smart(text)
    translated_parts = []

    for i, part in enumerate(parts):
        await update.message.reply_text(f"Перевод части {i + 1} из {len(parts)}...")

        try:
            response = openai.ChatCompletion.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": part}
                ],
                temperature=0.3,
            )
            translated = response["choices"][0]["message"]["content"].strip()
            translated_parts.append(translated)

        except Exception as e:
            await update.message.reply_text(f"Ошибка перевода: {str(e)}")

    return "\n".join(translated_parts)

# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Отправьте мне текстовый файл на казахском, турецком или английском языках, и я переведу его на русский."
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    content = await file.download_as_bytearray()
    text = content.decode("utf-8")

    translated_text = await translate_text_with_progress(text, update)

    if translated_text:
        output_path = "translated_result.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(translated_text)

        with open(output_path, "rb") as f:
            await update.message.reply_document(f, filename="translated_result.txt")

        os.remove(output_path)

# Роутинг webhook
@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

# Запуск сервера Flask
if __name__ == "__main__":
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)
