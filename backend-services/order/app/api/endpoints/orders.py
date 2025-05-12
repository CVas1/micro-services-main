"""Orders endpoints."""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from api.dependencies import admin_auth_dependency, customer_auth_dependency, vendor_auth_dependency
from dtos.order_schema import OrderCreate, OrderResponse
from entity import ALLOWED_STATUSES
from services.order_service import (
    get_order_service, OrderService
)
from logger import logger

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)

@router.get("/", response_model=list[OrderResponse], dependencies=[Depends(admin_auth_dependency)])
def list_orders(
    order_service: OrderService = Depends(get_order_service),
    ):
    """
    Retrieve all orders. admin only.
    """
    try:
        logger.info("Listing all orders")
        orders = order_service.get_all_orders()
        return orders
    except Exception as e:
        logger.error(f"Error fetching orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching orders: {str(e)}"
        )

@router.get("/{order_id}", response_model=OrderResponse, dependencies=[Depends(customer_auth_dependency)])
def get_order(
    order_id: str,
    order_service: OrderService = Depends(get_order_service),
    ):
    """
    Retrieve an order by its ID. admin and customer only.
    """
    try:
        logger.info(f"Fetching order with ID: {order_id}")
        order = order_service.get_order_by_id(order_id)
        return order
    except ValueError as e:
        logger.warning(f"Order not found: {order_id} - {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the order: {str(e)}"
        )

@router.get("/user/{email}", response_model=list[OrderResponse], dependencies=[Depends(customer_auth_dependency)])
def get_orders_by_user(
    email: str, 
    order_service: OrderService = Depends(get_order_service),
    ):
    """
    Retrieve all orders for the specified user. admin and customer only.
    """
    try:
        logger.info(f"Fetching orders for user: {email}")
        orders = order_service.get_user_orders(email)
        return orders
    except ValueError as e:
        logger.warning(f"Orders not found for user: {email} - {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching orders for user {email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching user orders: {str(e)}"
        )

@router.get("/vendor/{vendor_id}", response_model=list[OrderResponse], dependencies=[Depends(vendor_auth_dependency)])
def get_orders_by_vendor(
    vendor_id: str,
    order_service: OrderService = Depends(get_order_service),
    ):
    """
    Retrieve all orders for the specified vendor. admin and vendor only.
    """
    try:
        logger.info(f"Fetching orders for vendor: {vendor_id}")
        orders = order_service.get_vendor_orders(vendor_id)
        return orders
    except ValueError as e:
        logger.warning(f"Orders not found for vendor: {vendor_id} - {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching orders for vendor {vendor_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching vendor orders: {str(e)}"
        )

@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(customer_auth_dependency)])
def create_order_endpoint(
    order: OrderCreate, 
    order_service: OrderService = Depends(get_order_service),
    ):
    """
    Create a new order. customer and admin only.
    """
    try:
        logger.info(f"Creating order for user: {order.email}")
        new_order = order_service.create_order(order.model_dump())
        logger.info(f"Order created with ID: {new_order.id}")
        return JSONResponse(content={"id": new_order.id}, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the order: {str(e)}"
        )

@router.put("/{order_id}/status/{new_status}", response_model=OrderResponse, dependencies=[Depends(vendor_auth_dependency)])
def update_status(
    order_id: str,
    new_status: str,
    order_service: OrderService = Depends(get_order_service),
    ):
    """
    Update the status of an order. vendor and admin only.
    """
    if new_status not in ALLOWED_STATUSES:
        logger.warning(f"Invalid status update attempted: {new_status}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Allowed statuses: {ALLOWED_STATUSES}"
        )
    try:
        logger.info(f"Updating order {order_id} to status {new_status}")
        order = order_service.update_order_status(order_id, new_status)
        return order
    except ValueError as e:
        logger.warning(f"Order not found for status update: {order_id} - {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating order status {order_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the order status: {str(e)}"
        )

@router.put("/{order_id}/payment/{payment_id}", response_model=OrderResponse, dependencies=[Depends(customer_auth_dependency)])
def update_payment(
    order_id: str, 
    payment_id: str, 
    order_service: OrderService = Depends(get_order_service),
    ):
    """
    Update the payment ID for an order. customer and admin only.
    """
    try:
        logger.info(f"Updating payment for order {order_id} to payment ID {payment_id}")
        order = order_service.update_order_payment(order_id, payment_id)
        return order
    except ValueError as e:
        logger.warning(f"Order not found for payment update: {order_id} - {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating payment for order {order_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the payment ID: {str(e)}"
        )

@router.put("/{order_id}/delivery", response_model=OrderResponse, dependencies=[Depends(customer_auth_dependency)])
def update_delivery_date(
    order_id: str, 
    order_service: OrderService = Depends(get_order_service),
    ):
    """
    Update the delivery date for an order. customer and admin only.
    """
    try:
        logger.info(f"Updating delivery date for order {order_id}")
        order = order_service.update_order_delivery_date(order_id)
        return order
    except ValueError as e:
        logger.warning(f"Order not found for delivery update: {order_id} - {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating delivery date for order {order_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the delivery date: {str(e)}"
        )

@router.delete("/{order_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(customer_auth_dependency)])
def delete_order_endpoint(
    order_id: str, 
    order_service: OrderService = Depends(get_order_service),
    ):
    """
    Delete an order by its ID. customer and admin only.
    """
    try:
        logger.info(f"Deleting order {order_id}")
        order_service.delete_order(order_id)
        logger.info(f"Order {order_id} deleted successfully")
        return JSONResponse(content={"message": "Order deleted successfully"}, status_code=status.HTTP_200_OK)
    except ValueError as e:
        logger.warning(f"Order not found for deletion: {order_id} - {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting order {order_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the order: {str(e)}"
        )