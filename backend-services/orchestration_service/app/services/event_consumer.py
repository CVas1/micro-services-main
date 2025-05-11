"""Event Consumer for Saga Orchestrator"""
import pika
import json
from services.saga_orchestrator import get_saga_orchestrator
import config
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
            print(f"Started consuming on queue: {self.queue}")
            self.channel.start_consuming()

        except Exception as e:
            print("Error setting up consumer:", e)
        finally:
            if self.connection and not self.connection.is_closed:
                self.connection.close()

    def stop_consuming(self):
        """Signal the consumer to stop consuming messages."""
        if self.channel and self.channel.is_open:
            # Signal the consumer's thread to stop consuming in a thread-safe manner
            self.connection.add_callback_threadsafe(self.channel.stop_consuming)


def get_consumer_service(queue: str) -> RabbitMQConsumer:
    return RabbitMQConsumer(queue)