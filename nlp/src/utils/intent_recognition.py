from transformers import DistilBertForSequenceClassification, AutoTokenizer
import torch
from torch.utils.data import Dataset, DataLoader
import nlpaug.augmenter.word as naw


class IntentDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, item):
        text = str(self.texts[item])
        label = self.labels[item]

        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt',
        )

        return {
            'text': text,
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }


def augment_data(texts, labels, num_aug=1):
    aug = naw.SynonymAug(aug_src='wordnet')
    augmented_texts = []
    augmented_labels = []

    for text, label in zip(texts, labels):
        augmented_texts.append(text)
        augmented_labels.append(label)

        for _ in range(num_aug):
            augmented_text = aug.augment(text)
            augmented_texts.append(augmented_text)
            augmented_labels.append(label)

    return augmented_texts, augmented_labels


def train_intent_model(texts, labels, tokenizer, device, num_labels):
    dataset = IntentDataset(texts, labels, tokenizer)
    dataloader = DataLoader(dataset, batch_size=16, shuffle=True)

    model = DistilBertForSequenceClassification.from_pretrained(
        'dbmdz/distilbert-base-turkish-cased', num_labels=num_labels)
    model.to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)

    for epoch in range(5):  # 5 epoch eğitim
        model.train()
        for batch in dataloader:
            optimizer.zero_grad()
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            outputs = model(
                input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            loss.backward()
            optimizer.step()

    return model


def classify_intent(text, model, tokenizer, label_dict, device):
    model.eval()
    encoding = tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=128,
        return_token_type_ids=False,
        padding='max_length',
        truncation=True,
        return_attention_mask=True,
        return_tensors='pt',
    )

    input_ids = encoding['input_ids'].to(device)
    attention_mask = encoding['attention_mask'].to(device)

    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
        _, prediction = torch.max(outputs.logits, dim=1)

    return prediction.item()  # Sayısal intent değerini döndür
