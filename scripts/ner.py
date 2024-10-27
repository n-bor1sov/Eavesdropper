import torch
from transformers import BertForTokenClassification, BertTokenizerFast
import pandas as pd
import pickle

def get_model(device, num_labels, path='./models/ner'):
    model = BertForTokenClassification.from_pretrained(path, num_labels=num_labels)
    model = model.to(device)
    return model



def get_tokenizer(path='./models/ner'):
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



def inference(text, model, tokenizer, device, max_len=128):
    encoding = tokenizer(text, return_tensors="pt", padding="max_length", truncation=True, max_length=max_len)
    input_ids = encoding['input_ids'].to(device)
    attention_mask = encoding['attention_mask'].to(device)

    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        print(logits.shape)

    predictions = torch.argmax(logits, dim=-1)
    tokens = tokenizer.convert_ids_to_tokens(input_ids[0].cpu().numpy())
    masked_predictions = predictions[attention_mask.bool()].cpu().tolist()
    return tokens[1:len(masked_predictions)-1], masked_predictions[:-2]


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