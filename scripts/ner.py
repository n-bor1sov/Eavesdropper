import torch
from transformers import BertForTokenClassification, BertTokenizerFast
import pandas as pd
import pickle

def get_model(device,num_labels ,path='./models/ner/model.pth'):
    model = BertForTokenClassification.from_pretrained("bert-base-cased", num_labels=num_labels)
    state_dict = torch.load(path)
    model.load_state_dict(state_dict)
    model = model.to(device)
    return model



def get_tokenizer(path='bert-base-cased'):
    tokenizer = BertTokenizerFast.from_pretrained(path)
    return tokenizer


def chunked_text(text, max_len=128):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_len, len(text))
        if end < len(text) and text[end] != ' ':
            end = text.rfind(' ', start, end)
            if end == -1:
                end = start + max_len
        chunks.append(text[start:end].strip())
        start = end
    return chunks



def inference(text, model, tokenizer, inverse_label_map, device, max_len=128):
    # Tokenize the sentence with offsets
    inputs = tokenizer(
        text,
        return_tensors="pt",
        return_offsets_mapping=True,
        padding=True,
        truncation=True,
        max_length=max_len
    )

    # Move inputs to the same device as the model
    input_ids = inputs["input_ids"].to(device)
    attention_mask = inputs["attention_mask"].to(device)
    offsets = inputs["offset_mapping"].cpu().numpy()[0]

    # Run inference
    model.eval()
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits

    # Get predicted labels
    predicted_token_class_ids = torch.argmax(logits, dim=2).cpu().numpy()[0]
    tokens = tokenizer.convert_ids_to_tokens(input_ids[0].cpu().numpy())

    # Convert the predicted class IDs back to NER labels
    predicted_labels = [inverse_label_map[label_id] for label_id in predicted_token_class_ids]

    # Combine tokens with their corresponding labels and offsets for readability
    results = [(token, label, (start, end)) for token, label, (start, end) in zip(tokens, predicted_labels, offsets)]

    # Align subword tokens with original words
    aligned_results = []
    current_word = ""
    current_labels = []

    for token, label, (start, end) in results:
        if start == 0 and end == 0:  # [CLS] and [SEP] tokens
            continue
        if token.startswith("##"):
            current_word += token[2:]
            current_labels.append(label)
        else:
            if current_word:
                # Aggregate labels for the current word
                # Here we simple take the first label, but you can define a more sophisticated strategy
                aligned_label = current_labels[0]
                aligned_results.append((current_word, aligned_label))
                current_word = ""
                current_labels = []
            current_word = token
            current_labels.append(label)

    # Add the last word if there's any
    if current_word:
        aligned_label = current_labels[0]
        aligned_results.append((current_word, aligned_label))

    # Post-process to ensure correct entity boundaries
    final_results = []
    i = 0
    while i < len(aligned_results):
        word, label = aligned_results[i]
        if label.startswith("B-"):
            # Check if the next words belong to the same entity
            entity_type = label[2:]
            j = i + 1
            while j < len(aligned_results) and aligned_results[j][1] == f"I-{entity_type}":
                word += ' ' + aligned_results[j][0]
                j += 1
            final_results.append((word, label))
            i = j
        else:
            final_results.append((word, label))
            i += 1

    return final_results


def main():
    with open('./models/label_map.pickle', 'rb') as f:
        idx_to_label = pickle.load(f)
    num_labels = len(idx_to_label)

    example_text = 'Hello, my name is Amir. I work at OpenAI as a senior ML engineer.'
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = get_model(device, num_labels=num_labels)
    tokenizer = get_tokenizer()

    for chunk in chunked_text(example_text):
        tokens, res = inference(chunk, model, tokenizer, device)
        decoded_labels = [idx_to_label[label] for label in res]
        print(decoded_labels)
        print(tokens)


if __name__ == '__main__':
    main()