import torch
from transformers import BertTokenizer, BertForSequenceClassification, GPT2LMHeadModel, GPT2Tokenizer, AdamW
from torch.utils.data import DataLoader, TensorDataset, TextDataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import json
import pickle
import logging
from transformers import Trainer, TrainingArguments

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_intent_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return pd.DataFrame(data)

def preprocess_intent_data(df, tokenizer, max_length=128):
    texts = df['text'].tolist()
    labels = df['intent'].tolist()

    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(labels)

    encoded_texts = tokenizer(texts, padding=True, truncation=True, max_length=max_length, return_tensors='pt')
    return encoded_texts, encoded_labels, label_encoder

def train_intent_model(data_path, model_save_path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")

    tokenizer = BertTokenizer.from_pretrained("dbmdz/bert-base-turkish-cased")
    df = load_intent_data(data_path)
    encoded_texts, encoded_labels, label_encoder = preprocess_intent_data(df, tokenizer)

    train_inputs, val_inputs, train_labels, val_labels = train_test_split(
        encoded_texts['input_ids'], encoded_texts['attention_mask'], encoded_labels, test_size=0.2, random_state=42
    )

    train_dataset = TensorDataset(train_inputs, train_labels)
    val_dataset = TensorDataset(val_inputs, val_labels)

    train_dataloader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_dataloader = DataLoader(val_dataset, batch_size=32)

    num_labels = len(label_encoder.classes_)
    model = BertForSequenceClassification.from_pretrained("dbmdz/bert-base-turkish-cased", num_labels=num_labels)
    model.to(device)

    optimizer = AdamW(model.parameters(), lr=2e-5)

    for epoch in range(5):  # 5 epochs for example, adjust as needed
        model.train()
        for batch in train_dataloader:
            batch = tuple(t.to(device) for t in batch)
            inputs = {'input_ids': batch[0], 'attention_mask': batch[1], 'labels': batch[2]}
            outputs = model(**inputs)
            loss = outputs.loss
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

        # Validation
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for batch in val_dataloader:
                batch = tuple(t.to(device) for t in batch)
                inputs = {'input_ids': batch[0], 'attention_mask': batch[1], 'labels': batch[2]}
                outputs = model(**inputs)
                val_loss += outputs.loss.item()

        avg_val_loss = val_loss / len(val_dataloader)
        logger.info(f"Epoch {epoch+1}, Validation Loss: {avg_val_loss}")

    # Save the model and tokenizer
    model.save_pretrained(model_save_path)
    tokenizer.save_pretrained(model_save_path)

    # Save the label encoder
    with open(f"{model_save_path}/label_encoder.pkl", "wb") as f:
        pickle.dump(label_encoder, f)

    logger.info(f"Intent model saved to {model_save_path}")

def load_response_dataset(file_path, tokenizer):
    return TextDataset(
        tokenizer=tokenizer,
        file_path=file_path,
        block_size=128)

def train_response_model(data_path, model_save_path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")

    # Initialize tokenizer and model
    tokenizer = GPT2Tokenizer.from_pretrained("dbmdz/german-gpt2")  # Use an appropriate Turkish GPT model
    model = GPT2LMHeadModel.from_pretrained("dbmdz/german-gpt2").to(device)

    # Load and tokenize the dataset
    dataset = load_response_dataset(data_path, tokenizer)
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    # Set up training arguments
    training_args = TrainingArguments(
        output_dir="./results",
        overwrite_output_dir=True,
        num_train_epochs=5,
        per_device_train_batch_size=4,
        save_steps=10_000,
        save_total_limit=2,
    )

    # Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=dataset,
    )

    # Train the model
    trainer.train()

    # Save the model and tokenizer
    model.save_pretrained(model_save_path)
    tokenizer.save_pretrained(model_save_path)

    logger.info(f"Response model saved to {model_save_path}")

if __name__ == "__main__":
    intent_data_path = "path/to/your/intent_data.json"
    intent_model_save_path = "path/to/save/intent_model"
    train_intent_model(intent_data_path, intent_model_save_path)

    response_data_path = "path/to/your/response_data.txt"
    response_model_save_path = "path/to/save/response_model"
    train_response_model(response_data_path, response_model_save_path)