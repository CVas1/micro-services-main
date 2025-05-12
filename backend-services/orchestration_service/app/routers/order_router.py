from fastapi import APIRouter, Depends, HTTPException, Request
from routers import PAYMENT_METHODS
from services.saga_orchestrator import SagaOrchestrator, get_saga_orchestrator
from models.order import OrderCreateRequest, OrderResponse
from logger import logger
from routers.auth_dependencies import authenticate_user

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/")
def health_check():
    logger.log("Health check endpoint accessed.")
    return {"status": "OK"}

@router.post("/create_order")
async def create_order(
    order_req: OrderCreateRequest,
    request: Request,
    user_type: str = Depends(authenticate_user),
    orchestrator: SagaOrchestrator = Depends(get_saga_orchestrator),
):  
    logger.log(f"Order creation attempt for user: {getattr(order_req, 'user_email', 'unknown')}")
    auth_header = request.headers.get("Authorization")
    
    payment_method = order_req.payment_method
    if payment_method not in PAYMENT_METHODS:
        logger.log(f"Invalid payment method: {payment_method}", level="ERROR")
        raise HTTPException(status_code=400, detail="Invalid payment method")

    order_id = orchestrator.start_order_saga(order_req, token=auth_header)  
    logger.log(f"Order creation started for user: {getattr(order_req, 'user_email', 'unknown')}")
    return {
        "status": "success",
        "message": "Order creation started",
        "data": None}

@router.post("/cancel_order")
async def cancel_order(
    order_id: str,
    request: Request,
    user_type: str = Depends(authenticate_user),
    orchestrator: SagaOrchestrator = Depends(get_saga_orchestrator),
):
    auth_header = request.headers.get("Authorization")
    
    orchestrator.cancel_order_saga(order_id, token=auth_header)
    return {"message": "Order cancellation started"}