from flask import Flask, request, jsonify
from nlp.src.utils.chatbot import process_message
import sys
import os
import logging

# Projenin kök dizinini Python yoluna ekle
project_root = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@app.route('/classify', methods=['POST'])
def classify():
    logger.debug(f"Received request: {request.json}")
    data = request.get_json()
    if not data or 'text' not in data:
        logger.error("Invalid request payload")
        return jsonify({"error": "Invalid request payload"}), 400

    user_input = data['text']
    try:
        intent, confidence, response, entities = process_message(user_input)
        logger.debug(
            f"Process message result: intent={intent}, confidence={confidence}, response={response}, entities={entities}")

        result = {
            "intent": intent,
            "confidence": confidence,
            "response": response,
            "entities": entities
        }
        logger.debug(f"Sending response: {result}")
        return jsonify(result)
    except Exception as e:
        logger.exception(f"Error processing message: {str(e)}")
        return jsonify({"error": "Error processing message"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
