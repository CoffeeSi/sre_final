from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, Enum):
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    WALLET = "wallet"


@dataclass
class Payment:
    id: int
    user_id: int
    order_id: int
    amount: Decimal
    currency: str
    status: PaymentStatus
    method: PaymentMethod
    transaction_id: str | None
    created_at: datetime
    updated_at: datetime
