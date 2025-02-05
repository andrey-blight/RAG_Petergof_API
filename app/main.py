from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import v1_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(v1_router, prefix="/api/v1")

# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: list[tuple[WebSocket, int]] = []
#
#     def connect(self, websocket: WebSocket, artikul: int):
#         self.active_connections.append((websocket, artikul))
#
#     def disconnect(self, websocket: WebSocket, artikul: int):
#         self.active_connections.remove((websocket, artikul))
#
#     async def broadcast(self, message: dict):
#         artikul = message["artikul"]
#
#         for connection in self.active_connections:
#             if connection[1] == artikul:
#                 try:
#                     await connection[0].send_json(message)
#                 except Exception as e:
#                     print(e)
#                     pass
#
#
# manager = ConnectionManager()
#
#
# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     try:
#         while True:
#             data = await websocket.receive_json()
#             action = data["action"]
#             artikul = data["artikul"]
#
#             if action == "subscribe" and artikul:
#                 manager.connect(websocket, artikul)
#
#                 async with httpx.AsyncClient(timeout=10) as client:
#                     await client.get(settings.WB_SUBSCRIBE_URL.format(artikul=artikul))
#
#             elif action == "trigger" and artikul:
#                 product = {
#                     "artikul": artikul,
#                     "name": data["name"],
#                     "price": data["price"],
#                     "rating": data["rating"],
#                     "count": data["count"]
#                 }
#
#                 await manager.broadcast(product)
#
#     except WebSocketDisconnect:
#         print("Disconnected")
