import threading
from fastapi import FastAPI, Depends
from core import config
from db.dependencies import get_db
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from db.base import engine, Base
from entity import order, order_item
from api.endpoints import orders
from services.rabbitmq_consumer import get_consumer_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create and start the consumer thread
    Base.metadata.create_all(bind=engine)
    print("Database connected")
    consumer = get_consumer_service(queue=config.RABBITMQ_ORDERS_QUEUE)
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
app.include_router(orders.router)

@app.get("/")
async def root(db: Session = Depends(get_db)):
    return {"message": "Hello World"}