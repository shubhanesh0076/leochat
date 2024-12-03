import typing
from db.db_connection import get_database 
from fastapi import Depends
from fastapi.websockets import WebSocket

# from app.utils.security import get_device_info

# Store connected WebSocket clients
active_connections: dict[str, set] = dict()


class ConnectionManager:
    async def connect(self, room_id: str, websocket: WebSocket):
    
        await websocket.accept()
        # Add the WebSocket to the set of connected clients
        if room_id in active_connections:
            active_connections[room_id].add(websocket)
        else:
            active_connections[room_id]={websocket}
    
    def ws_receive_text(self, websocket: WebSocket):
        return websocket.receive_text()
        
    async def disconnect(self, room_id: str):
        active_connections.pop(room_id, None)

    async def send_personal_message(self, message: str, user_id: str, chat_id):
        websocket = active_connections.get(user_id)
        if websocket:
            await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in active_connections.values():
            await connection.send_text(message)

class Chatmanager:
    
    async def create_message(self, data: dict):
        try:
            db = await get_database()
            await db['user_messages'].insert_one(data)
            print("Hiiii................")
        except Exception as e:
            print("ErrorL ", e)
        
    def update_message(self, message_id):
        pass
    
    def delete_message(self, message_id):
        pass
    
    def get_all_messages():
        pass
    
    def get_specific_user_rooms_messages():
        pass
    # def insert_message(self):
    #     pass