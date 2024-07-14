from chatbot.bot import Chatbot
from data_utils import augment_data, update_model
from model_utils import evaluate_model, optimize_hyperparameters, cross_validate
from intent_recognition import IntentDataset, classify_intent
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader
from transformers import BertTokenizer, BertForSequenceClassification
import json
import torch
import random
import sys
import os

# Proje kök dizinini Python yoluna ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# Veri yükleme
with open(os.path.join(os.path.dirname(__file__), '../data/intent_data.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

# Veriyi hazırlama
texts = []
labels = []
label_dict = {}

for i, intent in enumerate(data['intents']):
    label_dict[intent['tag']] = i
    for pattern in intent['patterns']:
        texts.append(pattern)
        labels.append(i)

# Veri artırma
augmented_texts, augmented_labels = augment_data(texts, labels, num_aug=2)

# Veriyi karıştır
combined = list(zip(augmented_texts, augmented_labels))
random.shuffle(combined)
augmented_texts, augmented_labels = zip(*combined)

# Veriyi eğitim ve test setlerine ayırma
X_train, X_test, y_train, y_test = train_test_split(
    augmented_texts, augmented_labels, test_size=0.2, random_state=42)

# BERT tokenizer ve model
tokenizer = BertTokenizer.from_pretrained('dbmdz/bert-base-turkish-cased')
model = BertForSequenceClassification.from_pretrained(
    'dbmdz/bert-base-turkish-cased', num_labels=len(label_dict))

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

# Hiper-parametre optimizasyonu
best_params = optimize_hyperparameters(
    X_train, y_train, X_test, y_test, tokenizer, label_dict, device)

# En iyi parametrelerle modeli eğitme
train_dataset = IntentDataset(X_train, y_train, tokenizer)
train_loader = DataLoader(
    train_dataset, batch_size=best_params['batch_size'], shuffle=True)

optimizer = torch.optim.AdamW(
    model.parameters(), lr=best_params['learning_rate'])

for epoch in range(best_params['num_epochs']):
    model.train()
    for batch in train_loader:
        optimizer.zero_grad()
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        outputs = model(
            input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
    print(f'Epoch {epoch+1} completed')

# Model değerlendirme
test_dataset = IntentDataset(X_test, y_test, tokenizer)
test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)
evaluate_model(model, test_loader, device)

# Çapraz doğrulama
cross_validate(augmented_texts, augmented_labels,
               tokenizer, label_dict, device)

# Model kaydetme
torch.save(model.state_dict(), '../models/optimized_intent_model.pth')

# Test
test_text = "İzin almak istiyorum"
predicted_intent, confidence = classify_intent(
    test_text, model, tokenizer, label_dict, device)
print(f"Test text: {test_text}")
print(f"Predicted intent: {predicted_intent}")
print(f"Confidence: {confidence:.2f}")

# Yeni veri ile model güncelleme örneği
new_texts = ["Yeni bir özellik eklemek istiyorum",
             "Proje durumunu öğrenmek istiyorum"]
new_labels = ["feature_request", "project_status"]
update_model(new_texts, new_labels, texts, labels,
             label_dict, tokenizer, device)

# Chatbot'u test et
chatbot = Chatbot(model, tokenizer, label_dict, device)

test_messages = [
    "Merhaba",
    "Yıllık izin almak istiyorum",
    "01.08.2024 ve 05.08.2024 tarihleri için yıllık izin talebi oluşturabilir misin",
    "Mazeret izni almak istiyorum",
    "05.08.2024 tarihi 09:30-11:30 için mazeret izin talebi oluşturabilir misin",
    "Yeni bir bilgisayar sipariş etmek istiyorum"
]

for message in test_messages:
    response = chatbot.process_message(message)
    print(f"User: {message}")
    print(f"Bot: {response}")
    print()
