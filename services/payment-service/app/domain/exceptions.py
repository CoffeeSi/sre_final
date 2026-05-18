class PaymentServiceError(Exception):
    """Base exception for payment service"""

    pass


class PaymentNotFoundError(PaymentServiceError):
    """Payment not found"""

    pass


class InvalidPaymentStatusError(PaymentServiceError):
    """Invalid payment status for operation"""

    pass


class PaymentProcessingError(PaymentServiceError):
    """Error during payment processing"""

    pass


class InsufficientFundsError(PaymentServiceError):
    """Insufficient funds for payment"""

    pass


class OrderNotFoundError(PaymentServiceError):
    """Order not found"""

    pass


class InvalidAmountError(PaymentServiceError):
    """Invalid payment amount"""

    pass
