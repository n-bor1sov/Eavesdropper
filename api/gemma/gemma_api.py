import os
from huggingface_hub import hf_hub_download
from llama_cpp import Llama
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# Specify the repository ID and the filename you want to download
repo_id = "bartowski/gemma-2-2b-it-GGUF"
filename = "gemma-2-2b-it-IQ4_XS.gguf"
cache_dir = "./gemma_model"

# Local path to the model file
local_model_path = os.path.join(cache_dir, filename)

system_prompt = """Online Meeting Summary & Insights Assistant
Task:
Analyze Discussion Structure: Identify and label key topics/subtopics discussed during the meeting.
Speaker-wise Subtopic Summaries: For each subtopic, provide a brief summary (1-2 sentences) of the key points mentioned by each relevant speaker.
Meeting Conclusion & Key Takeaways:
Short Conclusion (2-3 sentences): Outline the overall discussion and meeting outcome.
Emphasized Key Points (bullet points): Highlight the most crucial decisions, actions, or agreements from the meeting.
Input:

Meeting Transcript: 

{script}

Desired Output Format:

**Topic 1: [ Brief Topic Description ]**
* **Speaker [ID]**: [ Brief Summary of Speaker's Key Points (1-2 sentences) ]
* **Speaker [ID]**: [ Brief Summary of Speaker's Key Points (1-2 sentences) ]
*...

**Topic 2: [ Brief Topic Description ]**
* **Speaker [ID]**: [ Brief Summary of Speaker's Key Points (1-2 sentences) ]
* **Speaker [ID]**: [ Brief Summary of Speaker's Key Points (1-2 sentences) ]
*...

**Conclusion:**
* Brief summary of the overall discussion and meeting outcome (2-3 sentences)

**Key Takeaways:**
* • Crucial Decision/Action 1
* • Crucial Decision/Action 2
* •...

Answer:"""


# Check if the model file already exists locally
if not os.path.exists(local_model_path):
    print(f"Model file not found at {local_model_path}. Downloading from Hugging Face...")
    # Download the file to the local directory
    local_model_path = hf_hub_download(repo_id=repo_id, filename=filename, cache_dir=cache_dir)
    print(f"Model downloaded to: {local_model_path}")
else:
    print(f"Model file already exists at {local_model_path}. Skipping download.")

# Initialize the Llama model with the locally downloaded model file and desired context window size
llm = Llama(
    model_path=local_model_path,
    n_ctx=2048  # Set the desired context window size
)

def create_chat_completion(query):
    response = llm.create_chat_completion(
        messages=[
            {
                "role": "user",
                "content": system_prompt.format(script=query)
            }
        ]
    )
    return response

# Define a route for chat completion
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    query = data.get('query', '')
    if len(query) == 0:
        return jsonify({"content": "No data provided"})
    response = create_chat_completion(query)['choices'][0]['message']['content']
    return jsonify({"content": response})

if __name__ == "__main__":
    print("Model loaded. Ready to handle chat completions.")
    app.run(host='0.0.0.0', port=8000, debug=True)