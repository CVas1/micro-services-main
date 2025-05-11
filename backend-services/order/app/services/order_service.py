"""Order bisuness logic."""
from datetime import datetime
from fastapi import Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from core import config
from services.rabbitmq_publisher import get_publisher_service
from entity.order import Order
from entity.order_item import OrderItem
from db.dependencies import get_db

class OrderService:
    """
    Service class for handling order-related operations.
    """
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_orders(self) -> list[Order]:
        """
        Retrieve all orders from the database, including their associated items.

        Returns:
            List[Order]: A list of all orders.

        Raises:
            SQLAlchemyError: If there is a database error.
        """
        try:
            orders = self.db.query(Order).options(joinedload(Order.items)).all()
            return orders
        
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Database error while retrieving orders: {str(e)}")
        
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {str(e)}")


    def get_user_orders(self, email: str) -> list[Order]:
        """
        Retrieve all orders for the specified user.

        Args:
            email (str): The email of the user whose orders are to be retrieved.

        Returns:
            List[Order]: A list of orders for the specified user.

        Raises:
            SQLAlchemyError: If there is a database error.
            ValueError: If the email is invalid or no orders are found.
        """
        if not email or not isinstance(email, str):
            raise ValueError("Invalid email address.")
        
        try:
            orders = self.db.query(Order).filter(Order.user_email == email).options(joinedload(Order.items)).all()
            
            if not orders:
                raise ValueError(f"No orders found for user with email: {email}")
            
            return orders
        
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Database error while retrieving orders for user {email}: {str(e)}")
        
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {str(e)}")

    def get_order_by_id(self, order_id: str) -> Order:
        """
        Retrieve an order by its ID.

        Args:
            order_id (str): The ID of the order to retrieve.

        Returns:
            Order: The order with the specified ID.

        Raises:
            SQLAlchemyError: If there is a database error.
            ValueError: If the order ID is invalid or no order is found.
        """
        if not order_id or not isinstance(order_id, str):
            raise ValueError("Invalid order ID.")
        
        try:
            order = self.db.query(Order).filter(Order.id == order_id).options(joinedload(Order.items)).first()
            
            if not order:
                raise ValueError(f"No order found with ID: {order_id}")
            
            return order
        
        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Database error while retrieving order with ID {order_id}: {str(e)}")
        
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {str(e)}")

    def create_order(self, order_data: dict, transaction_id: str) -> Order:
        """
        Create a new order with the provided order data.
        
        Args:
            order_data (Dict): Dictionary containing order details.
            
        Returns:
            Order: The newly created order.
            
        Raises:
            ValueError: If the input data is invalid.
            KeyError: If required keys are missing.
            SQLAlchemyError: If there is a database error.
        """
        try:
            items_data = order_data.pop("items", [])
            
            if not isinstance(items_data, list):
                raise ValueError("Items data must be a list.")
            
            if not isinstance(transaction_id, str):
                raise ValueError("Transaction ID must be a string.")

            total_price = 0
            for item in items_data:
                if not all(key in item for key in ["quantity", "unit_price", "product_id"]):
                    raise KeyError("Each item must contain 'quantity', 'unit_price', and 'product_id'.")
                if not isinstance(item["quantity"], int) or item["quantity"] <= 0:
                    raise ValueError("Quantity must be a positive integer.")
                if not isinstance(item["unit_price"], (int, float)) or item["unit_price"] < 0:
                    raise ValueError("Unit price must be a non-negative number.")
                total_price += item["quantity"] * item["unit_price"]
            
            required_fields = ["user_email", "vendor_email", "delivery_address"]
            if not all(field in order_data for field in required_fields):
                raise KeyError(f"Order data must contain the following fields: {required_fields}")
            
            new_order = Order(
                user_email=order_data["user_email"],
                vendor_email=order_data["vendor_email"],
                delivery_address=order_data["delivery_address"],
                description=order_data.get("description"),
                status=order_data.get("status", "Pending"),
                total_price=total_price,
                transaction_id=transaction_id,
            )
            
            self.db.add(new_order)
            new_order.add_items(items_data)
            self.db.commit()
            self.db.refresh(new_order)
            return new_order
        
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
        
    def update_order_status(self, order_id: str, new_status: str) -> Order:
        """
        Update the status of an order.

        Args:
            order_id (str): The ID of the order to update.
            new_status (str): The new status to set for the order.

        Returns:
            Order: The updated order.

        Raises:
            ValueError: If the order ID is invalid, the order is not found, or the new status is invalid.
            SQLAlchemyError: If there is a database error.
        """
        if not order_id or not isinstance(order_id, str):
            raise ValueError("Invalid order ID.")
        
        if not new_status or not isinstance(new_status, str):
            raise ValueError("Invalid status.")
        
        try:
            order = self.db.query(Order).filter(Order.id == order_id).first()
            
            if not order:
                raise ValueError(f"No order found with ID: {order_id}")
            
            order.update_status(new_status)
            self.db.commit()
            self.db.refresh(order)
            return order
        
        except SQLAlchemyError as e:
            self.db.rollback() 
            raise SQLAlchemyError(f"Database error while updating order status: {str(e)}")
        
        except Exception as e:
            self.db.rollback()  
            raise Exception(f"An unexpected error occurred: {str(e)}")

    def update_order_payment(self, order_id: str, payment_id: str) -> Order:
        """
        Update the payment ID for an order.

        Args:
            order_id (str): The ID of the order to update.
            payment_id (str): The new payment ID to set for the order.

        Returns:
            Order: The updated order.

        Raises:
            ValueError: If the order ID is invalid, the order is not found, or the payment ID is invalid.
            SQLAlchemyError: If there is a database error.
        """
        if not order_id or not isinstance(order_id, str):
            raise ValueError("Invalid order ID.")
        
        if not payment_id or not isinstance(payment_id, str):
            raise ValueError("Invalid payment ID.")
        
        try:
            order = self.db.query(Order).filter(Order.id == order_id).first()
            
            if not order:
                raise ValueError(f"No order found with ID: {order_id}")
            
            order.update_payment(payment_id)
            self.db.commit()
            self.db.refresh(order)
            
            return order
        
        except SQLAlchemyError as e:
            self.db.rollback()  
            raise SQLAlchemyError(f"Database error while updating payment ID: {str(e)}")
        
        except Exception as e:
            self.db.rollback() 
            raise Exception(f"An unexpected error occurred: {str(e)}")

    def update_order_delivery_date(self, order_id: str) -> Order:
        """
        Update the delivery date for an order.

        Args:
            order_id (str): The ID of the order to update.

        Returns:
            Order: The updated order.

        Raises:
            ValueError: If the order ID is invalid or the order is not found.
            SQLAlchemyError: If there is a database error.
        """
        if not order_id or not isinstance(order_id, str):
            raise ValueError("Invalid order ID.")
        
        try:
            order = self.db.query(Order).filter(Order.id == order_id).first()
            
            if not order:
                raise ValueError(f"No order found with ID: {order_id}")
            order.update_delivery_date(datetime.now())
            self.db.commit()
            self.db.refresh(order)
            
            return order
        
        except SQLAlchemyError as e:
            self.db.rollback()  
            raise SQLAlchemyError(f"Database error while updating delivery date: {str(e)}")
        
        except Exception as e:
            self.db.rollback()  
            raise Exception(f"An unexpected error occurred: {str(e)}")

    def update_order_address(self, order_id: str, new_address: str) -> Order:
        """
        Update the delivery address for an order.
        
        Args:
            order_id (str): The ID of the order to update.
            new_address (str): The new delivery address to set for the order.
            
        Returns:
            Order: The updated order.

        Raises:
            ValueError: If the order ID is invalid, the order is not found, or the new address is invalid.
            SQLAlchemyError: If there is a database error.
        """
        if not order_id or not isinstance(order_id, str):
            raise ValueError("Invalid order ID.")
        
        if not new_address or not isinstance(new_address, str):
            raise ValueError("Invalid delivery address.")
        
        try:
            order = self.db.query(Order).filter(Order.id == order_id).first()
            
            if not order:
                raise ValueError(f"No order found with ID: {order_id}")
            
            order.update_delivery_address(new_address)
            self.db.commit()
            self.db.refresh(order)
            
            return order
        
        except SQLAlchemyError as e:
            self.db.rollback()  
            raise SQLAlchemyError(f"Database error while updating delivery address: {str(e)}")
        
        except Exception as e:
            self.db.rollback()  
            raise Exception(f"An unexpected error occurred: {str(e)}")
        

    def delete_order(self, order_id: str) -> None:
        """
        Delete an order by its ID.

        Args:
            order_id (str): The ID of the order to delete.

        Returns:
            None

        Raises:
            ValueError: If the order ID is invalid or the order is not found.
            SQLAlchemyError: If there is a database error.
        """
        if not order_id or not isinstance(order_id, str):
            raise ValueError("Invalid order ID.")
        
        try:
            order = self.db.query(Order).filter(Order.id == order_id).first()
            if not order:
                raise ValueError(f"No order found with ID: {order_id}")
            
            self.db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()
            
            self.db.query(Order).filter(Order.id == order_id).delete()
            self.db.commit()
        
        except SQLAlchemyError as e:
            self.db.rollback()  
            raise SQLAlchemyError(f"Database error while deleting order: {str(e)}")
        
        except Exception as e:
            self.db.rollback()  
            raise Exception(f"An unexpected error occurred: {str(e)}")
    
    def rollback_order(self, transaction_id: str) -> None:
        """ change order status to canceled """
        if not transaction_id or not isinstance(transaction_id, str):
            raise ValueError("Invalid transaction ID.")
        
        try:
            order = self.db.query(Order).filter(Order.transaction_id == transaction_id).first()
            if not order:
                raise ValueError(f"No order found with transaction ID: {transaction_id}")
            
            order.update_status("Canceled")
            self.db.commit()
        
        except SQLAlchemyError as e:
            self.db.rollback()  
            raise SQLAlchemyError(f"Database error while rolling back order: {str(e)}")
        
        except Exception as e:
            self.db.rollback()  
            raise Exception(f"An unexpected error occurred: {str(e)}")

    def test_publish_rabbit_mq(self):
        """
        Test RabbitMQ connection and publish a message.
        """
        try:
            # Create a connection to RabbitMQ
            publisher = get_publisher_service()
            publisher.connect()
            
            # Publish a test message to the 'test' queue
            message = {"message": "Hello, RabbitMQ!"}
            message2 = {"event": "order_created", "data": {"order_id": 123, "customer": "Alice"}}
            publisher.publish_message(message, config.RABBITMQ_PRODUCTS_QUEUE)
            publisher.publish_message(message2, config.RABBITMQ_ORDERS_QUEUE)

            
            # Close the connection
            publisher.close()
            
            return "Message published successfully."
        
        except Exception as e:
            return f"An error occurred: {str(e)}"
def get_order_service() -> OrderService:
    """
    Create an instance of the OrderService class."
    """
    db_gen = get_db()         # this is a generator
    db: Session = next(db_gen)
    return OrderService(db)
