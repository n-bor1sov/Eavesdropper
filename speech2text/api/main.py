from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from enum import Enum
from uuid import uuid4
from queue import Queue
import threading
import yaml
import json
import whisperx

app = FastAPI()

# Simulating a task queue
task_queue = Queue()

# Model
device = "cuda"
audio_file = "audio.mp3"
batch_size = 8  # reduce if low on GPU mem
compute_type = "float16"  # change to "int8" if low on GPU mem (may reduce accuracy)
model_name = "base"
model = whisperx.load_model(model_name, device, compute_type=compute_type)
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
hf_key = config["model"]["hf_key"]
diarize_model = whisperx.DiarizationPipeline(use_auth_token=hf_key, device=device)


def transcribe(audio_file_path):
    # Load audio
    audio = whisperx.load_audio(audio_file_path)

    # Transcribe
    result = model.transcribe(audio, batch_size=batch_size)

    # Align
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

    # Diarize
    diarize_segments = diarize_model(audio)
    result = whisperx.assign_word_speakers(diarize_segments, result)

    return result


# Simulating task processing in the background
def process_tasks():
    while True:
        task_id, audio_file_path = task_queue.get()
        try:
            result = transcribe(audio_file_path)
            # Simulating saving the result
            with open(f"{task_id}.json", "w") as f:
                json.dump(result, f)
            tasks[task_id] = TaskStatus.done
        except Exception as e:
            tasks[task_id] = TaskStatus.failed
            print(f"Error processing task {task_id}: {e}")
        task_queue.task_done()


# Starting the task processor in the background
threading.Thread(target=process_tasks, daemon=True).start()


# Enum for task status
class TaskStatus(str, Enum):
    failed = "failed"
    in_progress = "in_progress"
    done = "done"


# In-memory storage for task status (replace with a database for production)
tasks = {}


@app.post("/tasks/")
async def create_task(file: UploadFile = File(...)):
    task_id = str(uuid4())
    tasks[task_id] = TaskStatus.in_progress
    file_name = f"{task_id}.{file.filename.split('.')[-1]}"
    with open(file_name, "wb") as f:
        f.write(file.file.read())
    task_queue.put((task_id, file_name))
    return {"task_id": task_id}


@app.get("/tasks/{task_id}")
async def read_task(task_id: str):
    if task_id in tasks:
        if tasks[task_id] == TaskStatus.done:
            try:
                with open(f"{task_id}.json", "r") as f:
                    result = json.load(f)
                    return JSONResponse(content=result, media_type="application/json")
            except FileNotFoundError:
                return {"error": "Result not found"}
        else:
            return {"status": tasks[task_id]}
    else:
        raise HTTPException(status_code=404, detail="Task not found")
