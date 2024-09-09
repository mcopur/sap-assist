# nlp/src/api/server.py

from nlp.src.utils.chatbot import Chatbot
from flask import Flask, request, jsonify
import sys
import os

# Projenin kök dizinini Python yoluna ekle
project_root = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)


app = Flask(__name__)


def initialize_chatbot():
    model_path = os.path.join(
        project_root, 'nlp', 'models', 'intent_classifier_model')
    le_path = os.path.join(project_root, 'nlp', 'models', 'label_encoder.pkl')
    return Chatbot(model_path, le_path)


chatbot = initialize_chatbot()


@app.route('/classify', methods=['POST'])
def classify():
    app.logger.debug(f"Received request: {request.json}")
    data = request.get_json()
    if not data or 'text' not in data:
        app.logger.error("Invalid request payload")
        return jsonify({"error": "Invalid request payload"}), 400

    user_input = data['text']
    try:
        result = chatbot.process_message(user_input)
        app.logger.debug(f"Sending response: {result}")
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error processing message: {str(e)}")
        return jsonify({"error": "Error processing message"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
