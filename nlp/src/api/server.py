from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from nlp.src.utils.chatbot import Chatbot
import os
import sys
import logging
from flask_talisman import Talisman

# Projenin kök dizinini Python yoluna ekle
project_root = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

app = Flask(__name__)
CORS(app, resources={
     r"/classify": {"origins": "http://localhost:5173"}}, supports_credentials=True)
Talisman(app, content_security_policy=None)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",  # In-memory storage kullanıyoruz
    headers_enabled=True
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_chatbot():
    model_path = os.path.join(
        project_root, 'nlp', 'models', 'intent_classifier_model')
    le_path = os.path.join(project_root, 'nlp', 'models', 'label_encoder.pkl')

    if not os.path.exists(model_path):
        logger.error(f"Model path does not exist: {model_path}")
        return None

    if not os.path.exists(le_path):
        logger.error(f"Label encoder path does not exist: {le_path}")
        return None

    return Chatbot(model_path, le_path)


chatbot = initialize_chatbot()


@app.route('/classify', methods=['POST'])
@limiter.limit("30 per minute")  # Hız sınırlaması eklendi
def classify():
    if chatbot is None:
        return jsonify({"error": "Chatbot initialization failed"}), 500

    logger.info(f"Received request: {request.json}")
    data = request.get_json()
    if not data or 'text' not in data:
        logger.error("Invalid request payload")
        return jsonify({"error": "Invalid request payload"}), 400

    user_input = data['text']
    try:
        result = chatbot.process_message(user_input)
        logger.info(f"Sending response: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return jsonify({"error": "Error processing message"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
