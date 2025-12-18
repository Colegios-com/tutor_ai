from pydantic import BaseModel
from typing import Optional


class File(BaseModel):
    uri: str
    mime_type: str


class Message(BaseModel):
    id: Optional[str] = None
    whatsapp_message_id: str
    phone_number_id: str
    wa_id: str
    conversation_id: Optional[str] = None
    restaurant_id: Optional[str] = None
    bot_id: Optional[str] = None
    sender: str
    message_type: str
    text: Optional[str] = None
    context: Optional[str] = None
    file: Optional[File] = None
    created_at: Optional[str] = None
