import json
import asyncio
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # Map run_id -> set of active WebSockets
        self.active_rooms: Dict[str, Set[WebSocket]] = {}
        self.loop: Optional[asyncio.AbstractEventLoop] = None

    def register_loop(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop

    async def connect(self, run_id: str, websocket: WebSocket):
        await websocket.accept()
        if not self.loop:
            self.loop = asyncio.get_running_loop()
        if run_id not in self.active_rooms:
            self.active_rooms[run_id] = set()
        self.active_rooms[run_id].add(websocket)

    async def disconnect(self, run_id: str, websocket: WebSocket):
        if run_id in self.active_rooms:
            self.active_rooms[run_id].discard(websocket)
            if not self.active_rooms[run_id]:
                del self.active_rooms[run_id]

    async def broadcast(self, run_id: str, message: dict):
        try:
            curr_loop = asyncio.get_running_loop()
        except RuntimeError:
            curr_loop = None

        if self.loop and self.loop.is_running() and curr_loop != self.loop:
            # Called from a background thread with different loop
            asyncio.run_coroutine_threadsafe(self._send_payload(run_id, message), self.loop)
            return

        await self._send_payload(run_id, message)

    async def _send_payload(self, run_id: str, message: dict):
        sockets = list(self.active_rooms.get(run_id, []))
        if not sockets:
            return

        payload = json.dumps(message)
        for ws in sockets:
            try:
                await ws.send_text(payload)
            except Exception:
                pass

ws_manager = ConnectionManager()

@router.websocket("/runs/{run_id}")
async def websocket_run_stream(websocket: WebSocket, run_id: str):
    await ws_manager.connect(run_id, websocket)
    try:
        while True:
            # Keep-alive ping/pong
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await ws_manager.disconnect(run_id, websocket)
    except Exception:
        await ws_manager.disconnect(run_id, websocket)
