from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from qdrant_client import QdrantClient
from config import MONGO_URI
# from werkzeug.utils import secure_filename


client = AsyncIOMotorClient(MONGO_URI)
db = client['chat']

QdrantClient(host="localhost", port=6334, grpc=True)

router = APIRouter(
    prefix="/ai",
    tags=["ai"]
)


@router.get('/models')
async def get_models():
    ...

@router.post('/create-chat')
async def create_chat(chat):
    chats = db.collection["chats"]

@router.get('/message')
async def get_models():
    ...


@router.get('/history')
async def get_models():
    ...


@router.get('/clean')
async def get_models():
    ...