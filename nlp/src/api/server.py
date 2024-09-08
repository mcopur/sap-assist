from nlp.src.utils.chatbot import Chatbot
from flask import Flask, request, jsonify
import sys
import os
import logging

project_root = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)


app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

intent_model_path = os.path.join(
    project_root, 'nlp', 'models', 'intent_classifier_model')
response_model_path = os.path.join(
    project_root, 'nlp', 'models', 'response_generator')

try:
    chatbot = Chatbot(intent_model_path, response_model_path)
    logger.info("Chatbot başarıyla yüklendi.")
except Exception as e:
    logger.error(f"Chatbot yüklenirken hata oluştu: {str(e)}")
    raise


@app.route('/process', methods=['POST'])
def process():
    logger.debug(f"Received request: {request.json}")
    data = request.get_json()
    if not data or 'text' not in data:
        logger.error("Invalid request payload")
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
        logger.debug(f"Sending response: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        return jsonify({"error": "Error processing message", "details": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
