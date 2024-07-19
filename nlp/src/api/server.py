from flask import Flask, request, jsonify
from src.utils.chatbot import classify_intent, chatbot_response

app = Flask(__name__)


@app.route('/classify', methods=['POST'])
def classify():
    data = request.get_json()
    user_input = data.get('text')
    intent, confidence = classify_intent(user_input)
    response = chatbot_response(intent, confidence, user_input)
    return jsonify({"intent": intent, "confidence": confidence, "response": response})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
