import json
import torch
import random
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from intent_recognition import IntentDataset, classify_intent
from model_utils import evaluate_model, optimize_hyperparameters, cross_validate
from data_utils import augment_data
from chatbot.bot import Chatbot
import os

# Proje kök dizinini al
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Veri yükleme
data_path = os.path.join(project_root, 'data', 'intent_data.json')
with open(data_path, 'r', encoding='utf-8') as f:
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

# DistilBERT tokenizer ve model
model_name = 'distilbert-base-multilingual-cased'
tokenizer = DistilBertTokenizer.from_pretrained(model_name)
model = DistilBertForSequenceClassification.from_pretrained(
    model_name, num_labels=len(label_dict))

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

# Tokenizer ve model uyumluluğunu kontrol et
print(f"Tokenizer vocabulary size: {len(tokenizer.vocab)}")
print(
    f"Model embedding size: {model.distilbert.embeddings.word_embeddings.num_embeddings}")

# Veri setinden örnek al ve tokenize et
sample_text = texts[0]
sample_encoding = tokenizer.encode_plus(
    sample_text,
    add_special_tokens=True,
    max_length=128,
    return_token_type_ids=False,
    padding='max_length',
    truncation=True,
    return_attention_mask=True,
    return_tensors='pt',
)

print(f"Sample text: {sample_text}")
print(f"Encoded ids: {sample_encoding['input_ids']}")
print(f"Max token id: {sample_encoding['input_ids'].max().item()}")

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
cross_validate(X_train, y_train, tokenizer, label_dict, device)

# Model kaydetme
model_save_path = os.path.join(
    project_root, 'models', 'optimized_intent_model.pth')
torch.save(model.state_dict(), model_save_path)

# Test
test_text = "İzin almak istiyorum"
predicted_intent, confidence = classify_intent(
    test_text, model, tokenizer, label_dict, device)
print(f"Test text: {test_text}")
print(f"Predicted intent: {predicted_intent}")
print(f"Confidence: {confidence:.2f}")

# Chatbot'u test et
chatbot = Chatbot(model, tokenizer, label_dict, device)

test_conversations = [
    [
        "Merhaba",
        "Yıllık izin almak istiyorum",
        "01.08.2024 ve 05.08.2024 tarihleri arasında",
        "Evet, başka bir şey yok",
        "Bu izin talebimi iptal etmek istiyorum",
        "Teşekkür ederim, iyi günler"
    ],
    [
        "Selam",
        "Mazeret izni almak istiyorum",
        "Yarın 14:00-16:00 arası",
        "Teşekkürler, bu kadar",
        "Aslında biraz sinirliyim, çünkü izin almakta zorlanıyorum",
        "Haklısın, biraz sakinleşmeliyim"
    ],
    [
        "İyi günler",
        "Yeni bir bilgisayar sipariş etmek istiyorum",
        "MacBook Pro, 16 inç, M1 işlemcili model",
        "Hayır, başka bir şey istemiyorum",
        "Bu bilgisayarın fiyatı nedir?",
        "Anladım, teşekkürler"
    ]
]

for conversation in test_conversations:
    print("Yeni Konuşma Başlıyor...")
    for message in conversation:
        print(f"User: {message}")
        response = chatbot.process_message(message)
        print(f"Bot: {response}")
        print()
    chatbot.reset_context()
    print("Konuşma Bitti.\n")

# Chatbot'un belleğini kontrol et
print("Chatbot Belleği:")
with open("chatbot_memory.json", "r") as f:
    memory = json.load(f)
print(json.dumps(memory, indent=2))