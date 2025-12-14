from pydantic import BaseModel
from typing import Optional


class Message(BaseModel):
    id: Optional[str] = None
    whatsapp_message_id: str
    phone_number_id: str
    sender: str
    phone_number: str
    message_type: str
    text: Optional[str] = None # Message Text
    context: Optional[str] = None # Reply Message ID
    file: Optional[object] = None # Media File Metadata
    timestamp: float
