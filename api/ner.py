from scripts.ner import get_model, get_tokenizer, inference, chunked_text
from fastapi import FastAPI, HTTPException
import torch
import pickle
from pydantic import BaseModel
import re
app = FastAPI()

# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
device = torch.device("cpu")
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


@app.post("/ner", response_model=NERResponse)
async def get_ner(request: NERRequest):
    tokens_all, labels_all = [], []
    for chunk in chunked_text(request.text):
        res = inference(chunk, model, tokenizer, idx_to_label, device)
        for token, label in res:
        #decoded_labels = [idx_to_label[label] for label in res]
            tokens_all.append(token)
            labels_all.append(label)

    return NERResponse(tokens=tokens_all, labels=labels_all)

