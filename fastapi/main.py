import os
from pathlib import Path
from tempfile import NamedTemporaryFile
import whisper
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.background import BackgroundTask
from fastapi.middleware.cors import CORSMiddleware


model = whisper.load_model(name="models/tiny.en.pt", in_memory=True)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def file_size(val: int, unit: str) -> int:
    if unit == "KB":
        return val * 1024
    elif unit == "MB":
        return val * 1024 * 1024
    elif unit == "GB":
        return val * 1024 * 1024 * 1024
    return val

async def cleanup_file(filepath: str):
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Error cleaning up file: {e}")

@app.post("/api/v1/transcribe")
async def transcribe(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No media file provided")
    
    if file.size > file_size(50, "MB"):
        raise HTTPException(status_code=400, detail="File size limit exceeded")

    temp_filepath = None
    try:
        temp_dir = Path("media/temp")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        with NamedTemporaryFile(
            delete=False,
            dir=str(temp_dir),
            prefix=file.filename.split(".")[0],
            suffix=f".{file.filename.split('.')[-1] if '.' in file.filename else 'tmp'}"
        ) as temp_file:
            temp_filepath = temp_file.name
            contents = await file.read()
            temp_file.write(contents)
            temp_file.flush()

        result = model.transcribe(temp_filepath)
        transcription = result["text"]

        return JSONResponse(
            content={"transcription": transcription, "status": "success"},
            background=BackgroundTask(cleanup_file, temp_filepath)
        )

    except Exception as e:
        if temp_filepath and os.path.exists(temp_filepath):
            await cleanup_file(temp_filepath)
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}",
            headers={"status": "error"}
        )

@app.get("/ping")
def ping():
    """Health check endpoint."""
    return JSONResponse(content={"ping": "pong"}, status_code=200)

@app.get("/")
def index():
    """Root endpoint returning plain text."""
    return PlainTextResponse("Hello, world!")