import os
import torch
import pickle
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForCausalLM


class Chatbot:
    def __init__(self, intent_model_path, response_model_path, project_root):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")

        # Intent model
        self.intent_tokenizer = AutoTokenizer.from_pretrained(
            intent_model_path, local_files_only=True)
        self.intent_model = AutoModelForSequenceClassification.from_pretrained(
            intent_model_path, local_files_only=True).to(self.device)

        # Response model
        self.response_tokenizer = AutoTokenizer.from_pretrained(
            response_model_path, local_files_only=True)
        self.response_model = AutoModelForCausalLM.from_pretrained(
            response_model_path, local_files_only=True).to(self.device)

        # Label encoder'ı yükle
        label_encoder_path = os.path.join(
            project_root, 'nlp', 'models', 'label_encoder.pkl')
        with open(label_encoder_path, 'rb') as f:
            self.label_encoder = pickle.load(f)

    def process_message(self, text):
        # Metin ön işleme
        preprocessed_text = preprocess_text(text)

        # Intent sınıflandırma
        inputs = self.intent_tokenizer(
            preprocessed_text, return_tensors="pt", truncation=True, padding=True).to(self.device)
        with torch.no_grad():
            outputs = self.intent_model(**inputs)

        logits = outputs.logits
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        confidence, predicted_class = torch.max(probabilities, dim=-1)

        intent = self.label_encoder.inverse_transform(
            [predicted_class.item()])[0]
        confidence = confidence.item()

        # Entity extraction
        entities = extract_entities(text)

        # Response generation
        response = self.generate_response(intent, entities, text)

        return intent, confidence, response, entities

    def generate_response(self, intent, entities, original_text):
        # Yanıt modeli için giriş metni oluştur
        input_text = f"Intent: {intent}\nEntities: {entities}\nUser: {original_text}\nAssistant:"

        # Yanıt modelini kullanarak cevap oluştur
        input_ids = self.response_tokenizer.encode(
            input_text, return_tensors="pt").to(self.device)
        attention_mask = torch.ones(
            input_ids.shape, dtype=torch.long, device=self.device)

        output = self.response_model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_length=150,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            top_k=50,
            top_p=0.95,
            temperature=0.7
        )

        response = self.response_tokenizer.decode(
            output[0], skip_special_tokens=True)

        # "Assistant:" kısmını kaldır
        response = response.split("Assistant:")[-1].strip()

        return response
