import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pickle
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'intent_classifier_model')
label_encoder_path = os.path.join(current_dir, 'label_encoder.pkl')

model = AutoModelForSequenceClassification.from_pretrained(model_path)
model.eval()
tokenizer = AutoTokenizer.from_pretrained(model_path)

with open(label_encoder_path, 'rb') as f:
    le = pickle.load(f)

print(f"Available intents: {le.classes_}")


def classify_intent(text):
    inputs = tokenizer(text, return_tensors="pt",
                       truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    confidence, predicted_class = torch.max(probs, dim=-1)
    intent = le.inverse_transform([predicted_class.item()])[0]
    print(f"Predicted intent: {intent}, Confidence: {confidence.item():.4f}")
    return intent, confidence.item()


def chatbot_response(intent, confidence, user_input):
    if confidence < 0.6:  # Eşik değerini artırdık
        if "arası" in user_input.lower() or "arasında" in user_input.lower():
            return "Anladım, bu tarihleri yıllık izin talebi olarak kaydediyorum. Başka bir isteğiniz var mı?"
        else:
            return "Üzgünüm, ne demek istediğinizi tam olarak anlayamadım. Lütfen başka bir şekilde ifade eder misiniz?"

    if intent == 'greeting':
        return "Merhaba! Size nasıl yardımcı olabilirim?"
    elif intent == 'leave_request_annual':
        return "Yıllık izin talebiniz için tarihleri alabilir miyim? Örneğin: 01.08.2024 ve 05.08.2024 arası"
    elif intent == 'leave_request_excuse':
        return "Mazeret izni talebiniz için tarih ve saatleri alabilir miyim? Örneğin: 05.08.2024 tarihi 09:30-11:30 arası"
    elif intent == 'purchase_request':
        return "Satın alma talebiniz için hangi ürünü veya hizmeti talep etmek istiyorsunuz?"
    elif intent == 'confirm_annual_leave':
        return "Yıllık izin talebinizi aldım. Bu tarihleri kaydediyorum. Onay için yöneticinize ileteceğim. Başka bir isteğiniz var mı?"
    elif intent == 'confirm_excuse_leave':
        return "Mazeret izni talebinizi aldım. Bu tarihleri kaydediyorum. Onay için yöneticinize ileteceğim. Başka bir isteğiniz var mı?"
    elif intent == 'end_conversation':
        return "Anladım. Başka bir isteğiniz yoksa, size iyi günler dilerim. Yardıma ihtiyacınız olursa tekrar buradayım!"
    else:
        return "Üzgünüm, bu tür bir talebi şu anda işleyemiyorum. Lütfen başka bir şekilde ifade etmeyi deneyin."


# print("Chatbot: Merhaba! Size nasıl yardımcı olabilirim?")

# while True:
#    user_input = input("Siz: ")
#    if user_input.lower() == 'çıkış':
#        print("Chatbot: Görüşmek üzere!")
#        break

#    intent, confidence = classify_intent(user_input)
#    response = chatbot_response(intent, confidence, user_input)
#    print(f"Chatbot: {response}")

#    if intent == 'end_conversation':
#        print("Chatbot: İyi günler! Başka bir sorunuz olursa yardımcı olmaktan memnuniyet duyarım.")
#        break
