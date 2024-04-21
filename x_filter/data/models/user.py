from pydantic import BaseModel
from typing import Dict

class User(BaseModel):
    id: str
    password: str
    x_username: str
    filters: Dict[str, str] = {}
