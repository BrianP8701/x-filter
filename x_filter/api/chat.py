# x_filter/api/chat.py
from fastapi import APIRouter
from pydantic import BaseModel
import logging  

from x_filter import Database
from x_filter.ai.chat import handle_chat_message

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
    # Misleading route, this is actually receiving a chat message
    logging.info(f"Received chat message: {data}")
    user_id = data.user_id
    message = data.message
    
    user_chat = db.query("conversations", user_id)
    user_chat["messages"].append({"role": "user", "content": message})
    db.update("conversations", user_chat)
    logging.info(f"Called the handcrafted conversation flow")
    await handle_chat_message(user_id, message)
    return {"user_chat": user_chat}
