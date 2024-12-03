from fastapi import FastAPI
from api.v1.auth import accounts
from fastapi.routing import APIWebSocketRoute 
from sockets.wsocket import chat_websocket_endpoint


def get_absolute_url(app: FastAPI):
    app.include_router(accounts, prefix="/api/v1/auth")
    
    # Register the WebSocket endpoint
    # app.router.routes.append(APIWebSocketRoute('/ws/chat/{chat_id}/device_id={device_id}', chat_websocket_endpoint))
    app.router.routes.append(APIWebSocketRoute('/ws/chat', chat_websocket_endpoint))
    return app