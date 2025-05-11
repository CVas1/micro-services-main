"""Payment schema module."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
class PaymentCreate(BaseModel):
    user_email : str
    order_id : str
    amount : float
    payment_method : str
    transaction_id : Optional[str] = None
    payment_status : Optional[str] = "Pending"

class PaymentResponse(BaseModel):
    id : str
    user_email : str
    order_id : Optional[str]
    amount : float
    payment_method : str
    payment_status : Optional[str]
    transaction_id : Optional[str]
    created_at : datetime
    class Config:
        from_attributes = True