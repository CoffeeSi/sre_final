from decimal import Decimal
from app.domain.models import PaymentStatus, PaymentMethod
from app.domain.exceptions import InvalidAmountError, InvalidPaymentStatusError


class PaymentValidationService:
    @staticmethod
    def validate_amount(amount: Decimal) -> None:
        if amount <= 0:
            raise InvalidAmountError("Payment amount must be greater than 0")

    @staticmethod
    def validate_payment_status_transition(
        current_status: PaymentStatus, new_status: PaymentStatus
    ) -> None:
        """Validate if transition between statuses is allowed"""
        allowed_transitions = {
            PaymentStatus.PENDING: [PaymentStatus.COMPLETED, PaymentStatus.FAILED],
            PaymentStatus.COMPLETED: [PaymentStatus.REFUNDED],
            PaymentStatus.FAILED: [PaymentStatus.PENDING],
            PaymentStatus.REFUNDED: [],
        }

        if new_status not in allowed_transitions.get(current_status, []):
            raise InvalidPaymentStatusError(
                f"Cannot transition from {current_status} to {new_status}"
            )

    @staticmethod
    def validate_payment_method(method: str) -> None:
        """Validate payment method"""
        valid_methods = [m.value for m in PaymentMethod]
        if method not in valid_methods:
            raise ValueError(f"Invalid payment method: {method}")
