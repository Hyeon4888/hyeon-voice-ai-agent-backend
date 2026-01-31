from dotenv import load_dotenv

load_dotenv()

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S"
)

from contextlib import asynccontextmanager
from app.models import init_db
from app.routers.core.auth.router import router as auth_router
from app.routers.agents import router as agents_router
from app.routers.api_keys import router as api_keys_router
from app.routers.tools import router as tools_router
from app.routers.history import router as history_router
from app.routers.phone_numbers import router as phone_numbers_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="Voice AI Agent Backend",
    description="Backend for Voice AI Agent",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(agents_router)
app.include_router(api_keys_router)
app.include_router(tools_router)
app.include_router(history_router)
app.include_router(phone_numbers_router)

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
