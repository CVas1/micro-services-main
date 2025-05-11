"""
RabbitMQ message publisher for sending messages to a queue.
This module provides a simple interface for publishing messages to RabbitMQ queues.
"""
from typing import List
import pika
import json
from models.saga_state import OrderSagaState, PaymentSagaState
import config
from models.order import OrderCreateRequest, OrderResponse, OrderItemCreate
from models.payment import PaymentCreate, PaymentResponse
class RabbitMQPublisher:
    def __init__(self):
        credentials = pika.PlainCredentials(
            username=config.RABBITMQ_USER, 
            password=config.RABBITMQ_PASSWORD
        )
        self.connection_params = pika.ConnectionParameters(
            host=config.RABBITMQ_HOST,
            port=config.RABBITMQ_PORT,
            credentials=credentials
        )
        self.connection = None
        self.channel = None

    def connect(self):
        """Establish connection and channel."""
        self.connection = pika.BlockingConnection(self.connection_params)
        self.channel = self.connection.channel()

    def publish_message(self, message: dict, queue: str):
        """Publish a message to the specified RabbitMQ queue."""
        if not self.connection or self.connection.is_closed:
            self.connect()

        # make every object with .dict() into a plain dict,
        # and leave primitives/lists alone
        body_str = json.dumps(
            message,
            default=lambda o: o.dict() if hasattr(o, "dict") else super(type(o), o)
        )

        self.channel.queue_declare(queue=queue, durable=True)
        self.channel.basic_publish(
            exchange='',
            routing_key=queue,
            body=body_str,
            properties=pika.BasicProperties(
                delivery_mode=2  # make message persistent
            )
        )

    def publish_reduce_stock_command(self, products: List[OrderItemCreate], transaction_id: str):
        """Publish a command to reduce stock."""
        command = {
            "event": "reduce_stock",
            "transaction_id": transaction_id,
            "data": {
                "products": [{"product_id": product.product_id, "quantity": product.quantity} for product in products]
            }
        }
        self.publish_message(command, config.RABBITMQ_PRODUCTS_QUEUE)

    def publish_create_order_command(self, order_data: OrderCreateRequest | OrderSagaState, transaction_id: str):
        """Publish a command to create an order."""
        command = {
            "event": "create_order",
            "transaction_id": transaction_id,
            "data": {
                "user_email": order_data.user_email,
                "vendor_email": order_data.vendor_email,
                "delivery_address": order_data.delivery_address,
                "description": order_data.description,
                "status": order_data.status,
                "items": order_data.items
            }
        }
        self.publish_message(command, config.RABBITMQ_ORDERS_QUEUE)

    def publish_take_payment_command(self, payment_data: PaymentSagaState):
        """Publish a command to take payment."""
        command = {
            "event": "take_payment",
            "transaction_id": payment_data.transaction_id,
            "data": {
                "user_email": payment_data.user_email,
                "order_id": payment_data.order_id,
                "amount": payment_data.amount,
                "payment_method": payment_data.payment_method,
                "payment_status": payment_data.payment_status
            }
        }
        self.publish_message(command, config.RABBITMQ_PAYMENT_QUEUE)
    
    def publish_rollback_stock_command(self, transaction_id: str):
        """Publish a command to rollback stock."""
        command = {
            "event": "rollback_stock",
            "transaction_id": transaction_id,
            "data": {
                
            }
        }
        self.publish_message(command, config.RABBITMQ_PRODUCTS_QUEUE)

    def publish_rollback_payment_command(self, transaction_id: str, payment_id: str):
        """Publish a command to rollback payment."""
        command = {
            "event": "rollback_payment",
            "transaction_id": transaction_id,
            "data": {
                "payment_id": payment_id
            }
        }
        self.publish_message(command, config.RABBITMQ_PAYMENT_QUEUE)
    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()

    def publish_rollback_order_command(self, transaction_id: str):
        """Publish a command to rollback order."""
        command = {
            "event": "rollback_order",
            "transaction_id": transaction_id,
            "data": {
                
            }
        }
        self.publish_message(command, config.RABBITMQ_ORDERS_QUEUE)

    def publish_update_order_payment_id(self, order_id: str, payment_id: str):
        """Publish a command to update order with payment ID."""
        command = {
            "event": "update_order_payment_id",
            "data": {
                "order_id": order_id,
                "payment_id": payment_id
            }
        }
        self.publish_message(command, config.RABBITMQ_ORDERS_QUEUE)
    
    def publish_update_payment_order_id(self, payment_id: str, order_id: str):
        """Publish a command to update payment with order ID."""
        command = {
            "event": "update_payment_order_id",
            "data": {
                "payment_id": payment_id,
                "order_id": order_id
            }
        }
        self.publish_message(command, config.RABBITMQ_PAYMENT_QUEUE)

def get_publisher_service() -> RabbitMQPublisher:
    return RabbitMQPublisher()