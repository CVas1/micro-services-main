from pydantic import BaseModel

class ProductSagaState:
    def __init__(self, transaction_id: str, product_id: str, quantity: int):
        """
        Represents the state of a Product in a Saga.

        :param transaction_id: The unique transaction ID for the Saga.
        :param product_id: The ID of the product.
        :param quantity: The quantity of the product.
        """
        self.transaction_id = transaction_id
        self.product_id = product_id
        self.quantity = quantity

    def dict(self):
        """
        Returns the attributes of the ProductSagaState as a dictionary.
        """
        return {
            "transaction_id": self.transaction_id,
            "product_id": self.product_id,
            "quantity": self.quantity
        }
class OrderSagaState:
    def __init__(self, transaction_id: str, description: str, user_email: str, vendor_email: str,
                  delivery_address: str, payment_method: str, status: str = "Pending", items: list = None
                  ,payment_id: str = None):
        """
        Represents the state of an Order in a Saga.

        :param transaction_id: The unique transaction ID for the Saga.
        :param user_email: The email of the user who placed the order.
        :param vendor_email: The email of the vendor fulfilling the order.
        :param delivery_address: The delivery address for the order.
        """
        self.transaction_id = transaction_id
        self.description = description
        self.user_email = user_email
        self.vendor_email = vendor_email
        self.delivery_address = delivery_address
        self.status = status
        self.items = items or []
        self.payment_method = payment_method
        self.payment_id = payment_id

    def total_price(self) -> float:
        total = 0.0
        for item in self.items:
            if isinstance(item, dict):
                qty  = item.get("quantity", 0)
                unit = item.get("unit_price", 0)
            else:
                qty  = getattr(item, "quantity", 0)
                unit = getattr(item, "unit_price", 0)
            total += qty * unit
        return total
    
    def dict(self):
        """
        Returns the attributes of the OrderSagaState as a dictionary.
        """
        return {
            "transaction_id": self.transaction_id,
            "description": self.description,
            "user_email": self.user_email,
            "vendor_email": self.vendor_email,
            "delivery_address": self.delivery_address,
            "status": self.status,
            "items": [item.dict() for item in self.items],
            "payment_method": self.payment_method,
            "payment_id": self.payment_id
        }
    
class PaymentSagaState:
    def __init__(self, transaction_id: str, user_email: str, amount: float, payment_method: str, payment_status: str = "Pending", order_id: str = None):
        """
        Represents the state of a Payment in a Saga.

        :param transaction_id: The unique transaction ID for the Saga.
        :param payment_info: The payment information.
        """
        self.transaction_id = transaction_id
        self.user_email = user_email
        self.order_id = order_id
        self.amount = amount
        self.payment_method = payment_method
        self.payment_status = payment_status

    def dict(self):
        """
        Returns the attributes of the PaymentSagaState as a dictionary.
        """
        return {
            "transaction_id": self.transaction_id,
            "user_email": self.user_email,
            "order_id": self.order_id,
            "amount": self.amount,
            "payment_method": self.payment_method,
            "payment_status": self.payment_status
        }


class SagaEvent(BaseModel):
    """
    Base class for all Saga events.
    """
    event: str
    data: dict
    