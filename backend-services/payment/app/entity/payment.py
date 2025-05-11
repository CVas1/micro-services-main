"""Payment model."""
from sqlalchemy import Column, String, TIMESTAMP, func, Float, Enum
from db.base import Base
from . import PAYMENT_METHODS, PAYMENT_STATUSES, generate_uuid


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_email = Column(String(100), nullable=False, index=True)
    order_id = Column(String(36), nullable=True, unique=True, index=True)
    amount = Column(Float, nullable=False)
    payment_method = Column(Enum(*PAYMENT_METHODS), nullable=False) 
    payment_status = Column(Enum(*PAYMENT_STATUSES), nullable=False, default="Pending")
    transaction_id = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)

    def __init__(self, user_email: str, order_id: str, amount: float, payment_method: str, payment_status: str = "Pending", transaction_id: str = None):
        """
        Initializes a new Payment instance.

        :param user_email: User email.
        :param order_id: Order ID.
        :param amount: Payment amount.
        :param payment_method: Payment method.
        :param payment_status: Payment status (default is "Pending").
        :param transaction_id: Payment transaction ID.
        """
        self.user_email = user_email
        self.order_id = order_id
        self.amount = amount
        self.payment_method = payment_method
        self.payment_status = payment_status
        self.transaction_id = transaction_id
    
    def __str__(self):
        """
        Returns a readable string representation of the Payment instance.
        """
        return (f"<Payment(id={self.id}, user_email={self.user_email} order_id={self.order_id}, amount={self.amount}, "
                f"payment_method={self.payment_method}, payment_status={self.payment_status})>")

    def update_status(self, new_status: str):
        """
        Update the status of the payment.

        :param new_status: The new status to set for the payment.
        """
        self.payment_status = new_status
        return self
    
    def update_order_id(self, order_id: str):
        """
        Update the order ID of the payment.

        :param order_id: The new order ID to set for the payment.
        """
        self.order_id = order_id
        return self
    
    def update_transaction_id(self, transaction_id: str):
        """
        Update the transaction ID of the payment.

        :param transaction_id: The new transaction ID to set for the payment.
        """
        self.transaction_id = transaction_id
        return self