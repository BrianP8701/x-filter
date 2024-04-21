# x_filter/api/chat.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional

from x_filter import Database
from x_filter.data.models.filter import FilterTarget
from x_filter.utils.security import authenticate, generate_uuid

db = Database()
router = APIRouter()

@router.get("/api/get_user_chat/{user_id}")
async def get_user_chat(user_id: str):
    user_chat = db.query("conversations", user_id)
    return {"user_chat": user_chat}


class SendChatMessage(BaseModel):
    user_id: str
    message: str
@router.post("/api/send_chat_message")
async def send_chat_message(data: SendChatMessage):
    user_id = data.user_id
    message = data.message
    
    user_chat = db.query("conversations", user_id)
    user_chat["messages"].append({"role": "user", "content": message})
    db.update("conversations", user_chat)
    return {"user_chat": user_chat}
