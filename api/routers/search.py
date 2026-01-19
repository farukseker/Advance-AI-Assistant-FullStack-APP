from fastapi import APIRouter, Depends, HTTPException
from ddgs import DDGS


router = APIRouter(
    prefix="/search",
    tags=["search"]
)


@router.get('')
async def q(q: str):
    try:
        return DDGS().text(q, max_results=5)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))