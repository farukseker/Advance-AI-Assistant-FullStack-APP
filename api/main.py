from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from contextlib import asynccontextmanager

from routers.audio import router as audio_router


'''
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        ...
    except Exception as e:
        print("Startup skipped:", e)
    yield
'''

# app = FastAPI(lifespan=lifespan)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audio_router)
