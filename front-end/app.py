import streamlit as st
import requests
import sys
import os
# Add the scripts directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from masking import mask, demask

# Title of the application
st.title("Audio Transcription App")

# File uploader for audio files
uploaded_file = st.file_uploader("Choose an audio file", type=["wav", "mp3", "flac"])

# Function to send audio file to the API and get transcription
def transcribe_audio(file):
    api_url = ""
    files = {"file": file}
    response = requests.post(api_url, files=files)
    if response.status_code == 200:
        return response.json().get("transcription", "No transcription available")
    else:
        return f"Error: {response.status_code} - {response.text}"

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
        st.subheader("Transcription:")
        st.write(transcription)
    else:
        st.error("Please upload an audio file first.")