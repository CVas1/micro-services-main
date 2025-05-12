""" Rabbitmq Publisher Service """
import pika
import json
from core import config
from logger import logger

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
        try:
            self.connection = pika.BlockingConnection(self.connection_params)
            self.channel = self.connection.channel()
        except Exception as e:
            logger.error(f"Error connecting to RabbitMQ: {str(e)}")
            raise

    def publish_message(self, message: dict, queue: str):
        """Publish a message to the specified RabbitMQ queue."""
        if not self.connection or self.connection.is_closed:
            self.connect()

        # Declare the queue dynamically based on the provided name
        self.channel.queue_declare(queue=queue, durable=True)
        
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=queue,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2  # make message persistent
                )
            )
            logger.info(f"Message published successfully to queue {queue}: {message}")
        except Exception as e:
            logger.error(f"Error publishing message to queue {queue}: {str(e)}")
            raise
    
    def publish_order_created_response(self, order_id: str, transaction_id: str):
        command = {
            "transaction_id": transaction_id,
            "event": "create_order",
            "message": "Order created successfully",
            "status": "success",
            "data": {
                "order_id": order_id,
            }
        }
        self.publish_message(command, config.RABBITMQ_ORCHESTRATION_QUEUE)

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()

def get_publisher_service() -> RabbitMQPublisher:
    return RabbitMQPublisher()