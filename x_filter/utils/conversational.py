from dotenv import load_dotenv
import os
import logging

from x_filter import Database
from x_filter.data.models.conversation import Conversation
from x_filter.data.models.filter import Filter

load_dotenv()
INTERFACE_MODE = os.getenv("INTERFACE_MODE")

db = Database()

def initialize_filter_chat(user_id: str):
    filter = Filter(id=user_id, user_id=user_id, name="Default")
    if db.exists("filters", user_id):
        db.update("filters", filter.model_dump())
    else:
        db.insert("filters", filter.model_dump())

    conversation = Conversation(id=user_id, user_id=user_id, messages=[], stage=1)
    if db.exists("conversations", user_id):
        db.update("conversations", conversation.model_dump())
    else: 
        db.insert("conversations", conversation.model_dump())
    return conversation

def add_message_to_conversation(conversation: Conversation, role: str, content: str):
    new_message = {
        "role": role,
        "content": content
    }
    conversation.messages.append(new_message)
    db.update("conversations", conversation.model_dump())

def send_message_to_user(conversation: Conversation, message: str, cache_message=True):
    """ Send a message to the user. For now, we'll just print it. """
    if cache_message:
        add_message_to_conversation(conversation, "assistant", message)

    if INTERFACE_MODE == "cli":
        with open('input.txt', 'a') as file:
            file.write("\n\nBot:\n" + message + "\n\n" + "User:\n")
        logging.info(f"Message sent to user: {message}")
    else:
        print("We only support the CLI interface at the moment.")

def clear_cached_conversation_messages(conversation: Conversation):
    conversation.messages = []
    db.update("conversations", conversation.model_dump())
