import os
from flask import Flask, request, jsonify
from nlp.src.utils.chatbot import Chatbot
import logging

# Proje kök dizinini belirleme
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..'))

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model yollarını belirleme
intent_model_path = os.path.join(
    PROJECT_ROOT, 'nlp', 'models', 'intent_classifier')
response_model_path = os.path.join(
    PROJECT_ROOT, 'nlp', 'models', 'response_generator')

# Chatbot nesnesini oluşturma
chatbot = Chatbot(intent_model_path, response_model_path)


@app.route('/process', methods=['POST'])
def process_message():
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "Invalid request payload"}), 400

    text = data['text']
    context = data.get('context', {})

    try:
        result = chatbot.process_message(text, context)
        logger.info(f"Processed message: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return jsonify({"error": "Error processing message"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
