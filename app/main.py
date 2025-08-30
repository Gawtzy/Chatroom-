from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import json
from typing import Dict, List, Set
import uuid
from pydantic import BaseModel

app = FastAPI(title="Distributed Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

manager = ConnectionManager()

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    if manager.is_username_taken(room_id, user_id):
        await websocket.close(code=1008, reason="Username already taken")
        return
        
    await manager.connect(websocket, room_id, user_id)

    join_message = {
        "id": str(uuid.uuid4()),
        "room_id": room_id,
        "user_id": "System",
        "content": f"{user_id} joined the chat",
        "timestamp": None,
        "message_type": "system"
    }
    await manager.broadcast_to_room(json.dumps(join_message), room_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message = {
                "id": str(uuid.uuid4()),
                "room_id": room_id,
                "user_id": user_id,
                "content": message_data["content"],
                "timestamp": message_data.get("timestamp"),
                "message_type": message_data.get("type", "text")
            }
            
            await manager.broadcast_to_room(json.dumps(message), room_id)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id, user_id)
        leave_message = {
            "id": str(uuid.uuid4()),
            "room_id": room_id,
            "user_id": "System",
            "content": f"{user_id} left the chat",
            "timestamp": None,
            "message_type": "system"
        }
        await manager.broadcast_to_room(json.dumps(leave_message), room_id)

class JoinRoomRequest(BaseModel):
    UserId: str
    roomId: str
    password: str

@app.post("/join-room")
async def joinroom(request: JoinRoomRequest):
    user_id = request.UserId
    room_id = request.roomId
    password = request.password
    
    if room_id in manager.rooms:
        if manager.rooms[room_id] != password:
            raise HTTPException(status_code=401, detail="Wrong password")
        
        if manager.is_username_taken(room_id, user_id):
            raise HTTPException(status_code=409, detail="Username already taken")
        
        return {"message": f"User {user_id} can join room {room_id}"}
    else:
        manager.rooms[room_id] = password
        return {"message": f"Room {room_id} created successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)