from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    BertTokenizerFast,
    BertForMaskedLM,
    GPT2Tokenizer,
    GPT2LMHeadModel,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import argparse
import logging
import json
import numpy as np
import torch
import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''

torch.backends.mps.enabled = False


# Proje kök dizinini belirleme
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', '..'))

# Logging ayarları
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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


class ResponseDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: val[idx].clone().detach()
                for key, val in self.encodings.items()}
        item['labels'] = self.labels[idx].clone().detach()
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

    # CPU'ya taşı
    device = torch.device("cpu")
    model = model.to(device)

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
        per_device_train_batch_size=8,
        per_device_eval_batch_size=16,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir=os.path.join(model_save_path, 'logs'),
        logging_steps=10,
        evaluation_strategy="steps",
        eval_steps=500,
        save_steps=1000,
        load_best_model_at_end=True,
        no_cuda=True,
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
    logger.info("Starting response generation model training")

    # Veri yükleme
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Veriyi uygun formata dönüştürme
    texts = [
        f"Intent: {item['intent']}\nContext: {json.dumps(item['context'])}\nResponse: {item['response']}" for item in data]

    # GPT-2 modelini ve tokenizer'ı yükle
    tokenizer = GPT2Tokenizer.from_pretrained(
        "dbmdz/gpt2-turkish-cased", bos_token='<|startoftext|>', eos_token='<|endoftext|>', pad_token='<|pad|>')
    model = GPT2LMHeadModel.from_pretrained("dbmdz/gpt2-turkish-cased")
    model.resize_token_embeddings(len(tokenizer))

    # Veriyi tokenize etme
    encodings = tokenizer(texts, truncation=True, padding=True,
                          max_length=512, return_tensors="pt")

    # Dataset oluşturma
    dataset = ResponseDataset(encodings, encodings['input_ids'])

    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer, mlm=False
    )

    # Eğitim ayarları
    training_args = TrainingArguments(
        output_dir=os.path.join(model_save_path, 'results'),
        num_train_epochs=10,  # Epoch sayısını artırdık
        per_device_train_batch_size=8,  # Batch size'ı artırdık
        save_steps=500,
        save_total_limit=2,
        prediction_loss_only=True,
        no_cuda=True,
        learning_rate=5e-5,  # Öğrenme oranını ekledik
        weight_decay=0.01,  # Weight decay ekledik
        warmup_steps=500,  # Warmup steps ekledik
    )

    # Trainer oluşturma ve eğitim
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=data_collator,
    )

    trainer.train()

    # Model ve tokenizer'ı kaydetme
    model.save_pretrained(model_save_path)
    tokenizer.save_pretrained(model_save_path)

    logger.info(f"Response generation model saved to {model_save_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train intent classification and response generation models")
    parser.add_argument('--task', type=str, required=True, choices=[
                        'intent', 'response'], help="Task to perform: 'intent' for intent classification, 'response' for response generation")
    args = parser.parse_args()

    if args.task == 'intent':
        intent_data_path = os.path.join(
            PROJECT_ROOT, 'nlp', 'data', 'intent_data.json')
        intent_model_save_path = os.path.join(
            PROJECT_ROOT, 'nlp', 'models', 'intent_classifier')
        train_intent_model(intent_data_path, intent_model_save_path)
    elif args.task == 'response':
        response_data_path = os.path.join(
            PROJECT_ROOT, 'nlp', 'data', 'response_data.json')
        response_model_save_path = os.path.join(
            PROJECT_ROOT, 'nlp', 'models', 'response_generator')
        train_response_model(response_data_path, response_model_save_path)
