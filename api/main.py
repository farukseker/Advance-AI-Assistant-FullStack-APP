from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
# from contextlib import asynccontextmanager
# from middlewares import register_middlewares
from routers import audio_router, search_router, embed_router, ai_router

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

# register_middlewares(app, exclude_paths=["/health", "/static"], header_name="X-Process-Time-ms")

app.include_router(audio_router)
app.include_router(search_router)
app.include_router(embed_router)
app.include_router(ai_router)

# f4