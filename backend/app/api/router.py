from fastapi import APIRouter
from app.api.v1 import projects, scenarios, runs, websockets

api_router = APIRouter()

api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(scenarios.router, prefix="/scenarios", tags=["Scenarios"])
api_router.include_router(runs.router, prefix="/runs", tags=["Test Runs"])
api_router.include_router(websockets.router, prefix="/ws", tags=["Live WebSockets"])
