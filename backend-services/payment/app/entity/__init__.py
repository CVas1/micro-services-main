"""Models package."""
import uuid

def generate_uuid():
    """Generate a UUID."""
    return str(uuid.uuid4())


PAYMENT_METHODS = (
    "Credit Card",
    "Debit Card",
    "Cash on Delivery",
)

PAYMENT_STATUSES = (
    "Pending",
    "Failed",
    "Success",
    "Refund",
    "Cancelled",
)