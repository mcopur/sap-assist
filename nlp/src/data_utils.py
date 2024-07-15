import nlpaug.augmenter.word as naw
from sklearn.model_selection import train_test_split
import torch
from torch.utils.data import DataLoader
from transformers import BertForSequenceClassification
from intent_recognition import IntentDataset
from transformers import DistilBertForSequenceClassification


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


def update_model(new_texts, new_labels, texts, labels, label_dict, tokenizer, device):
    # Yeni etiketleri label_dict'e ekle
    for label in set(new_labels):
        if label not in label_dict:
            label_dict[label] = len(label_dict)

    # Yeni veriyi mevcut veri ile birleştir
    all_texts = texts + new_texts
    all_labels = labels + [label_dict[label] for label in new_labels]

    # Veriyi karıştır ve böl
    X_train, X_test, y_train, y_test = train_test_split(
        all_texts, all_labels, test_size=0.2, random_state=42)

    # Modeli yeniden eğit
    model = DistilBertForSequenceClassification.from_pretrained(
        'distilbert-base-multilingual-cased', num_labels=len(label_dict))
    model.to(device)

    train_dataset = IntentDataset(X_train, y_train, tokenizer)
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)

    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)

    for epoch in range(5):  # 5 epoch eğitim
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

    # Modeli değerlendir ve kaydet
    test_dataset = IntentDataset(X_test, y_test, tokenizer)
    test_loader = DataLoader(test_dataset, batch_size=16, shuffle=False)
    evaluate_model(model, test_loader, device)

    torch.save(model.state_dict(), '../models/updated_intent_model.pth')
    print("Model updated and saved.")
