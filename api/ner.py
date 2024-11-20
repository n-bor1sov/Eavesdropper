from scripts.ner import get_model, get_tokenizer, inference, chunked_text
from fastapi import FastAPI, HTTPException
import torch
import pickle
from pydantic import BaseModel
import re
app = FastAPI()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
with open('./models/label_map.pickle', 'rb') as f:
    label_to_idx = pickle.load(f)
idx_to_label = {idx: label for label, idx in label_to_idx.items()}

model = get_model(device, len(idx_to_label))
tokenizer = get_tokenizer()


class NERRequest(BaseModel):
    text: str

class NERResponse(BaseModel):
    tokens: list
    labels: list


def clean_text(input_text):
    """
    Removes lines containing only numbers from the input text.

    Args:
        input_text (str): The text to be cleaned.

    Returns:
        str: The cleaned text with number-only lines removed.
    """
    # Split the input text into lines
    lines = input_text.split('\n')

    # Filter out lines that contain only numbers (possibly with leading/trailing whitespace)
    cleaned_lines = [line for line in lines if not re.match(r'^\s*\d+\s*$', line)]

    # Join the cleaned lines back into a single string
    cleaned_text = '\n'.join(cleaned_lines)
    return cleaned_text


@app.post("/ner", response_model=NERResponse)
async def get_ner(request: NERRequest):
    tokens_all, labels_all = [], []
    text_without_timestamps = re.sub(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', '', request.text)
    cleaned_text = clean_text(re.sub(r'^\d$\n', '', text_without_timestamps, flags=re.MULTILINE))
    for chunk in chunked_text(cleaned_text):
        res = inference(chunk, model, tokenizer, idx_to_label, device)
        for token, label in res:
        #decoded_labels = [idx_to_label[label] for label in res]
            tokens_all.append(token)
            labels_all.append(label)

    return NERResponse(tokens=tokens_all, labels=labels_all)

