from pydantic import BaseModel
from typing import Optional


class Template(BaseModel):
    id: str
    template_type: str
    title: str
    description: str
    metadata: str


class Parameters(BaseModel):
    template: str
    seed: Optional[str] = None
    grade: str
    class_level: str
    subject: str
    topic: str
    instructions: str
    complexity: str
    length: str
