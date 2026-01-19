import shutil
from pathlib import Path
from services import AudioTranscriber
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from models import CreateAudioModel
from io import BytesIO
import edge_tts


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
    communicate = edge_tts.Communicate(
        **payload.to_dict()
    )

    audio = BytesIO()

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.write(chunk["data"])

    audio.seek(0)

    return StreamingResponse(
        audio,
        media_type="audio/wav",
        headers={
            "Content-Disposition": "attachment; filename=audio.mp3"
        }
    )


@router.get("/list")
async def get_audio_list():
    return await edge_tts.list_voices()