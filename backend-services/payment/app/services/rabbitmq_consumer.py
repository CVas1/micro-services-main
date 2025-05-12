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
from logger import logger

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
        logger.info(f"Connecting to RabbitMQ at {config.RABBITMQ_HOST}:{config.RABBITMQ_PORT}")
        self.connection = pika.BlockingConnection(self.connection_params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue, durable=True)
        logger.info(f"Declared queue '{self.queue}'")

    def callback(self, ch, method, properties, body):
        """Callback function to process incoming messages."""
        try:
            message = json.loads(body)
            logger.info(f"Received message: {message}")
            event_type = message.get("event")

            # Dispatch the message to the appropriate handler if it exists
            if event_type in self.event_handlers:
                logger.info(f"Dispatching event '{event_type}' to handler")
                self.event_handlers[event_type](message)
            else:
                logger.warning(f"Unhandled event type: {event_type}")
                print(f"Unhandled event type: {event_type}")

            # Acknowledge the message after processing
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info("Message acknowledged")
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            print("Error processing message:", e)
            # Optionally, you might choose to nack the message or log it for further inspection

    def handle_take_payment(self, message):
        """Handle payment processing logic."""
        logger.info("Handling 'take_payment' event")
        try:
            data = message.get("data")
            transaction_id = message.get("transaction_id")
            logger.debug(f"take_payment data: {data}, transaction_id: {transaction_id}")
            # Call the payment service to process the payment
            payment_response = self.payment_service.create_payment(data)
            logger.info(f"Created payment with ID: {payment_response.id}")
            self.payment_service.update_payment_status(payment_response.id, "Success")
            logger.info(f"Updated payment status to 'Success' for ID: {payment_response.id}")
            self.payment_service.update_transaction_id(transaction_id=transaction_id, payment_id=payment_response.id)
            logger.info(f"Updated transaction ID for payment {payment_response.id}")
            # Publish a success message or take further action
            self.publisher.publish_payment_message(payment_response.id, transaction_id)
            logger.info(f"Published payment message for ID: {payment_response.id}")
        except Exception as e:
            logger.error(f"Error in handle_take_payment: {e}", exc_info=True)
            print("Error in handle_take_payment:", e)

    def handle_order_id_updated(self, message):
        """Handle order ID update logic."""
        logger.info("Handling 'update_payment_order_id' event")
        try:
            data = message.get("data")
            order_id = data.get("order_id")
            payment_id = data.get("payment_id")
            logger.debug(f"update_payment_order_id data: order_id={order_id}, payment_id={payment_id}")
            # Call the payment service to update the order ID
            self.payment_service.update_order_id(order_id=order_id, payment_id=payment_id)
            logger.info(f"Updated order ID to {order_id} for payment {payment_id}")
        except Exception as e:
            logger.error(f"Error in handle_order_id_updated: {e}", exc_info=True)
            print("Error in handle_order_id_updated:", e)

    def handle_rollback_payment(self, message):
        """Handle payment rollback logic."""
        logger.info("Handling 'rollback_payment' event")
        try:
            data = message.get("data")
            payment_id = data.get("payment_id")
            transaction_id = message.get("transaction_id")
            logger.debug(f"rollback_payment data: payment_id={payment_id}, transaction_id={transaction_id}")
            # Call the payment service to rollback the payment
            self.payment_service.rollback_payment(transaction_id=transaction_id, payment_id=payment_id)
            logger.info(f"Rolled back payment {payment_id}")
        except Exception as e:
            logger.error(f"Error in handle_rollback_payment: {e}", exc_info=True)
            print("Error in handle_rollback_payment:", e)

    def start_consuming(self):
        """Start consuming messages from the specified queue."""
        if not self.connection or self.connection.is_closed:
            logger.info("Starting connection and channel for consuming")
            self.connect()

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.queue,
            on_message_callback=self.callback
        )
        logger.info(f"Started consuming on queue: {self.queue}")
        print(f"Started consuming on queue: {self.queue}")
        try:
            self.channel.start_consuming()
        except Exception as e:
            logger.error(f"Error during consuming: {e}", exc_info=True)
            print("Error during consuming:", e)
        finally:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("Connection closed")

    def stop_consuming(self):
        """Signal the consumer to stop consuming messages."""
        if self.channel and self.channel.is_open:
            logger.info("Stopping consumer")
            # Signal the consumer's thread to stop consuming in a thread-safe manner
            self.connection.add_callback_threadsafe(self.channel.stop_consuming)

def get_consumer_service(
        queue: str
    ):
    publisher = get_publisher_service()
    payment_service = get_payment_service()
    return RabbitMQConsumer(queue=queue, payment_service=payment_service, publisher=publisher)
