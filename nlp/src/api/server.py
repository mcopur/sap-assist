from nlp.src.utils.chatbot import Chatbot
import sys
import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# Projenin kök dizinini Python yoluna ekle
project_root = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)


app = Flask(__name__)
CORS(app)

# Loglama ayarları
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Model yollarını projenin kök dizinine göre belirle
intent_model_path = os.path.join(
    project_root, 'nlp', 'models', 'intent_classifier_model')
response_model_path = os.path.join(
    project_root, 'nlp', 'models', 'response_generator')

# Chatbot nesnesini oluştur
try:
    chatbot = Chatbot(intent_model_path, response_model_path, project_root)
    logger.info("Chatbot başarıyla yüklendi.")
except Exception as e:
    logger.error(f"Chatbot yüklenirken hata oluştu: {str(e)}")
    raise


@app.route('/classify', methods=['POST'])
def classify():
    logger.debug(f"Gelen istek: {request.json}")
    data = request.get_json()
    if not data or 'text' not in data:
        logger.error("Geçersiz istek yapısı")
        return jsonify({"error": "Geçersiz istek yapısı"}), 400

    user_input = data['text']
    try:
        intent, confidence, response, entities = chatbot.process_message(
            user_input)

        result = {
            "intent": intent,
            "confidence": confidence,
            "response": response,
            "entities": entities
        }
        logger.debug(f"Gönderilen yanıt: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Mesaj işlenirken hata oluştu: {str(e)}")
        return jsonify({"error": "Mesaj işlenirken hata oluştu"}), 500


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200


@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Invalid request payload"}), 400

    user_input = data['text']
    try:
        intent, confidence, response, entities = chatbot.process_message(
            user_input)
        result = {
            "intent": intent,
            "confidence": confidence,
            "response": response,
            "entities": entities
        }
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return jsonify({"error": "Error processing message"}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
