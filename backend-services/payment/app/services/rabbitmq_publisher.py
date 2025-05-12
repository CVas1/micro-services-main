""" RabbitMQ Publisher Service """
import pika
import json
from core import config
from logger import logger

class RabbitMQPublisher:
    def __init__(self):
        logger.info("Initializing RabbitMQPublisher")
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
            logger.info(f"Connecting to RabbitMQ at {config.RABBITMQ_HOST}:{config.RABBITMQ_PORT}")
            self.connection = pika.BlockingConnection(self.connection_params)
            self.channel = self.connection.channel()
            logger.info("RabbitMQ connection established and channel opened")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}", exc_info=True)
            raise

    def publish_message(self, message: dict, queue: str):
        """Publish a message to the specified RabbitMQ queue."""
        try:
            if not self.connection or self.connection.is_closed:
                logger.info("Connection closed or missing, reconnecting")
                self.connect()

            logger.info(f"Declaring queue '{queue}' and publishing message: {message}")
            self.channel.queue_declare(queue=queue, durable=True)
            self.channel.basic_publish(
                exchange='',
                routing_key=queue,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2  # make message persistent
                )
            )
            logger.info(f"Message published to queue '{queue}'")
        except Exception as e:
            logger.error(f"Error publishing message to queue '{queue}': {e}", exc_info=True)
            raise

    def publish_payment_message(self, payment_id: int, transaction_id: str):
        command = {
            "transaction_id": transaction_id,
            "event": "take_payment",
            "status": "success",
            "message": "Payment is successfully done",
            "data": {"payment_id": payment_id}
        }
        logger.info(f"Publishing payment message for payment_id={payment_id}, transaction_id={transaction_id}")
        self.publish_message(command, config.RABBITMQ_ORCHESTRATION_QUEUE)

    def close(self):
        if self.connection and not self.connection.is_closed:
            logger.info("Closing RabbitMQ connection")
            self.connection.close()
            logger.info("RabbitMQ connection closed")

def get_publisher_service():
    return RabbitMQPublisher()
