from db.db_connection import get_database 
from fastapi.websockets import WebSocket
from typing import Dict


class ConnectionManager:
    
        def __init__(self):
            # Map room_id to a list of WebSocket connections
            self.active_connections: Dict[str, set] = {}
            
        async def connect(self, room_id: str, websocket: WebSocket):
            try:
                await websocket.accept()
                if room_id not in self.active_connections:
                    self.active_connections[room_id] = []
                self.active_connections[room_id].append(websocket)
                print("ACTIVE CONNECTION: ", self.active_connections)
                
            except Exception as e:
                pass

        def ws_receive_text(self, websocket: WebSocket):
            return websocket.receive_text()
        
        def disconnect(self, room_id: str, websocket: WebSocket):
            if room_id in self.active_connections:
                self.active_connections[room_id].remove(websocket)
                if not self.active_connections[room_id]:  # Remove room if no connections remain
                    del self.active_connections[room_id]

        async def broadcast_message(self, room_id: str, message: dict):
            if room_id in self.active_connections:
                for websocket in self.active_connections[room_id]:
                    await websocket.send_json(message)

class Chatmanager:
    
    async def check_room(self):
        pass
        # find the room
        # if not room then create it else get it and return the room info. 
    
    async def create_message(self, data: dict):
        try:
            db = await get_database()
            await db['user_messages'].insert_one(data)

        except Exception as e:
            print("ErrorL ", e)
    
    async def get_room(self, room_id):
        db = await get_database()
        room_info = await db['chat_room'].find_one({"room_id": room_id})
        if not room_info:
            return None
        return room_info
    
    # def update_message(self, message_id):
    #     pass
    
    # def delete_message(self, message_id):
    #     pass
    
    # def get_all_messages():
    #     pass
    
    # def get_specific_user_rooms_messages():
    #     pass
    # # def insert_message(self):
    # #     pass