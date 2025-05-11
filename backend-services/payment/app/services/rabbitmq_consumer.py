""" RabbitMQ Consumer Service
Message structure:
{
  "event": "order_created",
  "data": {
    "order_id": 123,
    "customer": "Alice"
  }
}

"""
import pika
import json
from core import config
from services.payment_service import PaymentService, get_payment_service
from services.rabbitmq_publisher import RabbitMQPublisher, get_publisher_service
from fastapi import Depends

class RabbitMQConsumer:
    def __init__(self, queue: str, payment_service: PaymentService, publisher: RabbitMQPublisher):
        self.payment_service = payment_service
        self.publisher = publisher
        self.queue = queue
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

        # Mapping event types to handler methods
        self.event_handlers = {
            "take_payment": self.handle_take_payment,
            "update_payment_order_id": self.handle_order_id_updated,
            "rollback_payment": self.handle_rollback_payment,
        }

    def connect(self):
        """Establish the connection and declare the queue."""
        self.connection = pika.BlockingConnection(self.connection_params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue, durable=True)

    def callback(self, ch, method, properties, body):
        """Callback function to process incoming messages."""
        try:
            message = json.loads(body)
            event_type = message.get("event")

            # Dispatch the message to the appropriate handler if it exists
            if event_type in self.event_handlers:
                self.event_handlers[event_type](message)
            else:
                print(f"Unhandled event type: {event_type}")

            # Acknowledge the message after processing
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print("Error processing message:", e)
            # Optionally, you might choose to nack the message or log it for further inspection

    def handle_take_payment(self, message):
        """Handle payment processing logic."""
        try:
            data = message.get("data")
            transaction_id = message.get("transaction_id")
            # Call the payment service to process the payment
            payment_response = self.payment_service.create_payment(data)
            self.payment_service.update_payment_status(payment_response.id, "Success")
            self.payment_service.update_transaction_id(transaction_id=transaction_id, payment_id=payment_response.id)
            # Publish a success message or take further action
            self.publisher.publish_payment_message(payment_response.id, transaction_id)
        except Exception as e:
            print("Error in handle_take_payment:", e)

    def handle_order_id_updated(self, message):
        """Handle order ID update logic."""
        try:
            data = message.get("data")
            order_id = data.get("order_id")
            payment_id = data.get("payment_id")
            # Call the payment service to update the order ID
            self.payment_service.update_order_id(order_id=order_id, payment_id=payment_id)
        except Exception as e:
            print("Error in handle_order_id_updated:", e)

    def handle_rollback_payment(self, message):
        """Handle payment rollback logic."""
        try:
            data = message.get("data")
            payment_id = data.get("payment_id")
            transaction_id = message.get("transaction_id")
            # Call the payment service to rollback the payment
            self.payment_service.rollback_payment(transaction_id=transaction_id, payment_id=payment_id)
        except Exception as e:
            print("Error in handle_rollback_payment:", e)

    def start_consuming(self):
        """Start consuming messages from the specified queue."""
        if not self.connection or self.connection.is_closed:
            self.connect()
        
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.queue,
            on_message_callback=self.callback
        )
        print(f"Started consuming on queue: {self.queue}")
        try:
            self.channel.start_consuming()
        except Exception as e:
            print("Error during consuming:", e)
        finally:
            if self.connection and not self.connection.is_closed:
                self.connection.close()

    def stop_consuming(self):
        """Signal the consumer to stop consuming messages."""
        if self.channel and self.channel.is_open:
            # Signal the consumer's thread to stop consuming in a thread-safe manner
            self.connection.add_callback_threadsafe(self.channel.stop_consuming)

def get_consumer_service(
        queue: str
    ):
    publisher = get_publisher_service()
    payment_service = get_payment_service()
    return RabbitMQConsumer(queue=queue, payment_service=payment_service, publisher=publisher)
