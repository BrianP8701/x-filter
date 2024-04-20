from pydantic import BaseModel
from typing import Dict

class User(BaseModel):
    id: str
    period: int # period in days
    conversations: Dict[str, str]
    password: str
    x_username: str
