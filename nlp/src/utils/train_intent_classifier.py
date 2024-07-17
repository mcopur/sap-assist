import json
import os
import pickle
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from collections import Counter
import random

# Force CPU usage
device = torch.device("cpu")

# Basit veri artırma fonksiyonu


def augment_text(text, n=1):
    words = text.split()
    new_texts = [text]
    for _ in range(n):
        new_words = words.copy()
        for i in range(len(new_words)):
            if random.random() < 0.2:  # %20 olasılıkla bir kelimeyi değiştir
                new_words[i] = random.choice(words)  # Rastgele bir kelime seç
        new_texts.append(" ".join(new_words))
    return new_texts


# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the correct path to the data file
data_file_path = os.path.join(
    current_dir, '..', '..', 'data', 'intent_data.json')

# Load the dataset
with open(data_file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

texts = [item['text'] for item in data]
intents = [item['intent'] for item in data]

print(f"Total samples: {len(texts)}")
print(f"Unique intents: {set(intents)}")
print(f"Intent distribution: {dict(Counter(intents))}")

# Veri artırma
augmented_texts = []
augmented_intents = []
for text, intent in zip(texts, intents):
    augmented = augment_text(text, n=2)  # Her örnek için 2 yeni örnek oluştur
    augmented_texts.extend(augmented)
    augmented_intents.extend([intent] * len(augmented))

texts = augmented_texts
intents = augmented_intents

print(f"Total samples after augmentation: {len(texts)}")
print(f"Intent distribution after augmentation: {dict(Counter(intents))}")

# Encode labels
le = LabelEncoder()
labels = le.fit_transform(intents)

# Split the dataset
train_texts, val_texts, train_labels, val_labels = train_test_split(
    texts, labels, test_size=0.2, random_state=42)

# Load tokenizer and model
model_name = "distilbert-base-multilingual-cased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(
    model_name, num_labels=len(le.classes_)).to(device)

# Tokenize data
train_encodings = tokenizer(train_texts, truncation=True, padding=True)
val_encodings = tokenizer(val_texts, truncation=True, padding=True)

# Create torch datasets


class IntentDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx])
                for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)


train_dataset = IntentDataset(train_encodings, train_labels)
val_dataset = IntentDataset(val_encodings, val_labels)

# Define metrics


def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average='weighted')
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }


# Define training arguments
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=10,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=32,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    no_cuda=True,
)

# Create Trainer instance
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics
)

print("Starting training...")
trainer.train()
print("Training completed.")

# Evaluate model
print("Evaluating model...")
eval_results = trainer.evaluate()
print(f"Evaluation results: {eval_results}")

# Save the model
model.save_pretrained("./intent_classifier_model")
tokenizer.save_pretrained("./intent_classifier_model")

# Save the label encoder
with open('label_encoder.pkl', 'wb') as f:
    pickle.dump(le, f)

print("Model training completed and saved.")
