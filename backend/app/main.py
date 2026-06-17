from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.config import settings
from app.database import Base, engine
from app.routers.admin import router as admin_router
from app.routers.categories import router as categories_router
from app.routers.notes import router as notes_router
from app.services.search import ensure_index
from app.websocket.manager import manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    try:
        ensure_index()
    except Exception:
        pass
    yield


app = FastAPI(title="Madani Muzakarah Database", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(notes_router)
app.include_router(categories_router)
app.include_router(admin_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
