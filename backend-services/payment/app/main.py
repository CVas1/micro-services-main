import threading
from core import config
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from db.dependencies import get_db
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from db.base import engine, Base
from entity import payment
from api.endpoints import payments, logs
from services.rabbitmq_consumer import get_consumer_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create and start the consumer thread
    Base.metadata.create_all(bind=engine)
    print("Database connected")
    consumer = get_consumer_service(queue=config.RABBITMQ_PAYMENT_QUEUE)
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(payments.router)
app.include_router(logs.router)
@app.get("/")
async def root(db: Session = Depends(get_db)):
    return {"message": "Hello World"}