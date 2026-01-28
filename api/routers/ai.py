from fastapi import APIRouter, HTTPException, Form, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List, Annotated
from models import MessageRequest, CreateChatRequest, MergeAudioRequest
import json
from datetime import datetime
from services import RAGService, CustomMongoHistory
from bson import ObjectId
from langchain_core.messages import ToolMessage
from ai_base import base_ai_agent

# Config
from config import MONGO_URI, OPENROUTER_API_KEY, OPENROUTER_API_HOST, DEFAULT_MODEL

from ai_base import generate_chat_title

# MongoDB Setup
client = AsyncIOMotorClient(MONGO_URI)
db = client['chat']
chats_collection = db['chats']
history_collection = db['chat_histories']

router = APIRouter(
    prefix="/ai",
    tags=["ai"]
)

def get_session_history(session_id: str) -> CustomMongoHistory:
    """Get or create session history :SessionId"""
    return CustomMongoHistory(
        connection_string=MONGO_URI,
        session_id=session_id,
        database_name="chat",
        collection_name="chat_histories"

    )

rag_service = RAGService()


@router.post('/chat/{chat_id}')
async def send_message_streaming(
        chat_id: str,
        question: str = Form(...),
        file: Optional[UploadFile] = File(None),
        model: Optional[str] = Form(DEFAULT_MODEL),
        custom_prompt: Optional[str] = Form(None)
):
    """Streaming response endpoint with memory"""

    async def generate():
        chat_message = ''  # AI yanıtını toplamak için
        chat_used = None

        try:
            agent_executor = base_ai_agent(
                model_name='openai/gpt-5-mini'
            )

            user_input = question

            await history_collection.insert_one({
                'SessionId': chat_id,
                'role': 'user',
                'content': user_input,
                'created_at': datetime.utcnow()
            })

            if file:
                user_input = f"{question} (Hedef dosya: {file.filename})"

            messages = [("user", user_input)]

            if custom_prompt:
                messages.append(("system", custom_prompt))

            config = {
                "configurable": {
                    "thread_id": chat_id
                }
            }

            # Stream events
            async for event in agent_executor.astream_events(
                    {"messages": messages},
                    config=config,
                    version="v2"
            ):
                kind = event["event"]

                if kind in ("on_chat_model_stream", "on_llm_stream"):
                    content = event["data"]["chunk"].content
                    if content:
                        chat_message += content
                        yield f"data: {json.dumps({'type': 'token', 'content': content}, ensure_ascii=False)}\n\n"

                elif kind == "on_tool_start":
                    tool_name = event["name"]
                    tool_input = event["data"]["input"]
                    print(f'Tool başladı: {tool_name}', tool_input)
                    yield f"data: {json.dumps({'type': 'tool_start', 'tool': tool_name, 'input': tool_input}, ensure_ascii=False)}\n\n"

                elif kind == "on_tool_end":
                    tool_name = event["name"]
                    tool_output = event["data"]["output"]

                    if isinstance(tool_output, ToolMessage):
                        payload = {
                            "tool": tool_output.name,
                            "content": tool_output.content,
                            "tool_call_id": tool_output.tool_call_id,
                        }
                    else:
                        payload = tool_output

                    yield f"data: {json.dumps({'type': 'tool_end', 'content': payload, 'tool': tool_name}, ensure_ascii=False)}\n\n"

                elif kind == "on_chat_model_end":
                    output = event.get("data", {}).get("output")

                    if output and hasattr(output, "usage_metadata"):
                        token_usage = output.usage_metadata
                        chat_used = token_usage

                        yield f"data: {json.dumps({'type': 'token_usage', 'data': token_usage}, ensure_ascii=False)}\n\n"

            if chat_message:
                await history_collection.insert_one({
                    'SessionId': chat_id,
                    'role': 'ai',
                    'content': chat_message.strip(),
                    'created_at': datetime.utcnow(),
                    'used': chat_used
                })

                print(f"AI mesajı kaydedildi (uzunluk: {len(chat_message)}): {chat_message[:100]}...")

            # Chat metadata güncelle
            await chats_collection.update_one(
                {"_id": ObjectId(chat_id)},
                {
                    "$set": {"updated_at": datetime.utcnow()},
                    "$inc": {"message_count": 2}
                }
            )

            # İşlem tamamlandı sinyali
            yield f"data: {json.dumps({'type': 'done', 'metadata': chat_used}, ensure_ascii=False)}\n\n"

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"Hata oluştu: {error_detail}")

            # Hata durumunda bile mesajı kaydetmeyi dene
            if chat_message:
                try:
                    await history_collection.insert_one({
                        'SessionId': chat_id,
                        'role': 'ai',
                        'content': chat_message.strip(),
                        'created_at': datetime.utcnow(),
                        'error': True
                    })
                except:
                    pass

            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.get('/models')
