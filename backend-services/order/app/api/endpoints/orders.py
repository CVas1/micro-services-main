"""Orders endpoints."""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from api.dependencies import admin_auth_dependency, customer_auth_dependency, vendor_auth_dependency
from dtos.order_schema import OrderCreate, OrderResponse
from entity import ALLOWED_STATUSES
from services.order_service import (
    get_order_service, OrderService
)

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)
@router.get("/test")
def test_rabbit_mq():
    get_order_service().test_publish_rabbit_mq()
    return JSONResponse(content={"message": "Message published successfully"}, status_code=status.HTTP_200_OK)

@router.get("/", response_model=list[OrderResponse])
def list_orders(
    order_service: OrderService = Depends(get_order_service)
    ):
    """
    Retrieve all orders.
    """
    try:
        orders = order_service.get_all_orders()
        return orders
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching orders: {str(e)}"
        )

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    order_service: OrderService = Depends(get_order_service),
    ):
    """
    Retrieve an order by its ID.
    """
    try:
        order = order_service.get_order_by_id(order_id)
        return order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the order: {str(e)}"
        )

@router.get("/user/{email}", response_model=list[OrderResponse])
def get_orders_by_user(
    email: str, 
    order_service: OrderService = Depends(get_order_service),
    ):
    """
    Retrieve all orders for the specified user.
    """
    try:
        orders = order_service.get_user_orders(email)
        return orders
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching user orders: {str(e)}"
        )

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_order_endpoint(
    order: OrderCreate, 
    order_service: OrderService = Depends(get_order_service),
    ):
    """
    Create a new order.
    """
    try:
        new_order = order_service.create_order(order.model_dump())
        return JSONResponse(content={"id": new_order.id}, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the order: {str(e)}"
        )

@router.put("/{order_id}/status/{new_status}", response_model=OrderResponse)
def update_status(
    order_id: str,
    new_status: str,
    order_service: OrderService = Depends(get_order_service),
    ):
    """
    Update the status of an order.
    """
    if new_status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Allowed statuses: {ALLOWED_STATUSES}"
        )
    try:
        order = order_service.update_order_status(order_id, new_status)
        return order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the order status: {str(e)}"
        )

@router.put("/{order_id}/payment/{payment_id}", response_model=OrderResponse)
def update_payment(
    order_id: str, 
    payment_id: str, 
    order_service: OrderService = Depends(get_order_service),
    ):
    """
    Update the payment ID for an order.
    """
    try:
        order = order_service.update_order_payment(order_id, payment_id)
        return order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the payment ID: {str(e)}"
        )

@router.put("/{order_id}/delivery", response_model=OrderResponse)
def update_delivery_date(
    order_id: str, 
    order_service: OrderService = Depends(get_order_service),
    ):
    """
    Update the delivery date for an order.
    """
    try:
        order = order_service.update_order_delivery_date(order_id)
        return order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the delivery date: {str(e)}"
        )

@router.delete("/{order_id}", status_code=status.HTTP_200_OK)
def delete_order_endpoint(
    order_id: str, 
    order_service: OrderService = Depends(get_order_service),
    ):
    """
    Delete an order by its ID.
    """
    try:
        order_service.delete_order(order_id)
        return JSONResponse(content={"message": "Order deleted successfully"}, status_code=status.HTTP_200_OK)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the order: {str(e)}"
        )