from pydantic import BaseModel
from typing import Dict, List

class Conversation(BaseModel):
    id: str
    user_id: str
    stage: float
    messages: List[Dict[str, str]] = []
    cached_messages: List[Dict[str, str]] = []
