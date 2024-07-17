import json
from sklearn.model_selection import train_test_split
from .intent_recognition import train_intent_model


def load_training_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    texts = [item['text'] for item in data]
    labels = [item['intent'] for item in data]

    # Etiketleri sayısal değerlere dönüştür
    unique_labels = list(set(labels))
    label_dict = {label: i for i, label in enumerate(unique_labels)}
    numeric_labels = [label_dict[label] for label in labels]

    return texts, numeric_labels, label_dict


def update_model(new_texts, new_labels, texts, labels, label_dict, tokenizer, device):
    # Yeni veriyi mevcut veri ile birleştir
    all_texts = texts + new_texts
    all_labels = labels + new_labels

    # Veriyi karıştır ve böl
    X_train, X_test, y_train, y_test = train_test_split(
        all_texts, all_labels, test_size=0.2, random_state=42)

    # Modeli yeniden eğit
    num_labels = len(set(all_labels))
    model = train_intent_model(X_train, y_train, tokenizer, device, num_labels)

    # Modeli değerlendir ve kaydet
    # (Değerlendirme fonksiyonunu implement etmeniz gerekecek)
    # evaluate_model(model, X_test, y_test, tokenizer, device)

    return model, label_dict