async def get_models():
    """Return available AI models"""
    return JSONResponse(content={
        "models": [
            {"id": "gpt-4o", "name": "GPT-4 Optimized", "provider": "openai"},
            {"id": "gpt-4o-mini", "name": "GPT-4 Mini", "provider": "openai"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "provider": "openai"}
        ]
    })


@router.post('/create-chat')
async def create_chat(request: CreateChatRequest):
    """Create a new chat session"""
    try:
        seed_text = getattr(request, "message")
        title = await generate_chat_title(seed_text)

        chat_doc = {
            # "user_id": request.user_id,
            "user_id": 'pars',
            "title": title,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "message_count": 0
        }

        result = await chats_collection.insert_one(chat_doc)
        chat_id = str(result.inserted_id)

        return JSONResponse(content={
            "chat_id": chat_id,
            "title": title,
            "created_at": chat_doc["created_at"].isoformat()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat oluşturma hatası: {str(e)}")

from s3_handler import S3Handler


@router.get("/chat/{chat_id}/history")
async def get_history(chat_id: str, limit: int = 50):
    try:
        s3 = S3Handler()

        cursor = (
            history_collection
            .find({"SessionId": chat_id})
            .sort("created_at", 1)
            .limit(limit)
        )
        history = await cursor.to_list(length=limit)
        for msg in history:
            msg["_id"] = str(msg["_id"])
            msg["created_at"] = msg["created_at"].isoformat()

            if msg.get('attachments', {}).get("audio", None):
                msg["attachments"]["audio"] = s3.generate_presigned_url(msg["attachments"]["audio"], 3600)

            if msg.get('attachments', {}).get("images", None):
                msg["attachments"]["images"] = [
                    s3.generate_presigned_url(image, 3600)
                    for image in msg["attachments"]["images"]
                ]

        return {
            "chat_id": chat_id,
            "history": history
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Geçmiş alma hatası: {str(e)}"
        )


@router.delete('/chat/{chat_id}')
async def delete_chat(chat_id: str):
    """Delete chat and its history"""
    try:
        # Clear message history
        history = get_session_history(chat_id)
        history.clear()

        # Delete chat document
        await chats_collection.delete_one({"_id": chat_id})

        return JSONResponse(content={
            "message": "Sohbet silindi",
            "chat_id": chat_id
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Silme hatası: {str(e)}")


@router.delete('/chat/{chat_id}/clear')
async def clear_history(chat_id: str):
    """Clear chat history only (keep chat document)"""
    try:
        history = get_session_history(chat_id)
        history.clear()

        await chats_collection.update_one(
            {"_id": chat_id},
            {"$set": {"message_count": 0, "updated_at": datetime.utcnow()}}
        )

        return JSONResponse(content={
            "message": "Sohbet geçmişi temizlendi",
            "chat_id": chat_id
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Temizleme hatası: {str(e)}")


@router.get('/chats')
async def get_user_chats(user_id: str, limit: int = 100):
    """Get all chats for a user"""
    try:
        cursor = (
            chats_collection
            .find({"user_id": user_id})
            .sort("created_at", -1)
            .limit(limit)
        )

        chats = await cursor.to_list(length=limit)
        for chat in chats:
            chat["chat_id"] = str(chat.pop("_id"))
            chat["created_at"] = chat["created_at"].isoformat()
            chat["updated_at"] = chat["updated_at"].isoformat()

        return JSONResponse(content={"chats": chats})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sohbet listesi alma hatası: {str(e)}")


@router.patch('/chat/{chat_id}/title')
async def update_chat_title(chat_id: str, title: str):
    """Update chat title"""
    try:
        await chats_collection.update_one(
            {"_id": chat_id},
            {"$set": {"title": title, "updated_at": datetime.utcnow()}}
        )

        return JSONResponse(content={
            "message": "Başlık güncellendi",
            "chat_id": chat_id,
            "title": title
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Güncelleme hatası: {str(e)}")


@router.patch('/chat/{chat_id}/merge/content/audio')
async def update_chat_content(payload: MergeAudioRequest):
    """set chat content to audio/mp3"""
    try:
        await history_collection.update_one(
            {"_id": ObjectId(payload.history_id)},
            {
                "$set":
                {
                    "updated_at": datetime.utcnow(),
                    "attachments": {
                        "audio": payload.content_s3_key
                        # "images" : []
                    }
                }
            }
        )

        return JSONResponse(content={
            "message": "content has merge",
            "history_id": payload.history_id,
            "content": payload.content_s3_key
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Güncelleme hatası: {str(e)}")