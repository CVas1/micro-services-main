"""Payment endpoints."""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from dtos.payment_schema import PaymentCreate, PaymentResponse
from services.payment_service import get_payment_service, PaymentService
from api.dependencies import admin_auth_dependency, any_user_auth_dependency
from logger import logger

router = APIRouter(
    prefix="/payments",
    tags=["payments"]
)

@router.get("/", response_model=list[PaymentResponse], dependencies=[Depends(admin_auth_dependency)])
def list_payments(payment_service: PaymentService = Depends(get_payment_service)):
    """
    Retrieve all payments. Only accessible by admin users.
    """
    try:
        logger.info("Fetching all payments")
        payments = payment_service.get_all_payments()
        logger.info(f"Retrieved {len(payments)} payments")
        return payments
    except Exception as e:
        logger.error(f"Failed to fetch payments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching payments: {str(e)}"
        )

@router.get("/{payment_id}", response_model=PaymentResponse, dependencies=[Depends(any_user_auth_dependency)])
def get_payment(payment_id: str, payment_service: PaymentService = Depends(get_payment_service)):
    """
    Retrieve a payment by its ID.
    """
    try:
        logger.info(f"Fetching payment with ID: {payment_id}")
        payment = payment_service.get_payment_by_id(payment_id)
        logger.info(f"Payment retrieved: {payment.id}")
        return payment
    except ValueError as e:
        logger.warning(f"Payment not found: {payment_id} | {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to fetch payment {payment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching the payment: {str(e)}"
        )

@router.get("/user/{email}", response_model=list[PaymentResponse], dependencies=[Depends(any_user_auth_dependency)])
def get_payments_by_user(email: str, payment_service: PaymentService = Depends(get_payment_service)):
    """
    Retrieve all payments for the specified user.
    """
    try:
        logger.info(f"Fetching payments for user: {email}")
        payments = payment_service.get_user_payments(email)
        logger.info(f"Retrieved {len(payments)} payments for user: {email}")
        return payments
    except ValueError as e:
        logger.warning(f"No payments found for user {email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to fetch payments for user {email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while fetching user payments: {str(e)}"
        )

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PaymentResponse, dependencies=[Depends(admin_auth_dependency)])
def create_payment_endpoint(payment: PaymentCreate, payment_service: PaymentService = Depends(get_payment_service)):
    """
    Create a new payment.
    """
    try:
        logger.info(f"Creating payment with data: {payment.dict()}")
        new_payment = payment_service.create_payment(payment.model_dump())
        logger.info(f"Payment created with ID: {new_payment.id}")
        return JSONResponse(content={"id": new_payment.id}, status_code=status.HTTP_201_CREATED)
    except KeyError as e:
        logger.warning(f"Missing field in payment creation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        logger.warning(f"Invalid value in payment creation: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the payment: {str(e)}"
        )

@router.put("/{payment_id}/status/{new_status}", response_model=PaymentResponse, dependencies=[Depends(admin_auth_dependency)])
def update_payment_status_endpoint(payment_id: str, new_status: str, payment_service: PaymentService = Depends(get_payment_service)):
    """
    Update the status of a payment.
    """
    try:
        logger.info(f"Updating payment {payment_id} to status: {new_status}")
        payment = payment_service.update_payment_status(payment_id, new_status)
        logger.info(f"Payment {payment_id} status updated to {new_status}")
        return payment
    except ValueError as e:
        logger.warning(f"Payment {payment_id} not found or invalid status: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to update payment {payment_id} status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the payment status: {str(e)}"
        )

@router.delete("/{payment_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(admin_auth_dependency)])
def delete_payment_endpoint(payment_id: str, payment_service: PaymentService = Depends(get_payment_service)):
    """
    Delete a payment by its ID.
    """
    try:
        logger.info(f"Deleting payment with ID: {payment_id}")
        payment_service.delete_payment(payment_id)
        logger.info(f"Payment {payment_id} deleted successfully")
        return JSONResponse(content={"message": "Payment deleted successfully"}, status_code=status.HTTP_200_OK)
    except ValueError as e:
        logger.warning(f"Payment not found for deletion: {payment_id} | {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to delete payment {payment_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the payment: {str(e)}"
        )
