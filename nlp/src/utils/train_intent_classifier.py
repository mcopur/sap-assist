import pickle
import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import pandas as pd
import json
import numpy as np

os.environ['CUDA_VISIBLE_DEVICES'] = ''
device = torch.device('cpu')

project_root = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', '..'))
data_path = os.path.join(project_root, 'nlp', 'data',
                         'enriched_intent_data.json')

with open(data_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Print class distribution
print("Class distribution:")
print(df['intent'].value_counts(normalize=True))

le = LabelEncoder()
df['label'] = le.fit_transform(df['intent'])

train_texts, val_texts, train_labels, val_labels = train_test_split(
    df['text'], df['label'], test_size=0.2, stratify=df['label'], random_state=42)

model_name = "dbmdz/bert-base-turkish-cased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(
    model_name, num_labels=len(le.classes_)).to(device)


class IntentDataset(torch.utils.data.Dataset):
    def __init__(self, texts, labels):
        self.texts = texts
        self.labels = labels

    def __getitem__(self, idx):
        item = tokenizer(self.texts.iloc[idx], truncation=True,
                         padding='max_length', max_length=128, return_tensors="pt")
        item = {key: val.squeeze() for key, val in item.items()}
        item['labels'] = torch.tensor(self.labels.iloc[idx])
        return item

    def __len__(self):
        return len(self.labels)


train_dataset = IntentDataset(train_texts, train_labels)
val_dataset = IntentDataset(val_texts, val_labels)


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


training_args = TrainingArguments(
    output_dir=os.path.join(project_root, "nlp", "models", "results"),
    num_train_epochs=40,  # Eğitim süresini artırdık
    per_device_train_batch_size=16,
    per_device_eval_batch_size=64,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir=os.path.join(project_root, "nlp", "models", "logs"),
    logging_steps=10,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    no_cuda=True,
    learning_rate=3e-5,  # Öğrenme oranını artırdık
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
)

trainer.train()

model_save_path = os.path.join(
    project_root, "nlp", "models", "improved_intent_classifier_model")
model.save_pretrained(model_save_path)
tokenizer.save_pretrained(model_save_path)

le_save_path = os.path.join(project_root, "nlp", "models", "label_encoder.pkl")
with open(le_save_path, 'wb') as f:
    pickle.dump(le, f)

print(f"Model saved to {model_save_path}")
print(f"Label encoder saved to {le_save_path}")

eval_results = trainer.evaluate()
print("Evaluation results:", eval_results)

test_texts = ["Merhaba", "Yıllık izin almak istiyorum",
              "Satın alma talebi oluşturmak istiyorum"]
for text in test_texts:
    inputs = tokenizer(text, return_tensors="pt",
                       truncation=True, padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
    probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
    predicted_class = torch.argmax(probabilities, dim=-1).item()
    predicted_intent = le.inverse_transform([predicted_class])[0]
    confidence = probabilities[0][predicted_class].item()
    print(f"Text: {text}")
    print(f"Predicted Intent: {predicted_intent}")
    print(f"Confidence: {confidence:.4f}")
    print("---")
