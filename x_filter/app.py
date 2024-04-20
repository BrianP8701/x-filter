# x_filter/app.py
# uvicorn x_filter.app:app --reload
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from x_filter import Database
from x_filter.x.wrapper import XWrapper
from x_filter.api.run_filter import router as run_filter_router, process_events
from x_filter.api.authentication import router as authentication_router
from x_filter.api.filter_settings import router as filter_settings_router
from x_filter.api.receive_event import router as receive_event_router

logging.basicConfig(filename='tests/logs.txt', filemode='a', format='\n\n%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)


shutdown_event = asyncio.Event()  # Define a shutdown signal

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start event processing loop before the application starts
    asyncio.create_task(process_events())  # Start processing events as a background task
    yield
    # Clean up after the application stops. For now we clear the entire database as we're testing
    db.dispose_instance()

app = FastAPI(lifespan=lifespan) # FastAPI app handles events

app.include_router(run_filter_router)
app.include_router(authentication_router)
app.include_router(filter_settings_router)
app.include_router(receive_event_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify domains if you want to be more restrictive
    allow_credentials=True,
    allow_methods=["*"],  # Or specify just the methods your API uses
    allow_headers=["*"],
)

db = Database() # Database follows the abstract base class to easily scale or switch databases. Rn we use SQLite locally
x_wrapper = XWrapper()

# Custom exception handler for RequestValidationError
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Log the error details
    logging.debug(f"Invalid request: {request} - Errors: {exc.errors()} - Body: {await request.body()}")
    # You can modify the response if needed, here we're just returning the default error response
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": await request.json()},
    )
