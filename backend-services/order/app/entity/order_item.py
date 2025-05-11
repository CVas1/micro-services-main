"""Order item model."""
from sqlalchemy import Column, String, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from db.base import Base
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(String(36), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False)
    order = relationship("Order", back_populates="items")

    def __init__(self, product_id: str, unit_price: float, quantity: int = 1):
        """
        Initializes a new OrderItem instance.

        :param order_id: Order ID.
        :param product_id: Product ID.
        :param unit_price: Unit price of the product.
        :param quantity: Quantity of the product (default is 1).
        """
        self.product_id = product_id
        self.unit_price = unit_price
        self.quantity = quantity
    
    def __str__(self):
        """
        Returns a readable string representation of the OrderItem instance.
        """
        return (f"<OrderItem(id={self.id}, product_id={self.product_id}, "
                f"unit_price={self.unit_price}, quantity={self.quantity})>")