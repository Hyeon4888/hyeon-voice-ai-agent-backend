from fastapi import FastAPI

from contextlib import asynccontextmanager
from app.models import init_db
from app.routers.core.auth.router import router as auth_router

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

app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
