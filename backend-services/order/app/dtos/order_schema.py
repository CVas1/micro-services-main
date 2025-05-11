"""Order schema."""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class OrderItemCreate(BaseModel):
    product_id: str
    quantity: int = 1
    unit_price: float

class OrderCreate(BaseModel):
    user_email: EmailStr
    vendor_email: EmailStr
    delivery_address: str
    description: Optional[str] = None
    status: Optional[str] = "Pending"
    items: List[OrderItemCreate] 

class OrderItemResponse(BaseModel):
    product_id: str
    quantity: int
    unit_price: float

class OrderResponse(BaseModel):
    id: str
    user_email: str
    vendor_email: str
    delivery_address: str
    description: Optional[str] = None
    status: str
    total_price: float
    order_date: datetime
    delivery_date: Optional[datetime] = None
    payment_id: Optional[str] = None
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True