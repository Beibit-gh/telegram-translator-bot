
from flask import Flask, request, jsonify
from transformers import MarianMTModel, MarianTokenizer
import torch

# Инициализация Flask
app = Flask(__name__)

# Загрузка модели и токенизатора для перевода
model_name = 'Helsinki-NLP/opus-mt-kk-ru'  # Это для казахского на русский
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

def translate(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        translated = model.generate(**inputs)
    return tokenizer.decode(translated[0], skip_special_tokens=True)

@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.get_json()
    text = data.get("text", "")
    if text:
        translated_text = translate(text)
        return jsonify({"translated_text": translated_text})
    return jsonify({"error": "No text provided"}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
