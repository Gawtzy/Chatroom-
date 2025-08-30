from fastapi import APIRouter, HTTPException
from services import manager
from models import JoinRoomRequest


router = APIRouter()

@router.post("/join-room")
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
