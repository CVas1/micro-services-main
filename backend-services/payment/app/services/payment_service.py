"""Payment bisuness logic."""
from fastapi import Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from db.dependencies import get_db
from entity.payment import Payment

class PaymentService:
    """
    Payment service class.
    """
    def __init__(self, db: Session):
        self.db = db

    def get_all_payments(self) -> list[Payment]:
        """
        Retrieve all payments from the database.

        Returns:
            List[Payment]: A list of all payments.

        Raises:
            SQLAlchemyError: If there is a database error.
        """
        try:
            payments = self.db.query(Payment).all()
            return payments
        
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Database error while retrieving payments: {str(e)}")
        
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {str(e)}")


    def get_user_payments(self, email: str) -> list[Payment]:
        """
        Retrieve all payments for the specified user.

        Args:
            email (str): The email of the user whose payments are to be retrieved.

        Returns:
            List[Payment]: A list of payments for the specified user.

        Raises:
            SQLAlchemyError: If there is a database error.
            ValueError: If the email is invalid or no payments are found.
        """
        if not email or not isinstance(email, str):
            raise ValueError("Invalid email address.")
        
        try:
            payments = self.db.query(Payment).filter(Payment.user_email == email).all()
            
            if not payments:
                raise ValueError(f"No payments found for user with email: {email}")
            
            return payments
        
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Database error while retrieving payments for user {email}: {str(e)}")
        
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {str(e)}")

    def get_payment_by_id(self, payment_id: str) -> Payment:
        """
        Retrieve an payment by its ID.

        Args:
            db (Session): Database session.
            payment_id (str): The ID of the payment to retrieve.

        Returns:
            Payment: The payment with the specified ID.

        Raises:
            SQLAlchemyError: If there is a database error.
            ValueError: If the payment ID is invalid or no payment is found.
        """
        if not payment_id or not isinstance(payment_id, str):
            raise ValueError("Invalid payment ID.")
        
        try:
            payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
            
            if not payment:
                raise ValueError(f"No payment found with ID: {payment_id}")
            
            return payment
        
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Database error while retrieving payment with ID {payment_id}: {str(e)}")
        
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {str(e)}")

    def create_payment(self, payment_data: dict) -> Payment:
        """
        Create a new payment with the provided payment data.
        
        Args:
            payment_data (Dict): Dictionary containing payment details.
            
        Returns:
            Payment: The newly created payment.
            
        Raises:
            ValueError: If the input data is invalid.
            KeyError: If required keys are missing.
            SQLAlchemyError: If there is a database error.
        """
        try:
            
            required_fields = ["user_email", "order_id", "amount", "payment_method"]
            if not all(field in payment_data for field in required_fields):
                raise KeyError(f"Payment data must contain the following fields: {required_fields}")
            
            new_payment = Payment(
                user_email=payment_data["user_email"],
                order_id=payment_data["order_id"],
                amount=payment_data["amount"],
                payment_method=payment_data["payment_method"],
                transaction_id=payment_data.get("transaction_id"),
                payment_status=payment_data.get("payment_status"),
            )
            
            self.db.add(new_payment)
            self.db.commit()
            self.db.refresh(new_payment)
            
            return new_payment
        
        except KeyError as e:
            self.db.rollback()
            raise KeyError(f"Missing required field: {str(e)}")
        
        except ValueError as e:
            self.db.rollback()
            raise ValueError(f"Invalid data: {str(e)}")
        
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Database integrity error: {str(e)}")
        
        except SQLAlchemyError as e:
            self.db.rollback()
            raise SQLAlchemyError(f"Database error: {str(e)}")
        
        except Exception as e:
            self.db.rollback()
            raise Exception(f"An unexpected error occurred: {str(e)}")
        
    def update_payment_status(self, payment_id: str, new_status: str) -> Payment:
        """
        Update the status of an payment.

        Args:
            payment_id (str): The ID of the payment to update.
            new_status (str): The new status to set for the payment.

        Returns:
            Payment: The updated payment.

        Raises:
            ValueError: If the payment ID is invalid, the payment is not found, or the new status is invalid.
            SQLAlchemyError: If there is a database error.
        """
        if not payment_id or not isinstance(payment_id, str):
            raise ValueError("Invalid payment ID.")
        
        if not new_status or not isinstance(new_status, str):
            raise ValueError("Invalid status.")
        
        try:
            payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
            
            if not payment:
                raise ValueError(f"No payment found with ID: {payment_id}")
            
            payment.update_status(new_status)
            self.db.commit()
            self.db.refresh(payment)
            
            return payment
        
        except SQLAlchemyError as e:
            self.db.rollback() 
            raise SQLAlchemyError(f"Database error while updating payment status: {str(e)}")
        
        except Exception as e:
            self.db.rollback()  
            raise Exception(f"An unexpected error occurred: {str(e)}")

    def delete_payment(self, payment_id: str) -> None:
        """
        Delete an payment by its ID.

        Args:
            payment_id (str): The ID of the payment to delete.

        Returns:
            None

        Raises:
            ValueError: If the payment ID is invalid or the payment is not found.
            SQLAlchemyError: If there is a database error.
        """
        if not payment_id or not isinstance(payment_id, str):
            raise ValueError("Invalid payment ID.")
        
        try:
            payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
            if not payment:
                raise ValueError(f"No payment found with ID: {payment_id}")
            
            self.db.query(Payment).filter(Payment.id == payment_id).delete()
            self.db.commit()
        
        except SQLAlchemyError as e:
            self.db.rollback()  
            raise SQLAlchemyError(f"Database error while deleting payment: {str(e)}")
        
        except Exception as e:
            self.db.rollback()  
            raise Exception(f"An unexpected error occurred: {str(e)}")
        
    def update_order_id(self, order_id: str, payment_id: str) -> None:
        """
        Update the order ID of a payment.

        Args:
            order_id (str): The new order ID to set for the payment.

        Returns:
            None

        Raises:
            ValueError: If the order ID is invalid.
            SQLAlchemyError: If there is a database error.
        """
        if not order_id or not isinstance(order_id, str):
            raise ValueError("Invalid order ID.")
        
        try:
            payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
            
            if not payment:
                raise ValueError(f"No payment found with payment_id ID: {payment_id}")
            
            payment.update_order_id(order_id)
            self.db.commit()
        
        except SQLAlchemyError as e:
            self.db.rollback()  
            raise SQLAlchemyError(f"Database error while updating order ID: {str(e)}")
        
        except Exception as e:
            self.db.rollback()  
            raise Exception(f"An unexpected error occurred: {str(e)}")
    
    def update_transaction_id(self, transaction_id: str, payment_id: str) -> None:
        """
        Update the transaction ID of a payment.

        Args:
            transaction_id (str): The new transaction ID to set for the payment.

        Returns:
            None

        Raises:
            ValueError: If the transaction ID is invalid.
            SQLAlchemyError: If there is a database error.
        """
        if not transaction_id or not isinstance(transaction_id, str):
            raise ValueError("Invalid transaction ID.")
        
        try:
            payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
            
            if not payment:
                raise ValueError(f"No payment found with payment_id ID: {payment_id}")
            
            payment.update_transaction_id(transaction_id)
            self.db.commit()
        
        except SQLAlchemyError as e:
            self.db.rollback()  
            raise SQLAlchemyError(f"Database error while updating transaction ID: {str(e)}")
        
        except Exception as e:
            self.db.rollback()  
            raise Exception(f"An unexpected error occurred: {str(e)}")
    
    def rollback_payment(self, transaction_id: str, payment_id: str) -> None:
        """
        Rollback a payment by its transaction ID.

        Args:
            transaction_id (str): The transaction ID of the payment to rollback.

        Returns:
            None

        Raises:
            ValueError: If the transaction ID is invalid.
            SQLAlchemyError: If there is a database error.
        """
        if not transaction_id or not isinstance(transaction_id, str):
            raise ValueError("Invalid transaction ID.")
        
        try:
            payment = self.db.query(Payment).filter(Payment.transaction_id == transaction_id).first()
            
            if not payment:
                raise ValueError(f"No payment found with transaction ID: {transaction_id}")
            
            payment.update_status("Cancelled")
            self.db.commit()
        
        except SQLAlchemyError as e:
            self.db.rollback()  
            raise SQLAlchemyError(f"Database error while rolling back payment: {str(e)}")
        
        except Exception as e:
            self.db.rollback()  
            raise Exception(f"An unexpected error occurred: {str(e)}")
        
def get_payment_service() -> PaymentService:
    """
    Return an instance of the PaymentService class.

    Args:
        db (Session): Database session.

    Returns:
        PaymentService: An instance of the PaymentService class.
    """
    db_gen = get_db()         # this is a generator
    db: Session = next(db_gen)
    return PaymentService(db)