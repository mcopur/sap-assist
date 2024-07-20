from flask import Flask, request, jsonify
from src.utils.chatbot import classify_intent, chatbot_response

app = Flask(__name__)


def send_leave_request(personnel_number, start_date, end_date):
    url = "https://10.1.4.21:44300/sap/opu/odata/sap/ZCXP_LEAVE_REQUEST_SRV/LEAVE_REQUESTSet"
    headers = {
        "Content-Type": "application/json",
        "X-CSRF-TOKEN": "FETCH"
    }
    payload = {
        "d": {
            "PersonnelNumber": personnel_number,
            "StartDate": start_date,
            "EndDate": end_date,
            "RequestId": "0AA94D873C191EDAA6B96F42599EEB77"
        }
    }
    response = requests.put(url, json=payload, headers=headers)
    return response.json()


@app.route('/classify', methods=['POST'])
def classify():
    data = request.get_json()
    user_input = data.get('text')
    intent, confidence = classify_intent(user_input)
    response_message = chatbot_response(intent, confidence, user_input)

    if intent == 'confirm_annual_leave':
        # SAP Leave Request işlemi
        personnel_number = "00000029"
        start_date = "2024-08-01"
        end_date = "2024-08-05"
        leave_response = send_leave_request(
            personnel_number, start_date, end_date)
        response_message += f"\nLeave Request Response: {leave_response}"

    return jsonify({"intent": intent, "confidence": confidence, "response": response_message})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
