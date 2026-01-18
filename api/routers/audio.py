from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from models import CreateAudioModel
from io import BytesIO
import edge_tts


router = APIRouter(
    prefix="/audio",
    tags=["audio"]
)


@router.post("/create")
async def create_audio(payload: CreateAudioModel):
    print(payload.to_dict())
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
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "attachment; filename=audio.mp3"
        }
    )


@router.get("/list")
async def get_audio_list():
    return await edge_tts.list_voices()