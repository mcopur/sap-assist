# nlp/src/api/server.py

from flask import Flask, request, jsonify
from nlp.src.utils.chatbot import Chatbot
import sys
import os

project_root = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

app = Flask(__name__)
chatbot = Chatbot()


@app.route('/process', methods=['POST'])
def process():
    app.logger.debug(f"Received request: {request.json}")
    data = request.get_json()
    if not data or 'text' not in data:
        app.logger.error("Invalid request payload")
        return jsonify({"error": "Invalid request payload"}), 400

    user_input = data['text']
    context = data.get('context', {})
    try:
        intent, confidence, response, entities = chatbot.process_message(
            user_input, context)

        result = {
            "intent": intent,
            "confidence": confidence,
            "response": response,
            "entities": entities
        }
        app.logger.debug(f"Sending response: {result}")
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error processing message: {str(e)}")
        return jsonify({"error": "Error processing message"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
