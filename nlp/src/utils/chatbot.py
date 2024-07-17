import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pickle

# Load the model and tokenizer
model_name = "./intent_classifier_model"
model = AutoModelForSequenceClassification.from_pretrained(model_name)
model.eval()  # Modeli değerlendirme moduna al
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Load the label encoder
with open('label_encoder.pkl', 'rb') as f:
    le = pickle.load(f)

# Etiketleri yazdır
print(f"Available intents: {le.classes_}")


def classify_intent(text):
    inputs = tokenizer(text, return_tensors="pt",
                       truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    predicted_class = torch.argmax(probs, dim=-1).item()
    intent = le.inverse_transform([predicted_class])[0]
    print(f"Predicted intent: {intent}")  # Debug print
    return intent


def chatbot_response(intent):
    if intent == 'greeting':
        return "Merhaba! Size nasıl yardımcı olabilirim?"
    elif intent == 'leave_request_annual':
        return "Yıllık izin talebiniz için tarihleri alabilir miyim? Örneğin: 01.08.2024 ve 05.08.2024 arası"
    elif intent == 'leave_request_excuse':
        return "Mazeret izni talebiniz için tarih ve saatleri alabilir miyim? Örneğin: 05.08.2024 tarihi 09:30-11:30 arası"
    elif intent == 'purchase_request':
        return "Satın alma talebiniz için hangi ürünü veya hizmeti talep etmek istiyorsunuz?"
    elif intent == 'confirm_annual_leave':
        return "Yıllık izin talebinizi aldım. Onay için yöneticinize ileteceğim. Başka bir isteğiniz var mı?"
    elif intent == 'confirm_excuse_leave':
        return "Mazeret izni talebinizi aldım. Onay için yöneticinize ileteceğim. Başka bir isteğiniz var mı?"
    else:
        return "Üzgünüm, bu tür bir talebi şu anda işleyemiyorum. Lütfen başka bir şekilde ifade etmeyi deneyin."


print("Chatbot: Merhaba! Size nasıl yardımcı olabilirim?")

while True:
    user_input = input("Siz: ")
    if user_input.lower() == 'çıkış':
        print("Chatbot: Görüşmek üzere!")
        break

    intent = classify_intent(user_input)
    response = chatbot_response(intent)
    print(f"Chatbot: {response}")
