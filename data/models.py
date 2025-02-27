from pydantic import BaseModel
from typing import Optional


class Message(BaseModel):
    id: str
    phone_number_id: str
    sender: str
    phone_number: str
    message_type: str
    text: str
    context: Optional[str] = None
    media_id: Optional[str] = None
    media_content: Optional[str] = None
    tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    timestamp: float
