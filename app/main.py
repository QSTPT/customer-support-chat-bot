from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.groq_client import close_groq_client, get_groq_client
from app.routes import chat, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_groq_client()  # fail fast if GROQ_API_KEY is missing
    yield
    await close_groq_client()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="FastAPI Groq SSE", version="1.0.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(chat.router)
    app.mount("/", StaticFiles(directory="static", html=True), name="static") #must be registered after the routers
    return app


app = create_app()