"""Order model."""
from sqlalchemy import Column, String, TIMESTAMP, func, Float, Enum
from entity.order_item import OrderItem
from db.base import Base
from sqlalchemy.orm import relationship
from . import generate_uuid, ALLOWED_STATUSES

class Order(Base):
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, index=True, default=generate_uuid)
    payment_id = Column(String(36), nullable=True)
    user_email = Column(String(100), nullable=False, index=True)
    vendor_email = Column(String(100), nullable=False)
    description = Column(String(255))
    order_date = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)
    delivery_date = Column(TIMESTAMP, nullable=True)
    total_price = Column(Float, nullable=False)
    delivery_address = Column(String(255), nullable=False)
    transaction_id = Column(String(36), nullable=True)
    status = Column(Enum(*ALLOWED_STATUSES), nullable=False, default="Pending")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __init__(self, user_email: str, vendor_email: str, total_price: float, delivery_address: str,
                 description: str = None, delivery_date = None, status: str = "Pending", transaction_id: str = None):
        """
        Initializes a new Order instance.

        :param email: Email of the customer placing the order.
        :param vendor_email: Email of the vendor fulfilling the order.
        :param total_price: Total price of the order.
        :param delivery_address: Delivery address for the order.
        :param description: Optional description for the order.
        :param delivery_date: Optional scheduled delivery date.
        :param status: Order status (default is "Pending").
        """
        self.user_email = user_email
        self.vendor_email = vendor_email
        self.total_price = total_price
        self.delivery_address = delivery_address
        self.description = description
        self.delivery_date = delivery_date
        self.status = status
        self.transaction_id = transaction_id

    def __str__(self):
        """
        Returns a readable string representation of the Order instance.
        """
        return (f"<Order(id={self.id}, email={self.email}, payment_id={self.payment_id}, vendor_email={self.vendor_email}, "
                f"total_price={self.total_price}, status={self.status})>")
    
    def update_delivery_address(self, new_address: str):
        """
        Update the delivery address for the order.

        :param new_address: New delivery address.
        """
        self.delivery_address = new_address

    def update_delivery_date(self, new_date):
        """
        Update the delivery date for the order.

        :param new_date: New delivery date.
        """
        self.delivery_date = new_date

    def update_status(self, new_status: str):
        """
        Update the status of the order.

        :param new_status: New status for the order.
        """
        if new_status not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid status. Allowed statuses: {ALLOWED_STATUSES}")
        self.status = new_status

    def update_payment(self, payment_id: str):
        """
        Update the payment ID for the order.

        :param payment_id: Payment ID.
        """
        self.payment_id = payment_id
    def add_item(self, product_id: str, unit_price: float, quantity: int = 1):
        """
        Add an item to the order.

        :param product_id: Product ID.
        :param unit_price: Unit price of the product.
        :param quantity: Quantity of the product (default is 1).
        """
        self.items.append(OrderItem(product_id=product_id, unit_price=unit_price, quantity=quantity))

    def add_items(self, items_list: list):
        """
        Add multiple items to the order.

        :param items_list: List of dictionaries, where each dictionary should contain:
                        - product_id: Product ID.
                        - unit_price: Unit price of the product.
                        - quantity: Optional quantity (default is 1 if not provided).
        """
        for item in items_list:
            self.items.append(
                OrderItem(
                    product_id=item["product_id"],
                    unit_price=item["unit_price"],
                    quantity=item.get("quantity", 1)
                )
            )