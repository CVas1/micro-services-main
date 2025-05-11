import redis
import json
from models.order import OrderItemCreate
from models.saga_state import OrderSagaState, ProductSagaState, PaymentSagaState
import config
class RedisSagaStore:
    def __init__(self, host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def save_order_saga(self, saga: OrderSagaState, ttl: int = 600):
        key = f"order_saga:{saga.transaction_id}"
        self.client.set(key, json.dumps(saga.dict()), ex=ttl)

    def save_order_id_with_saga(self, order_id: str, transaction_id: str):
        key = f"order_id:{order_id}"
        self.client.set(key, transaction_id)

    def get_order_id_with_saga(self, order_id: str) -> str | None:
        key = f"order_id:{order_id}"
        transaction_id = self.client.get(key)
        if not transaction_id:
            return None
        return transaction_id
    
    def get_order_saga(self, transaction_id: str) -> OrderSagaState | None:
        raw = self.client.get(f"order_saga:{transaction_id}")
        if not raw:
            return None

        payload = json.loads(raw)
        items_data = payload.pop("items", [])
        items = [OrderItemCreate(**it) for it in items_data]

        return OrderSagaState(
            transaction_id   = payload["transaction_id"],
            description      = payload["description"],
            user_email       = payload["user_email"],
            vendor_email     = payload["vendor_email"],
            delivery_address = payload["delivery_address"],
            payment_method   = payload["payment_method"],
            status           = payload.get("status", "Pending"),
            items            = items,
            payment_id       = payload.get("payment_id"),
        )

    def delete_order_saga(self, transaction_id: str):
        key = f"order_saga:{transaction_id}"
        self.client.delete(key)

    def save_product_saga(self, saga: ProductSagaState, ttl: int = 600):
        key = f"product_saga:{saga.transaction_id}"
        self.client.set(key, json.dumps(saga.dict()), ex=ttl)

    def get_product_saga(self, transaction_id: str) -> ProductSagaState | None:
        key = f"product_saga:{transaction_id}"
        data = self.client.get(key)
        return ProductSagaState(**json.loads(data)) if data else None

    def delete_product_saga(self, transaction_id: str):
        key = f"product_saga:{transaction_id}"
        self.client.delete(key)
    
    def save_payment_saga(self, saga: PaymentSagaState, ttl: int = 600):
        key = f"payment_saga:{saga.transaction_id}"
        self.client.set(key, json.dumps(saga.dict()), ex=ttl)
    
    def get_payment_saga(self, transaction_id: str) -> PaymentSagaState | None:
        key = f"payment_saga:{transaction_id}"
        data = self.client.get(key)
        return PaymentSagaState(**json.loads(data)) if data else None
    def delete_payment_saga(self, transaction_id: str):
        key = f"payment_saga:{transaction_id}"
        self.client.delete(key)
    
    
def get_redis_saga_store() -> RedisSagaStore:
    return RedisSagaStore(
    )