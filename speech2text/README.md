# WhisperX API
This is a Python API for the WhisperX

## Prerequisites
- Cuda >= 12.6.0
- Docker
- Nvidia hpc toolkit

## How to run
Create a huggingface access token from [here](https://huggingface.co/settings/tokens). and accept the user agreement for
the following models: [Segmentation](https://huggingface.co/pyannote/segmentation-3.0) and 
[Speaker-Diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1).

Put the access token in the `config.yaml` file. The file should look like this:
```
model:
  hf_key: "your_access_token"
```
Next, inside the `speech2text` directory, run the following commands:
```
docker build -t speech2text .
docker run --gpus all -p 8080:8080 speech2text
```

## How to use
The api is available at http://localhost:8080. The api is used to transcribe audio files.

Two handles are available:
1) `tasks`: to put the audio file to queue

Request: audio file: file\
Response: task_id: string
2) `results`: to get the result

Request: task_id: string\
Response: transcription: json

## Example python code
```
import requests

def create_task(file_path):
    url = "http://127.0.0.1:8080/tasks/"
    files = {'file': open(file_path, 'rb')}
    response = requests.post(url, files=files)
    if response.status_code == 200:
        task_id = response.json()['task_id']
        print(f"Task created with ID: {task_id}")
        return task_id
    else:
        print(f"Error creating task: {response.text}")
        return None

# Example usage:
file_path = "audio.mp3"
task_id = create_task(file_path)
```

```
import requests

def get_task_status(task_id):
    url = f"http://127.0.0.1:8080/tasks/{task_id}"
    response = requests.get(url)
    print(response.json())
    return response.json()

# Example usage:
transcription = get_task_status(task_id)
```