import streamlit as st
import requests
import sys
import os
import time
# Add the scripts directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from masking import mask, demask

# Title of the application
st.title("Audio Transcription App")

# File uploader for audio files
uploaded_file = st.file_uploader("Choose an audio file", type=["wav", "mp3", "flac"])

# Function to send audio file to the API and get transcription


def transcribe_audio(file):
    def create_task(file):
        url = "http://127.0.0.1:8080/tasks/"
        response = requests.post(url, files={'file': file})
        if response.status_code == 200:
            task_id = response.json()['task_id']
            return task_id
        else:
            return None

    task_id = create_task(file)
    assert task_id is not None, "Task creation failed"

    def get_task_status(task_id):
        url = f"http://127.0.0.1:8080/tasks/{task_id}"
        response = requests.get(url)
        print(response.json())
        return response.json()

    response = get_task_status(task_id)
    while response['status'] == 'in_progress':
        response = get_task_status(task_id)

        if 'status' not in response:
            break

        if response['status'] == 'failed':
            # exception
            raise Exception("Transcription failed")

        time.sleep(1)

    result_string = ""
    for i, segment in enumerate(response['segments']):
        result_string += f"Speaker {segment['speaker'][-2:]}: {segment['text'].strip()}\n"

    return result_string


def ner(result_string):
    # Define the URL of the FastAPI app
    url = "http://127.0.0.1:8081/ner"

    # Define the input payload
    payload = {
        "text": result_string
    }

    # Send a POST request
    response = requests.post(url, json=payload)

    # Check the response
    if response.status_code == 200:
        print("Cool")
    else:
        print("Error:", response.status_code, response.text)

    return response

def summarize(ner_result):
    masked_text, key = mask([ner_result])
    
    url = "http://localhost:8000/chat"

    data = {
        "query": masked_text
    }
    response = requests.post(url,json=data)
    if response.status_code == 200:
        response_data = response.json()
        summary = response_data.get('content', '')
        
        return demask(summary, key)[0]
    else:
        st.error(f"Error: {response.status_code} - {response.text}")
        return None

# Button to trigger transcription
if st.button("Transcribe"):
    if uploaded_file is not None:
        with st.spinner("Transcribing audio..."):
            transcription = transcribe_audio(uploaded_file)
        with st.spinner("NER..."):
            ner_result = ner(transcription).json()
        with st.spinner("Summarizing..."):
            summary = summarize(ner_result)
        print(summary)
        st.subheader("Summary:")
        st.write(summary)
    else:
        st.error("Please upload an audio file first.")