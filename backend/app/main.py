import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db
from app.api.router import api_router

from app.api.v1.websockets import ws_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables and directories exist
    ws_manager.register_loop(asyncio.get_running_loop())
    await init_db()
    settings.ARTIFACTS_PATH.mkdir(parents=True, exist_ok=True)
    yield
    # Shutdown

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Autonomous Browser Agent for End-to-End Web App Testing & Self-Healing Playwright Code Generation",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for screenshots and audit PDFs
app.mount("/artifacts", StaticFiles(directory=str(settings.ARTIFACTS_PATH)), name="artifacts")

# Register Master API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "headless": settings.HEADLESS,
        "default_model": settings.DEFAULT_MODEL
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
