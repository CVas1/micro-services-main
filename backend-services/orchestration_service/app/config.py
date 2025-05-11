"""
Configuration settings for the application.
"""
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", default="localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", default=5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", default="guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", default="guest")
RABBITMQ_PRODUCTS_QUEUE = "products_queue"
RABBITMQ_ORDERS_QUEUE = "orders_queue"
RABBITMQ_PAYMENT_QUEUE = "payment_queue"
RABBITMQ_ORCHESTRATION_QUEUE = "orchestration_queue"

REDIS_HOST = os.getenv("REDIS_HOST", default="localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", default=6379))
REDIS_DB = int(os.getenv("REDIS_DB", default=0))


AUTHERIZATION_SERVER_HOST = os.getenv("AUTHERIZATION_SERVER_HOST",default="http://localhost")
AUTHORIZATION_SERVER_PORT = os.getenv("AUTHORIZATION_SERVER_PORT",default=5206)
AUTHORIZATION_SERVER_CUSTOMER_ENDPOINT = "/customer-policy"
AUTHORIZATION_SERVER_VENDOR_ENDPOINT = "/vendor-policy"
AUTHORIZATION_SERVER_ADMIN_ENDPOINT = "/admin-policy"
