import torch
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import ParameterGrid, KFold
from transformers import BertForSequenceClassification
from intent_recognition import IntentDataset
from transformers import DistilBertForSequenceClassification


def evaluate_model(model, test_loader, device):
    model.eval()
    predictions = []
    actual_labels = []

    with torch.no_grad():
        for batch in test_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            outputs = model(input_ids, attention_mask=attention_mask)
            _, preds = torch.max(outputs.logits, dim=1)

            predictions.extend(preds.cpu().tolist())
            actual_labels.extend(labels.cpu().tolist())

    report = classification_report(
        actual_labels, predictions, output_dict=True)
    print(classification_report(actual_labels, predictions))
    print("\nConfusion Matrix:")
    print(confusion_matrix(actual_labels, predictions))

    return report['accuracy']  # Accuracy'yi döndür


def optimize_hyperparameters(X_train, y_train, X_val, y_val, tokenizer, label_dict, device):
    param_grid = {
        'learning_rate': [1e-5, 2e-5, 3e-5],
        'batch_size': [8, 16, 32],
        'num_epochs': [3, 5, 10]
    }

    best_score = 0
    best_params = None

    for params in ParameterGrid(param_grid):
        model = DistilBertForSequenceClassification.from_pretrained(
            'distilbert-base-multilingual-cased', num_labels=len(label_dict))
        model.to(device)

        train_dataset = IntentDataset(X_train, y_train, tokenizer)
        train_loader = DataLoader(
            train_dataset, batch_size=params['batch_size'], shuffle=True)

        optimizer = torch.optim.AdamW(
            model.parameters(), lr=params['learning_rate'])

        for epoch in range(params['num_epochs']):
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

        # Validasyon seti üzerinde değerlendirme
        val_dataset = IntentDataset(X_val, y_val, tokenizer)
        val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)
        val_accuracy = evaluate_model(model, val_loader, device)

        print(f"Parameters: {params}, Validation Accuracy: {val_accuracy}")

        if val_accuracy > best_score:
            best_score = val_accuracy
            best_params = params

    print(f"Best parameters: {best_params}")
    print(f"Best validation accuracy: {best_score}")
    return best_params


def cross_validate(X, y, tokenizer, label_dict, device, n_splits=5):
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)

    fold_scores = []

    for fold, (train_index, val_index) in enumerate(kf.split(X), 1):
        X_train_fold, X_val_fold = [X[i]
                                    for i in train_index], [X[i] for i in val_index]
        y_train_fold, y_val_fold = [y[i]
                                    for i in train_index], [y[i] for i in val_index]

        model = DistilBertForSequenceClassification.from_pretrained(
            'distilbert-base-multilingual-cased', num_labels=len(label_dict))
        model.to(device)

        train_dataset = IntentDataset(X_train_fold, y_train_fold, tokenizer)
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

        # Validasyon
        val_dataset = IntentDataset(X_val_fold, y_val_fold, tokenizer)
        val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)
        fold_score = evaluate_model(model, val_loader, device)
        fold_scores.append(fold_score)

        print(f"Fold {fold} score: {fold_score}")

    print(
        f"Average cross-validation score: {sum(fold_scores) / len(fold_scores)}")
