# x_filter/websocket.py
from fastapi import WebSocket

# User Connection Manager (add this to a new module or inside app.py)
class WebsocketManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WebsocketManager, cls).__new__(cls)
            cls._instance.active_connections = {}
        return cls._instance

    def is_connected(self, user_id: str) -> bool:
        return user_id in self.active_connections

    async def connect(self, user_id: str, websocket: WebSocket):
        if user_id not in self.active_connections:
            self.active_connections[user_id] = websocket
            await websocket.accept()

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

    def send_chat_message_to_user(self, user_id: str, message: str):
        if user_id in self.active_connections:
            data = {"message": message}
            self.active_connections[user_id].send_json(data)
            
    def send_filter_message_to_user(self, user_id: str, filter_id: str, message: str):
        if user_id in self.active_connections:
            data = {"message": message, "filter_id": filter_id}
            # Use send_json to send the dictionary as JSON
            self.active_connections[user_id].send_json(data)
