"""
FastAPI application for managing a list of items.
"""
import threading
from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers import order_router
from services.event_consumer import get_consumer_service
import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create and start the consumer thread
    consumer = get_consumer_service(queue=config.RABBITMQ_ORCHESTRATION_QUEUE)
    thread = threading.Thread(target=consumer.start_consuming, daemon=True)
    thread.start()
    print("Consumer thread started.")
    try:
        yield
    finally:
        # Shutdown: Signal the consumer to stop and wait for the thread to exit
        consumer.stop_consuming()
        thread.join(timeout=5)
        print("Consumer stopped.")


app = FastAPI(lifespan=lifespan)
app.include_router(order_router.router)

@app.get("/")
def read_root():
    """
    A simple health-check endpoint.
    """
    return {"message": "Orchestration Service is running."}
