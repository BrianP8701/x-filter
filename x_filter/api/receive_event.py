# x_filter/api/receive_event.py
from fastapi import APIRouter
import logging

from x_filter import Database
from x_filter.data.models.events import MessageEvent
from x_filter.ai.main import handle_user_message
from x_filter.data.models.conversation import Conversation
from x_filter.data.models.filter import Filter

db = Database()
router = APIRouter()

@router.post("/receive-event/")
async def receive_event(data: MessageEvent):
    """
    This function is called when a user sends a message to the bot.
    
    The filter_chat's conversation and filter id is always the user id
    When a filter gets created the filter and conversation get a unique id and get saved, and the userid objects get cleared
    
    In the filter_choose if a user doesen't have a filter selected and sends a message... we do nothing.
    """
    logging.info(f"Received event: {data}")
    if db.exists("conversations", data.filter_id):
        conversation = Conversation(**db.query("conversations", data.filter_id))
        filter = Filter(**db.query("filters", data.filter_id))
    else:
        return
    
    return await handle_user_message(conversation, data, filter)
