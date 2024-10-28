from flask import Flask, request, jsonify
from threading import Thread
from queue import Queue
import sys
import torch
import os

app = Flask(__name__)

# In-memory queue
task_queue = Queue()

# GEMMA model initialization (adapted from your provided code)
VARIANT = '2b-it'
MACHINE_TYPE = 'cpu'
CONFIG = VARIANT[:2]
if CONFIG == '2b':
    CONFIG = '2b-v2'
    
weights_dir = "models/gemma-2-pytorch-gemma-2-2b-it-v1/"


# Ensure that the tokenizer is present
tokenizer_path = os.path.join(weights_dir, 'tokenizer.model')
assert os.path.isfile(tokenizer_path), 'Tokenizer not found!'

# Ensure that the checkpoint is present
ckpt_path = os.path.join(weights_dir, f'model.ckpt')
assert os.path.isfile(ckpt_path), 'PyTorch checkpoint not found!'

# print(os.getcwd())
sys.path.append('api/gemma_pytorch')

from gemma.config import GemmaConfig, get_model_config
from gemma.model import GemmaForCausalLM
from gemma.tokenizer import Tokenizer

model_config = get_model_config(CONFIG)
model_config.tokenizer = tokenizer_path
model_config.quant = 'quant' in VARIANT
torch.set_default_dtype(model_config.get_dtype())
device = torch.device('cpu')
model = GemmaForCausalLM(model_config)
model.load_weights(ckpt_path)
model = model.to(device).eval()

# Chat Templates
USER_CHAT_TEMPLATE = "<start_of_turn>user\n{prompt}<end_of_turn><eos>\n"
MODEL_CHAT_TEMPLATE = "<start_of_turn>model\n{prompt}<end_of_turn><eos>\n"


def process_gemma_request(prompt):
    # Sample formatted prompt
    prompt = USER_CHAT_TEMPLATE.format(prompt=prompt) + '<start_of_turn>model\n'
    results = model.generate(prompt, device=device, output_len=128)
    return results

def worker():
    while True:
        prompt = task_queue.get()
        result = process_gemma_request(prompt)
        print(f"Result: {result}")  # Replace with your desired output handling
        task_queue.task_done()

# Start the worker thread
thread = Thread(target=worker)
thread.daemon = True
thread.start()

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if 'prompt' not in data:
        return jsonify({'error': 'Missing prompt in request'}), 400

    prompt = data['prompt']
    task_queue.put(prompt)
    return jsonify({'message': 'Request queued for processing'}), 202

if __name__ == '__main__':
    app.run(debug=True)