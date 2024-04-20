# x_filter/api/run_filter.py
from fastapi import APIRouter
import asyncio
from pydantic import BaseModel

from x_filter import Database
from x_filter.data.models.filter import Filter

db = Database()
router = APIRouter()

event_queue = asyncio.Queue() # Queue for events

class RunFilterParams(BaseModel):
    filter_id: str
    
@router.post("/run-filter/")
async def run_filter(data: RunFilterParams):
    await event_queue.put(data.filter_id)
    return {"message": "Event added to the queue"}

# Event processing loop
async def process_events():
    while True:
        filter_id = await event_queue.get()
        asyncio.create_task(run_filter(filter_id))

# Process an event
async def run_filter(filter_id: str):
    event_queue.task_done()