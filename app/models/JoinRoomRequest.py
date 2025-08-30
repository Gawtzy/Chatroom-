from pydantic import BaseModel

class JoinRoomRequest(BaseModel):
    UserId: str
    roomId: str
    password: str