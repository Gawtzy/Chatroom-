from fastapi import APIRouter
from fastapi import WebSocket, WebSocketDisconnect
import json
import uuid
from services import manager

router = APIRouter()

@router.websocket("/ws/{room_id}/{user_id}")
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
