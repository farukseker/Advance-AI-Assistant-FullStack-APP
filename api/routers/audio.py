import shutil
import time
from pathlib import Path
from services import AudioTranscriber
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from models import CreateAudioModel
from io import BytesIO
import edge_tts
from s3_handler import get_s3_handler
from hashlib import sha256


router = APIRouter(
    prefix="/audio",
    tags=["audio"]
)


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    if not file.filename.endswith((".wav", ".mp3", ".webm")):
        raise HTTPException(status_code=400, detail="Invalid audio format")

    tmp_path = Path(f"tmp_{file.filename}")
    with tmp_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        transcriber = AudioTranscriber()
        text = transcriber.transcribe(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    return {"text": text}


@router.post("/create")
async def create_audio(payload: CreateAudioModel):
    h = sha256()
    communicate = edge_tts.Communicate(
        **payload.to_dict()
    )

    audio = BytesIO()

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.write(chunk["data"])

    audio.seek(0)
    h.update(audio.read())
    s3_key = f"voices/{h.hexdigest()}.wav"

    audio.seek(0)
    s3 = get_s3_handler()
    s3.upload_file(s3_key=s3_key, content_type="audio/wav", file_content=audio.read())

    ref = s3.generate_presigned_url(s3_key=s3_key, expiration=3600)

    return {
        "audio_s3_key": s3_key,
        "audio_ref": ref
    }

# custom_voices = db['custom_voices']


@router.get("/list")
async def get_audio_list():
    return await edge_tts.list_voices()