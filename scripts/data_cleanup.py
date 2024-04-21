# python scripts/data_cleanup.py
from x_filter.data import Database

db = Database()

conversation = db.query("conversations", "brian")
message = {
    "role": "assistant",
    "content": "Hello! I am X-Filter, a bot designed to assist users in finding specific content on X (Twitter). Can you tell me what you are looking for? Are you looking for users, tweets or reports (a summary of a collection of tweets)?"
}

conversation["messages"] = [message]
conversation["stage"] = 1

db.update("conversations", conversation)
