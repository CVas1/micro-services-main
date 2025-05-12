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
from services.order_service import OrderService, get_order_service
from services.rabbitmq_publisher import RabbitMQPublisher, get_publisher_service
from logger import logger

class RabbitMQConsumer:
    def __init__(self, queue: str, order_service: OrderService, publisher: RabbitMQPublisher):
        self.order_service = order_service
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
            "create_order": self.handle_order_created,
            "update_order_payment_id": self.handle_update_order_payment_id,
            "rollback_order": self.handle_rollback_order,
            # Add more event mappings as needed
        }

    def connect(self):
        """Establish the connection and declare the queue."""
        try:
            self.connection = pika.BlockingConnection(self.connection_params)
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue, durable=True)
        except Exception as e:
            logger.error(f"Error connecting to RabbitMQ: {str(e)}")
            raise

    def callback(self, ch, method, properties, body):
        """Callback function to process incoming messages."""
        try:
            message = json.loads(body)
            event_type = message.get("event")

            # Dispatch the message to the appropriate handler if it exists
            if event_type in self.event_handlers:
                self.event_handlers[event_type](message)
            else:
                logger.warning(f"Unhandled event type: {event_type}")

            # Acknowledge the message after processing
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            # Optionally, you might choose to nack the message or log it for further inspection

    def handle_order_created(self, message):
        """Handle order creation logic."""
        try:
            data = message.get("data", {})
            transection_id = message.get("transaction_id")
            order = self.order_service.create_order(
                order_data=data, transaction_id=transection_id
            )
            self.publisher.publish_order_created_response(order_id=order.id, transaction_id=transection_id)
        except Exception as e:
            logger.error(f"Error handling order creation: {str(e)}")
            raise

    def handle_update_order_payment_id(self, message):
        """Handle order payment ID update logic."""
        try:
            data = message.get("data", {})
            order_id = data.get("order_id")
            payment_id = data.get("payment_id")
            self.order_service.update_order_payment(order_id, payment_id)
        except Exception as e:
            logger.error(f"Error updating order payment ID: {str(e)}")
            raise

    def handle_rollback_order(self, message):
        """Handle order rollback logic."""
        try:
            transaction_id = message.get("transaction_id")
            self.order_service.rollback_order(transaction_id)
        except Exception as e:
            logger.error(f"Error rolling back order: {str(e)}")
            raise

    def start_consuming(self):
        """Start consuming messages from the specified queue."""
        if not self.connection or self.connection.is_closed:
            self.connect()
        
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.queue,
            on_message_callback=self.callback
        )
        logger.info(f"Started consuming on queue: {self.queue}")
        try:
            self.channel.start_consuming()
        except Exception as e:
            logger.error(f"Error during consuming: {str(e)}")
        finally:
            if self.connection and not self.connection.is_closed:
                self.connection.close()

    def stop_consuming(self):
        """Signal the consumer to stop consuming messages."""
        if self.channel and self.channel.is_open:
            # Signal the consumer's thread to stop consuming in a thread-safe manner
            self.connection.add_callback_threadsafe(self.channel.stop_consuming)

def get_consumer_service(
        queue: str,
        ) -> RabbitMQConsumer:
    order_service = get_order_service()
    publisher = get_publisher_service()
    return RabbitMQConsumer(queue, order_service, publisher)