"""
FastAPI application for managing a list of items.
"""
import threading
from fastapi import FastAPI, Security, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from contextlib import asynccontextmanager
from fastapi.openapi.utils import get_openapi
from routers import order_router, logs
from services.event_consumer import get_consumer_service
import config
from logger import logger

# Extract raw Authorization header
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

async def get_token(authorization: str = Security(api_key_header)) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    # You can add JWT decoding/validation here
    return authorization

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

app = FastAPI(
    lifespan=lifespan,
    title="Orchestration Service API",
    description="API for managing orders and viewing logs",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Custom OpenAPI schema to support raw Authorization header
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization"
        }
    }
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"APIKeyAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Include routers
app.include_router(order_router.router, dependencies=[Security(get_token)])
app.include_router(logs.router, dependencies=[Security(get_token)])

@app.get("/")
def read_root():
    """
    A simple health-check endpoint.
    """
    logger.log("Root endpoint accessed.")
    return {"message": "Orchestration Service is running."}

# Optional: Protected test endpoint
@app.get("/protected")
def protected(token: str = Security(get_token)):
    return {"token_received": token}
