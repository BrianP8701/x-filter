# scripts/cli_interface.py
# python scripts/cli_interface.py
import os
import shutil

from tests.utils import send_event
from x_filter.data.models.events import MessageEvent
from x_filter import Database
from x_filter.utils.conversational import initialize_filter_chat

db = Database()

filter_id = "test123"

def main(user_id):
    if os.path.exists('input.txt'):
        os.remove('input.txt')
    with open('input.txt', 'w') as file:
        file.write("\n\nUser:\n")

    print("Welcome to the CLI interface for X-Filter. Type 'exit' to save and exit.")

    while True:
        print("Please enter your message in the input.txt file. Press enter in the terminal when your done.")

        user_decision = input()  # Wait for the user to press Enter or type 'exit'

        if user_decision.lower() == 'exit':
            save_and_exit()
            break

        with open('input.txt', 'r') as file:
            content = file.read()
            last_user_index = content.rfind("User:\n") + len("User:\n")
            user_input = content[last_user_index:]

        # Simulate sending event and receiving a response
        event = MessageEvent(user_id=user_id, message=user_input.strip(), filter_id=filter_id)
        send_event(event, local=True)  # Assuming response is JSON and has a 'response' key
        print("Send message to server. Waiting for response...\n")

def save_and_exit():
    destination_folder = 'tests/saved_runs'
    os.makedirs(destination_folder, exist_ok=True)
    file_name = 'run_{}.txt'
    i = 0
    while os.path.exists(os.path.join(destination_folder, file_name.format(i))):
        i += 1
    final_path = os.path.join(destination_folder, file_name.format(i))
    shutil.move('input.txt', final_path)
    print(f"Saved this file to {final_path}. Closing.")

    db.clear_table("events", "CONFIRM")
    db.clear_table("conversations", "CONFIRM")
    db.clear_table("filters", "CONFIRM")

if __name__ == "__main__":
    initialize_filter_chat("test123")
    main("test123")
