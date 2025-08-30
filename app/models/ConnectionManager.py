from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.rooms: Dict[str, str] = {}  
        self.room_users: Dict[str, Set[str]] = {} 
    
    async def connect(self, websocket: WebSocket, room_id: str, user_id: str):
        await websocket.accept()
        
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
            
        if room_id not in self.room_users:
            self.room_users[room_id] = set()
        
        self.active_connections[room_id].append(websocket)
        self.room_users[room_id].add(user_id)
    
    def disconnect(self, websocket: WebSocket, room_id: str, user_id: str):
        if room_id in self.active_connections:
            if websocket in self.active_connections[room_id]:
                self.active_connections[room_id].remove(websocket)
                if not self.active_connections[room_id]:
                    del self.active_connections[room_id]
        
        if room_id in self.room_users:
            self.room_users[room_id].discard(user_id)
            if not self.room_users[room_id]:
                del self.room_users[room_id]
                if room_id in self.rooms:
                    del self.rooms[room_id]
    
    def is_username_taken(self, room_id: str, user_id: str) -> bool:
        if room_id not in self.room_users:
            return False
        return user_id in self.room_users[room_id]
    
    
    async def broadcast_to_room(self, message: str, room_id: str):
        if room_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_text(message)
                except WebSocketDisconnect:
                    disconnected.append(connection)
            
            for conn in disconnected:
                self.active_connections[room_id].remove(conn)