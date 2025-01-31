from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from os import environ as env 
import tempfile

from utils import get_transcriptions, get_suggest

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    env_var = "fail"
    try:
        env_var = env["TEST_ENV_VARIABLE"]
    except:
        pass
    return {"message": "Medify.ai 🎉", "ENV_ACCESS": env_var}


# Single speaker route
@app.post("/single-speaker-transcribe")
async def single_speaker_transcribe(file: UploadFile):

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:

        file_data = await file.read()
        temp_file.write(file_data)
        temp_file_path = temp_file.name

    text_output = get_transcriptions(temp_file_path)

    return { "file_name": file.filename, "text": text_output}


# Med Suggestion Route
@app.post("/med-suggest")
async def med_suggest(prompt: str):

    text = get_suggest(prompt)

    return {"prompt": prompt, "message": text}
