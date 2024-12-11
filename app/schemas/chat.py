
from pydantic import BaseModel,Field
from datetime import datetime
# import typing
from typing import Optional
from uuid import UUID, uuid4

class ChatRoom(BaseModel):
    room_id: UUID = Field(default_factory=uuid4)
    name: Optional[str]=Field(default=None)
    description: Optional[str]=Field(default=None)
    members: list[str]  # User IDs

class MessageModel(BaseModel):
    message_id: UUID = Field(default_factory=uuid4)  # Auto-generate UUID
    room_id: UUID=Field(default_factory=uuid4)
    message: str = Field(...)
    sent_by: str = Field(default=None)
    is_read: bool= Field(default=False)
    sent_at: datetime = Field(default_factory=datetime.now)