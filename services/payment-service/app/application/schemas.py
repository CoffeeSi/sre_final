from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CreatePaymentRequest(BaseModel):
    order_id: int = Field(..., gt=0)
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="KZT", min_length=3, max_length=3)
    method: str = Field(..., min_length=1)


class ProcessPaymentRequest(BaseModel):
    payment_id: int = Field(..., gt=0)


class PaymentResponse(BaseModel):
    id: int
    user_id: int
    order_id: int
    amount: Decimal
    currency: str
    status: str
    method: str
    transaction_id: str | None
    created_at: datetime
    updated_at: datetime


class PaymentsListResponse(BaseModel):
    payments: list[PaymentResponse]


class PaymentStatusResponse(BaseModel):
    payment_id: int
    status: str
    transaction_id: str | None
    updated_at: datetime
