
from pydantic import BaseModel,Field
from datetime import datetime
from uuid import UUID, uuid4

class MessageModel(BaseModel):
    message_id: UUID = Field(default_factory=uuid4)  # Auto-generate UUID
    message: str = Field(...)
    sent_by: str = Field(default=None)
    sent_to: str = Field(default=None)
    is_read: bool= Field(default=False)
    sent_at: datetime = Field(default_factory=datetime.now)