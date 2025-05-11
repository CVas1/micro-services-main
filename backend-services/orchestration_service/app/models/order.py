from pydantic import BaseModel, EmailStr
from typing import List, Optional

class OrderItemCreate(BaseModel):
    product_id: str
    quantity: int
    unit_price: float

    def dict(self):
        return {
            "product_id": self.product_id,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
        }
    
class OrderCreateRequest(BaseModel):
    user_email: EmailStr
    vendor_email: EmailStr
    delivery_address: str
    description: Optional[str] = None
    status: Optional[str] = "Pending"
    items: List[OrderItemCreate]
    payment_method: str

    def total_price(self) -> float:
        return sum(item.quantity * item.unit_price for item in self.items)

class OrderResponse(BaseModel):
    id: str
    user_email: EmailStr
    vendor_email: EmailStr
    delivery_address: str
    description: Optional[str]
    status: str
    items: List[OrderItemCreate]
    total_amount: float
    created_at: str