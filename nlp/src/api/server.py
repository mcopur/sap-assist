from flask import Flask, request, jsonify
from nlp.src.utils.chatbot import process_message
from nlp.src.utils.data_augmentation import augment_data, load_data, save_data
import logging
import os

app = Flask(__name__)

# Logging ayarları
logging.basicConfig(level=logging.DEBUG)
logger = app.logger


@app.route('/classify', methods=['POST'])
def classify():
    data = request.get_json()
    logger.debug(f"Received request: {data}")

    if not data or 'text' not in data:
        logger.error("Invalid request payload")
        return jsonify({"error": "Invalid request payload"}), 400

    user_input = data['text']
    try:
        intent, confidence, response, entities = process_message(user_input)
        result = {
            "intent": intent,
            "confidence": confidence,
            "response": response,
            "entities": entities
        }
        logger.debug(f"Sending response: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return jsonify({"error": "Error processing message"}), 500


@app.route('/augment_data', methods=['POST'])
def augment_data_endpoint():
    try:
        project_root = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', '..'))
        input_path = os.path.join(
            project_root, 'nlp', 'data', 'augmented_intent_data.json')
        output_path = os.path.join(
            project_root, 'nlp', 'data', 'enriched_intent_data.json')

        data = load_data(input_path)
        augmented_data = augment_data(data)
        save_data(augmented_data, output_path)

        logger.info(
            f"Data augmentation completed. Enriched data saved to {output_path}")
        return jsonify({"message": "Data augmentation completed successfully"}), 200
    except Exception as e:
        logger.error(f"Error during data augmentation: {str(e)}")
        return jsonify({"error": "Error during data augmentation"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
