import requests
from x_filter.data.models.events import MessageEvent

def send_event(event: MessageEvent, local=True):
    """
    Sends an event to the application.

    Args:
    - event (Event): The event to send.
    - local (bool): True if sending to local server, False if sending to an external server.

    Returns:
    - Response object from the requests library.
    """
    url = "http://127.0.0.1:8000/receive-event/"
    headers = {'Content-Type': 'application/json'}
    data = event.model_dump()

    requests.post(url, json=data, headers=headers)
