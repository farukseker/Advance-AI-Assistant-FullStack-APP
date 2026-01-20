# routes/embed.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from services import RAGService

router = APIRouter(
    prefix="/embed",
    tags=["embed"]
)

# Initialize RAG Service
rag_service = RAGService()


# ============= Request Models =============

class QuestionRequest(BaseModel):
    question: str
    filename: Optional[str] = None
    top_k: int = 3


class QuestionWithFileRequest(BaseModel):
    question: str
    top_k: int = 3


# ============= Endpoints =============

@router.post("/load-document")
async def load_document(file: UploadFile = File(...), save_to_db: bool = True):
    """
    Load document and proces

    - save_to_db=True: Save to Qdrant -permanently
    - save_to_db=False: Just proces -Temporarily
    """
    try:
        content = await file.read()

        if save_to_db:
            result = rag_service.process_and_store(content, file.filename)
        else:
            result = rag_service.process_only(content, file.filename)

        return JSONResponse(content=result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Unable to decode text file. Please ensure it's UTF-8 encoded."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@router.post("/ask-with-file")
async def ask_with_file(
        file: UploadFile = File(...),
        question: str = Form(...),
        top_k: int = Form(3)
):
    """
    Geçici dosya ile soru sor

    Dosyayı Qdrant'a kaydetmeden, sadece bu oturum için işler.
    Hızlı test ve tek seferlik sorgular için ideal.
    """
    try:
        content = await file.read()

        result = rag_service.ask_with_temporary_file(
            question=question,
            content=content,
            filename=file.filename,
            top_k=top_k
        )

        return JSONResponse(content=result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@router.get("/list-files")
async def list_files():
    try:
        files = rag_service.list_stored_files()

        return JSONResponse(content={
            "files": files,
            "total": len(files)
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")