# x_filter/api/other.py
from fastapi import APIRouter
from pydantic import BaseModel
import logging  

from x_filter import Database
from x_filter.ai.chat import handle_chat_message

db = Database()
router = APIRouter()

@router.get("/api/get_user/{user_id}")
async def get_user(user_id: str):
    user = db.query("users", user_id)
    user.pop("password")
    return {"user": user}
