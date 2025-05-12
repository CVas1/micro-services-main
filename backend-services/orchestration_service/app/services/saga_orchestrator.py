"""
Saga Orchestrator
Handles the orchestration of the Saga pattern.
"""# saga_orchestrator.py

"""
"""
import uuid
from fastapi import Depends
from services.auth_http_client import get_auth_service
from services.message_publisher import get_publisher_service
from models.saga_state import OrderSagaState, ProductSagaState, PaymentSagaState
from models.order import OrderCreateRequest
from services.redis_saga_store import get_redis_saga_store, RedisSagaStore
from logger import logger

class SagaOrchestrator:
    def __init__(self, saga_store: RedisSagaStore):
        self.auth_client = get_auth_service()  # Synchronous calls
        self.publisher = get_publisher_service()  # Publishes to RabbitMQ
        self.saga_store = saga_store  
        logger.log("SagaOrchestrator initialized", "INFO")

    def start_order_saga(self, order_data: OrderCreateRequest, token: str):
        logger.log(f"Starting order saga for user: {order_data.user_email}", "INFO")
        # verified = self.auth_client.authenticate_customer(jwt_token=token)
        # if not verified:
        #    raise Exception("Authentication failed")
        
        transaction_id = str(uuid.uuid4())
        logger.log(f"Generated transaction ID: {transaction_id}", "INFO")
        # If verified, store saga state
        order_saga_state = OrderSagaState(
            transaction_id=transaction_id,
            user_email=order_data.user_email,
            vendor_email=order_data.vendor_email,
            delivery_address=order_data.delivery_address,
            description=order_data.description,
            status=order_data.status,
            items=order_data.items,
            payment_method=order_data.payment_method
        )
        prouct_saga_state = ProductSagaState(
            transaction_id=transaction_id,
            product_id=order_data.items[0].product_id,
            quantity=order_data.items[0].quantity
        )

        self.saga_store.save_product_saga(prouct_saga_state)
        self.saga_store.save_order_saga(order_saga_state)
        logger.log(f"Saved initial saga states for transaction: {transaction_id}", "INFO")

        self.publisher.publish_reduce_stock_command(
            transaction_id=transaction_id, 
            products=order_data.items
        )
        logger.log(f"Published reduce stock command for transaction: {transaction_id}", "INFO")
        return True

    def cancel_order_saga(self, order_id: str, token: str):
        logger.log(f"Starting order cancellation for order: {order_id}", "INFO")
        # verified = self.auth_client.authenticate_customer(jwt_token=token)
        # if not verified:
        #    raise Exception("Authentication failed")
        
        transaction_id = self.saga_store.get_order_id_with_saga(order_id)
        order_saga_state = self.saga_store.get_order_saga(transaction_id)
        if not order_saga_state:
            logger.log(f"Order ID {order_id} not found in saga store.", "ERROR")
            return
        transaction_id = order_saga_state.transaction_id
        logger.log(f"Starting rollback for transaction: {transaction_id}", "INFO")
        # Trigger rollback stock if needed
        self.publisher.publish_rollback_stock_command(
            transaction_id=transaction_id
        )
        self.publisher.publish_rollback_payment_command(
            transaction_id=transaction_id,
            payment_id=order_saga_state.payment_id
        )
        self.publisher.publish_rollback_order_command(
            transaction_id=transaction_id
        )
        logger.log(f"Published all rollback commands for transaction: {transaction_id}", "INFO")
        return True

    def handle_stock_reduced_event(self, message: dict):
        transaction_id : str = message["transaction_id"]
        data : dict = message["data"]
        status : str = message["status"]
        logger.log(f"Handling stock reduced event for transaction: {transaction_id}", "INFO")
        
        saga_state = self.saga_store.get_product_saga(transaction_id)
        order_saga_state = self.saga_store.get_order_saga(transaction_id)
        if not saga_state:
            logger.log(f"Transaction ID {transaction_id} not found in saga store.", "ERROR")
            return
        
        if "error" in status:
            logger.log(f"Error reducing stock: {status}", "ERROR")
            return
        
        payment_saga_state = PaymentSagaState(
            transaction_id=transaction_id,
            user_email=order_saga_state.user_email,
            amount=order_saga_state.total_price(),
            payment_method=order_saga_state.payment_method,
            payment_status="Pending"
        )
        self.saga_store.save_payment_saga(payment_saga_state)
        logger.log(f"Saved payment saga state for transaction: {transaction_id}", "INFO")
        self.publisher.publish_take_payment_command(payment_data=payment_saga_state)
        logger.log(f"Published take payment command for transaction: {transaction_id}", "INFO")

    def hande_take_payment_event(self, message: dict):
        transaction_id : str = message["transaction_id"]
        data : dict = message["data"]
        payment_id : str = data["payment_id"]
        status : str = message["status"]
        logger.log(f"Handling take payment event for transaction: {transaction_id}", "INFO")
        
        payment_saga_state = self.saga_store.get_payment_saga(transaction_id)
        order_saga_state = self.saga_store.get_order_saga(transaction_id)
        
        if not payment_saga_state or not order_saga_state:
            logger.log(f"Transaction ID {transaction_id} not found in saga store.", "ERROR")
        if "error" in status:
            logger.log(f"Error taking payment: {status}", "ERROR")
            # Trigger rollback stock if needed
            self.publisher.publish_rollback_stock_command(
                transaction_id=transaction_id
            )
            return
        
        # Update saga state
        payment_saga_state.payment_status = status
        self.saga_store.save_payment_saga(payment_saga_state)
        order_saga_state.payment_id = payment_id
        self.saga_store.save_order_saga(order_saga_state)
        logger.log(f"Updated payment and order saga states for transaction: {transaction_id}", "INFO")
        
        order_saga_state = self.saga_store.get_order_saga(transaction_id)
        if not order_saga_state:
            logger.log(f"Transaction ID {transaction_id} not found in saga store.", "ERROR")
        
        # next step: publih create order command
        self.publisher.publish_create_order_command(
            order_data=order_saga_state,
            transaction_id=transaction_id
        )
        logger.log(f"Published create order command for transaction: {transaction_id}", "INFO")
        return
    
    def handle_create_order_event(self, message: dict):
        transaction_id : str = message["transaction_id"]
        data : dict = message["data"]
        order_id : str = data["order_id"]
        status : str = message["status"]
        logger.log(f"Handling create order event for transaction: {transaction_id}", "INFO")
        
        self.saga_store.save_order_id_with_saga(
            order_id=order_id, 
            transaction_id=transaction_id)
        order_saga_state = self.saga_store.get_order_saga(transaction_id)
        payment_saga_state = self.saga_store.get_payment_saga(transaction_id)
        if not order_saga_state or not payment_saga_state:
            logger.log(f"Transaction ID {transaction_id} not found in saga store.", "ERROR")
        
        if "error" in status:
            logger.log(f"Error creating order: {status}", "ERROR")
            # Trigger rollback stock if needed
            self.publisher.publish_rollback_stock_command(
                transaction_id=transaction_id
            )
            self.publisher.publish_rollback_payment_command(
                transaction_id=transaction_id,
                payment_id=order_saga_state.payment_id
            )
            return
        
        # Update saga state
        order_saga_state.status = status
        self.saga_store.save_order_saga(order_saga_state)
        payment_saga_state.order_id = order_id
        self.saga_store.save_payment_saga(payment_saga_state)
        logger.log(f"Updated order and payment saga states for transaction: {transaction_id}", "INFO")
        
        self.publisher.publish_update_order_payment_id(order_id=order_id, payment_id=order_saga_state.payment_id)
        self.publisher.publish_update_payment_order_id(
            order_id=order_id,
            payment_id=order_saga_state.payment_id
        )
        logger.log(f"Published payment and order ID updates for transaction: {transaction_id}", "INFO")

def get_saga_orchestrator() -> SagaOrchestrator:
    store = get_redis_saga_store()
    return SagaOrchestrator(saga_store=store)