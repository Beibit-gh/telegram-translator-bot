import os
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, Update
from transformers import MarianTokenizer, MarianMTModel
import torch

model_name = 'Helsinki-NLP/opus-mt-kk-ru'
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

def translate(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        translated = model.generate(**inputs)
    return tokenizer.decode(translated[0], skip_special_tokens=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    original_text = update.message.text
    translated_text = translate(original_text)
    await update.message.reply_text(translated_text)

if __name__ == '__main__':
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Бот запущен...")
    app.run_polling()