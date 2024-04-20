from tests.utils import send_event
from x_filter.data.models.events import MessageEvent

event = MessageEvent(user_id="123", message="Hello, world!")

# Example of sending an event locally
local_response = send_event(event, local=True)
print(local_response.text)

# Example of sending an event externally (replace '<your-external-ip-or-ngrok-url>' with your actual URL)
# external_response = send_event(event, local=False)
# print(external_response.text)
