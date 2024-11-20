import streamlit as st
import requests

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

# Button to trigger transcription
if st.button("Transcribe"):
    if uploaded_file is not None:
        with st.spinner("Transcribing audio..."):
            transcription = transcribe_audio(uploaded_file)
        st.subheader("Transcription:")
        st.write(transcription)
    else:
        st.error("Please upload an audio file first.")