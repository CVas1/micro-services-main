"""Models package."""
import uuid

def generate_uuid():
    """Generate a UUID."""
    return str(uuid.uuid4())

ALLOWED_STATUSES = (
    "Pending",
    "Preparing for Shipment",
    "Shipped",
    "Out for Delivery",
    "Delivered",
    "Refund",
    "Canceled",
)
