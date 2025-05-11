"""Payment endpoints."""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from dtos.payment_schema import PaymentCreate, PaymentResponse  # Define these schemas
from services.payment_service import (
    get_payment_service, PaymentService
)
from api.dependencies import admin_auth_dependency, customer_auth_dependency, vendor_auth_dependency

router = APIRouter(
    prefix="/payments",
    tags=["payments"]
)

@router.get("/", response_model=list[PaymentResponse])
def list_payments(
    payment_service: PaymentService = Depends(get_payment_service)):
    """
    Retrieve all payments.
    """
    try:
        payments = payment_service.get_all_payments()
        return payments
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching payments: {str(e)}"
        )

@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: str, payment_service: PaymentService = Depends(get_payment_service)):
    """
    Retrieve a payment by its ID.
    """
    try:
        payment = payment_service.get_payment_by_id(payment_id)
        return payment
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the payment: {str(e)}"
        )

@router.get("/user/{email}", response_model=list[PaymentResponse])
def get_payments_by_user(email: str, payment_service: PaymentService = Depends(get_payment_service)):
    """
    Retrieve all payments for the specified user.
    """
    try:
        payments = payment_service.get_user_payments(email)
        return payments
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching user payments: {str(e)}"
        )

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PaymentResponse)
def create_payment_endpoint(payment: PaymentCreate, payment_service: PaymentService = Depends(get_payment_service)):
    """
    Create a new payment.
    """
    try:
        new_payment = payment_service.create_payment( payment.model_dump())
        return JSONResponse(content={"id": new_payment.id}, status_code=status.HTTP_201_CREATED)

    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the payment: {str(e)}"
        )

@router.put("/{payment_id}/status/{new_status}", response_model=PaymentResponse)
def update_payment_status_endpoint(payment_id: str, new_status: str, payment_service: PaymentService = Depends(get_payment_service)):
    """
    Update the status of a payment.
    """
    try:
        payment = payment_service.update_payment_status(payment_id, new_status)
        return payment
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the payment status: {str(e)}"
        )

@router.delete("/{payment_id}", status_code=status.HTTP_200_OK)
def delete_payment_endpoint(payment_id: str, payment_service: PaymentService = Depends(get_payment_service)):
    """
    Delete a payment by its ID.
    """
    try:
        payment_service.delete_payment(payment_id)
        return JSONResponse(content={"message": "Payment deleted successfully"}, status_code=status.HTTP_200_OK)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the payment: {str(e)}"
        )