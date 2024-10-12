import os
import sys
import json
import torch
import logging
import argparse
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer, set_seed
from torch.utils.data import Dataset
import numpy as np

# Proje kök dizinini belirleme
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

# Logging ayarları
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Rastgeleliği sabit tutmak için seed ayarlayalım
set_seed(42)

# CUDA kullanımını devre dışı bırakalım ve CPU'yu zorlayalım
os.environ["CUDA_VISIBLE_DEVICES"] = ""
device = torch.device("cpu")


class IntentDataset(Dataset):
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


def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def train_intent_model(data_path, model_save_path):
    logger.info("Starting intent classification model training")

    # Veri yükleme
    data = load_data(data_path)
    texts = [item['text'] for item in data]
    intents = [item['intent'] for item in data]

    # Label encoding
    label_encoder = LabelEncoder()
    encoded_intents = label_encoder.fit_transform(intents)

    # Veri bölme
    train_texts, val_texts, train_labels, val_labels = train_test_split(
        texts, encoded_intents, test_size=0.2, random_state=42)

    # Tokenizer ve model yükleme
    tokenizer = AutoTokenizer.from_pretrained("dbmdz/bert-base-turkish-cased")
    model = AutoModelForSequenceClassification.from_pretrained(
        "dbmdz/bert-base-turkish-cased", num_labels=len(label_encoder.classes_))

    # Veriyi tokenize etme
    train_encodings = tokenizer(train_texts, truncation=True, padding=True)
    val_encodings = tokenizer(val_texts, truncation=True, padding=True)

    # Dataset oluşturma
    train_dataset = IntentDataset(train_encodings, train_labels)
    val_dataset = IntentDataset(val_encodings, val_labels)

    # Eğitim ayarları
    training_args = TrainingArguments(
        output_dir=os.path.join(model_save_path, 'results'),
        num_train_epochs=5,
        per_device_train_batch_size=8,  # Batch size'ı azalttık
        per_device_eval_batch_size=8,   # Batch size'ı azalttık
        warmup_steps=100,
        weight_decay=0.01,
        logging_dir=os.path.join(model_save_path, 'logs'),
        logging_steps=10,
        evaluation_strategy="steps",
        eval_steps=100,
        save_steps=100,
        load_best_model_at_end=True,
        no_cuda=True,  # GPU kullanımını devre dışı bıraktık
        dataloader_num_workers=0,  # Çoklu işlem kullanımını devre dışı bıraktık
    )

    # Trainer oluşturma ve eğitim
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset
    )

    trainer.train()

    # Model ve tokenizer'ı kaydetme
    model.save_pretrained(model_save_path)
    tokenizer.save_pretrained(model_save_path)

    # Label encoder'ı kaydetme
    with open(os.path.join(model_save_path, 'label_encoder.json'), 'w') as f:
        json.dump(label_encoder.classes_.tolist(), f)

    logger.info(f"Intent classification model saved to {model_save_path}")


def train_response_model(data_path, model_save_path):
    logger.info("Response model training is not implemented yet.")
    # Implement response model training here if needed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train intent classification and response generation models")
    parser.add_argument('--task', type=str, required=True, choices=['intent', 'response'],
                        help="Task to perform: 'intent' for intent classification, 'response' for response generation")
    args = parser.parse_args()

    try:
        if args.task == 'intent':
            intent_data_path = os.path.join(
                PROJECT_ROOT, 'nlp', 'data', 'intent_data.json')
            intent_model_save_path = os.path.join(
                PROJECT_ROOT, 'nlp', 'models', 'intent_classifier_model')
            train_intent_model(intent_data_path, intent_model_save_path)
        elif args.task == 'response':
            response_data_path = os.path.join(
                PROJECT_ROOT, 'nlp', 'data', 'response_data.json')
            response_model_save_path = os.path.join(
                PROJECT_ROOT, 'nlp', 'models', 'response_generator')
            train_response_model(response_data_path, response_model_save_path)
    except Exception as e:
        logger.error(f"An error occurred during training: {str(e)}")
        raise
