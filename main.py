from flask import Flask, request, jsonify
from transformers import MarianMTModel, MarianTokenizer
import torch

app = Flask(__name__)

# Загружаем модель и токенизатор (казахский -> русский)
model_name = 'Helsinki-NLP/opus-mt-ru-kk'  # Используем правильную модель
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

# Маршрут API для перевода текста
@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data.get('text', '')

    if text:
        # Переводим текст
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            translated = model.generate(**inputs)
        translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
        
        return jsonify({'translation': translated_text})
    else:
        return jsonify({'error': 'No text provided'}), 400

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
