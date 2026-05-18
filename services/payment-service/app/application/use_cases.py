import uuid
from app.domain.exceptions import (
    PaymentNotFoundError,
    InvalidPaymentStatusError,
    PaymentProcessingError,
    InvalidAmountError,
)
from app.domain.models import PaymentStatus, PaymentMethod
from app.domain.repositories import IPaymentRepository
from app.domain.services import PaymentValidationService
from app.application.schemas import (
    CreatePaymentRequest,
    PaymentResponse,
    PaymentsListResponse,
    PaymentStatusResponse,
)
from app.infrastructure.http_clients import get_order_details


class CreatePaymentUseCase:
    def __init__(self, repository: IPaymentRepository) -> None:
        self._repository = repository

    async def execute(
        self, data: CreatePaymentRequest, user_id: int
    ) -> PaymentResponse:
        # Validate payment data
        PaymentValidationService.validate_amount(data.amount)
        PaymentValidationService.validate_payment_method(data.method)

        # Check if order exists and belongs to user
        order = await get_order_details(data.order_id, user_id)
        if not order:
            raise PaymentProcessingError("Order not found or does not belong to user")

        # Check if payment already exists for this order
        existing_payment = await self._repository.get_by_order_id(data.order_id)
        if existing_payment and existing_payment.status == PaymentStatus.COMPLETED:
            raise PaymentProcessingError("Payment already completed for this order")

        # Generate transaction ID
        transaction_id = f"TXN-{uuid.uuid4().hex[:16].upper()}"

        # Create payment
        payment = await self._repository.create(
            user_id=user_id,
            order_id=data.order_id,
            amount=str(data.amount),
            currency=data.currency,
            method=data.method,
            transaction_id=transaction_id,
        )

        return self._to_response(payment)

    @staticmethod
    def _to_response(payment) -> PaymentResponse:
        return PaymentResponse(
            id=payment.id,
            user_id=payment.user_id,
            order_id=payment.order_id,
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status.value,
            method=payment.method.value,
            transaction_id=payment.transaction_id,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
        )


class ProcessPaymentUseCase:
    def __init__(self, repository: IPaymentRepository) -> None:
        self._repository = repository

    async def execute(self, payment_id: int, user_id: int) -> PaymentStatusResponse:
        # Get payment
        payment = await self._repository.get_by_id_for_user(payment_id, user_id)
        if not payment:
            raise PaymentNotFoundError(f"Payment {payment_id} not found")

        # Validate status transition
        if payment.status != PaymentStatus.PENDING:
            raise InvalidPaymentStatusError(
                f"Cannot process payment with status {payment.status}"
            )

        # Simulate payment processing (in real scenario, call payment gateway)
        try:
            # Simulate success (90% chance)
            import random

            is_success = random.random() < 0.9

            new_status = PaymentStatus.COMPLETED if is_success else PaymentStatus.FAILED

            updated_payment = await self._repository.update_status(
                payment_id, new_status, payment.transaction_id
            )

            return PaymentStatusResponse(
                payment_id=updated_payment.id,
                status=updated_payment.status.value,
                transaction_id=updated_payment.transaction_id,
                updated_at=updated_payment.updated_at,
            )
        except Exception as e:
            await self._repository.update_status(
                payment_id, PaymentStatus.FAILED, payment.transaction_id
            )
            raise PaymentProcessingError(f"Payment processing failed: {str(e)}")


class GetPaymentUseCase:
    def __init__(self, repository: IPaymentRepository) -> None:
        self._repository = repository

    async def execute(self, payment_id: int, user_id: int) -> PaymentResponse:
        payment = await self._repository.get_by_id_for_user(payment_id, user_id)
        if not payment:
            raise PaymentNotFoundError(f"Payment {payment_id} not found")

        return PaymentResponse(
            id=payment.id,
            user_id=payment.user_id,
            order_id=payment.order_id,
            amount=payment.amount,
            currency=payment.currency,
            status=payment.status.value,
            method=payment.method.value,
            transaction_id=payment.transaction_id,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
        )


class GetAllPaymentsUseCase:
    def __init__(self, repository: IPaymentRepository) -> None:
        self._repository = repository

    async def execute(self, user_id: int) -> PaymentsListResponse:
        payments = await self._repository.get_all_for_user(user_id)

        return PaymentsListResponse(
            payments=[
                PaymentResponse(
                    id=p.id,
                    user_id=p.user_id,
                    order_id=p.order_id,
                    amount=p.amount,
                    currency=p.currency,
                    status=p.status.value,
                    method=p.method.value,
                    transaction_id=p.transaction_id,
                    created_at=p.created_at,
                    updated_at=p.updated_at,
                )
                for p in payments
            ]
        )


class RefundPaymentUseCase:
    def __init__(self, repository: IPaymentRepository) -> None:
        self._repository = repository

    async def execute(self, payment_id: int, user_id: int) -> PaymentStatusResponse:
        payment = await self._repository.get_by_id_for_user(payment_id, user_id)
        if not payment:
            raise PaymentNotFoundError(f"Payment {payment_id} not found")

        # Validate status transition
        PaymentValidationService.validate_payment_status_transition(
            payment.status, PaymentStatus.REFUNDED
        )

        # Process refund
        updated_payment = await self._repository.update_status(
            payment_id, PaymentStatus.REFUNDED, payment.transaction_id
        )

        return PaymentStatusResponse(
            payment_id=updated_payment.id,
            status=updated_payment.status.value,
            transaction_id=updated_payment.transaction_id,
            updated_at=updated_payment.updated_at,
        )
