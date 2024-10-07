from pydantic import BaseModel
from datetime import datetime

class MessageCreate(BaseModel):
    sender_id: int
    receiver_id: int
    content: str

class MessageRequest(BaseModel):
    receiver_username: str | None = None
    receiver_email: str | None = None
    content: str

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    timestamp: datetime
