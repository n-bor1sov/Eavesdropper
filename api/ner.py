from scripts.ner import get_model, get_tokenizer, inference, chunked_text
from fastapi import FastAPI, HTTPException
import torch
import pickle
from pydantic import BaseModel
app = FastAPI()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
with open('./models/label_map.pickle', 'rb') as f:
    idx_to_label = pickle.load(f)

num_labels = len(idx_to_label)

model = get_model(device, num_labels)
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
        tokens, res = inference(chunk, model, tokenizer, device)
        decoded_labels = [idx_to_label[label] for label in res]
        tokens_all.extend(tokens)
        labels_all.extend(decoded_labels)

    return NERResponse(tokens=tokens_all, labels=labels_all)

