"""Event Consumer for Saga Orchestrator"""
import pika
import json
from services.saga_orchestrator import get_saga_orchestrator
import config
from logger import logger

class RabbitMQConsumer:
    def __init__(self, queue: str):
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
        orchestrator = get_saga_orchestrator()
        # Mapping event types to handler methods
        self.event_handlers = {
            "reduce_stock": orchestrator.handle_stock_reduced_event,
            "take_payment": orchestrator.hande_take_payment_event,
            "create_order": orchestrator.handle_create_order_event,
            # Add more event mappings as needed
        }
        logger.log(f"Initialized RabbitMQ consumer for queue: {queue}")

    def connect(self):
        """Establish the connection and declare the queue."""
        try:
            self.connection = pika.BlockingConnection(self.connection_params)
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue, durable=True)
            logger.log(f"Successfully connected to RabbitMQ and declared queue: {self.queue}")
        except Exception as e:
            logger.log(f"Failed to connect to RabbitMQ: {str(e)}", level="ERROR")
            raise

    def callback(self, ch, method, properties, body):
        """Callback function to process incoming messages."""
        try:
            message = json.loads(body)
            event_type = message.get("event")
            logger.log(f"Received message with event type: {event_type}")

            # Dispatch the message to the appropriate handler if it exists
            if event_type in self.event_handlers:
                logger.log(f"Processing event type: {event_type}")
                self.event_handlers[event_type](message)
                logger.log(f"Successfully processed event type: {event_type}")
            else:
                logger.log(f"Unhandled event type: {event_type}", level="ERROR")

            # Acknowledge the message after processing
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.log(f"Error processing message: {str(e)}", level="ERROR")
            # Optionally, you might choose to nack the message or log it for further inspection

    def start_consuming(self):
        """Start consuming messages from the specified queue."""
        try:
            if not self.connection or self.connection.is_closed:
                self.connect()
            
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=self.queue,
                on_message_callback=self.callback
            )
            logger.log(f"Started consuming on queue: {self.queue}")
            self.channel.start_consuming()

        except Exception as e:
            logger.log(f"Error setting up consumer: {str(e)}", level="ERROR")
        finally:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.log("Closed RabbitMQ connection")

    def stop_consuming(self):
        """Signal the consumer to stop consuming messages."""
        if self.channel and self.channel.is_open:
            # Signal the consumer's thread to stop consuming in a thread-safe manner
            self.connection.add_callback_threadsafe(self.channel.stop_consuming)
            logger.log("Stopped consuming messages")


def get_consumer_service(queue: str) -> RabbitMQConsumer:
    return RabbitMQConsumer(queue)