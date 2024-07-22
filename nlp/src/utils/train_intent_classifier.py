from nlp.src.utils.data_preprocessing import preprocess_text, balance_dataset
import pickle
import os
import sys
import torch
from transformers import RobertaTokenizer, RobertaForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# Projenin kök dizinini Python yoluna ekle
project_root = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)


# CPU kullanımını zorla
os.environ["CUDA_VISIBLE_DEVICES"] = ""
device = torch.device("cpu")
print(f"Using device: {device}")

# Veri yükleme
data_path = os.path.join(project_root, 'nlp', 'data',
                         'augmented_intent_data.json')
data = pd.read_json(data_path)

# Veri ön işleme
data['text'] = data['text'].apply(preprocess_text)
data = balance_dataset(data.to_dict('records'))
data = pd.DataFrame(data)

# Etiket kodlama
le = LabelEncoder()
data['label'] = le.fit_transform(data['intent'])

# Veri bölme
train_texts, val_texts, train_labels, val_labels = train_test_split(
    data['text'], data['label'], test_size=0.2, stratify=data['label'], random_state=42)

# Tokenizer ve model yükleme
tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
model = RobertaForSequenceClassification.from_pretrained(
    'roberta-base', num_labels=len(le.classes_))
model.to(device)

# Veri seti oluşturma


class IntentDataset(torch.utils.data.Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts.iloc[idx])
        label = self.labels.iloc[idx]

        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            return_token_type_ids=False,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt',
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }


train_dataset = IntentDataset(train_texts, train_labels, tokenizer)
val_dataset = IntentDataset(val_texts, val_labels, tokenizer)

# Metrik hesaplama fonksiyonu


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


# Eğitim argümanları
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=20,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=64,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    learning_rate=5e-5,
    no_cuda=True,
)

# Trainer oluşturma ve eğitim
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
)

trainer.train()

# Model kaydetme
model_save_path = os.path.join(
    project_root, 'nlp', 'models', 'intent_classifier_model')
model.save_pretrained(model_save_path)
tokenizer.save_pretrained(model_save_path)

# Label encoder kaydetme
le_save_path = os.path.join(project_root, 'nlp', 'models', 'label_encoder.pkl')
with open(le_save_path, 'wb') as f:
    pickle.dump(le, f)

print(f"Improved model saved to {model_save_path}")
print(f"Label encoder saved to {le_save_path}")
