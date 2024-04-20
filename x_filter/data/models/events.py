from pydantic import BaseModel, Field
from x_filter.utils.security import generate_uuid

class MessageEvent(BaseModel):
    id: str = Field(default_factory=lambda: generate_uuid())
    user_id: str
    filter_id: str
    message: str
