from datetime import datetime, timezone
from decimal import Decimal

import asyncio
import pytest

from app.application.schemas import CreatePaymentRequest
from app.application.use_cases import CreatePaymentUseCase
from app.domain.exceptions import InvalidAmountError, PaymentProcessingError
from app.domain.models import Payment, PaymentMethod, PaymentStatus


class DummyPaymentRepository:
    def __init__(self):
        self.created_args = None

    async def get_by_order_id(self, order_id):
        return None

    async def create(
        self,
        user_id,
        order_id,
        amount,
        currency,
        method,
        transaction_id=None,
    ):
        self.created_args = {
            "user_id": user_id,
            "order_id": order_id,
            "amount": amount,
            "currency": currency,
            "method": method,
            "transaction_id": transaction_id,
        }
        now = datetime.now(timezone.utc)
        return Payment(
            id=1,
            user_id=user_id,
            order_id=order_id,
            amount=Decimal(amount),
            currency=currency,
            status=PaymentStatus.PENDING,
            method=PaymentMethod(method),
            transaction_id=transaction_id,
            created_at=now,
            updated_at=now,
        )


def test_create_payment_uses_order_amount(monkeypatch):
    async def fake_get_order_details(order_id, user_id):
        return {"id": order_id, "user_id": user_id}

    monkeypatch.setattr(
        "app.application.use_cases.get_order_details", fake_get_order_details
    )

    repository = DummyPaymentRepository()
    use_case = CreatePaymentUseCase(repository)
    request = CreatePaymentRequest(
        order_id=15,
        amount=Decimal("4599.90"),
        currency="KZT",
        method="card",
    )

    response = asyncio.run(use_case.execute(request, user_id=7))

    assert response.order_id == 15
    assert response.amount == Decimal("4599.90")
    assert repository.created_args["amount"] == "4599.90"
    assert repository.created_args["user_id"] == 7


def test_create_payment_rejects_non_positive_amount():
    repository = DummyPaymentRepository()
    use_case = CreatePaymentUseCase(repository)
    request = CreatePaymentRequest.model_construct(
        order_id=15,
        amount=Decimal("0"),
        currency="KZT",
        method="card",
    )

    with pytest.raises(InvalidAmountError):
        asyncio.run(use_case.execute(request, user_id=7))


def test_create_payment_fails_when_order_missing(monkeypatch):
    async def fake_get_order_details(order_id, user_id):
        return None

    monkeypatch.setattr(
        "app.application.use_cases.get_order_details", fake_get_order_details
    )

    repository = DummyPaymentRepository()
    use_case = CreatePaymentUseCase(repository)
    request = CreatePaymentRequest(
        order_id=15,
        amount=Decimal("4599.90"),
        currency="KZT",
        method="card",
    )

    with pytest.raises(PaymentProcessingError):
        asyncio.run(use_case.execute(request, user_id=7))
