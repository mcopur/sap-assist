from flask import Flask, request, jsonify
from nlp.src.utils.chatbot import initialize_chatbot
import sys
import os

# Projenin kök dizinini Python yoluna ekle
project_root = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

app = Flask(__name__)
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
        intent, confidence, response, entities = chatbot.process_message(
            user_input)

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
