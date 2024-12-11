from fastapi import FastAPI
from api.v1.auth import accounts
from api.v1.chat_room import chat_room
from fastapi.routing import APIWebSocketRoute 
from sockets.wsocket import chat_websocket_endpoint


def get_absolute_url(app: FastAPI):
    app.include_router(accounts, prefix="/api/v1/auth")
    app.include_router(chat_room, prefix="/api/v1/chat_room")
    
    # Register the WebSocket endpoint
    app.router.routes.append(APIWebSocketRoute('/ws/chat', chat_websocket_endpoint))
    return app