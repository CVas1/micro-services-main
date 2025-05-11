from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class PaymentCreate(BaseModel):
    user_email : EmailStr
    order_id : str
    amount : float
    payment_method : str
    transaction_id : Optional[str] = None
    payment_status : Optional[str] = "Pending"

class PaymentResponse(BaseModel):
    id : str
    user_email : EmailStr
    order_id : str
    amount : float
    payment_method : str
    payment_status : str
    transaction_id : Optional[str]
    created_at : datetime