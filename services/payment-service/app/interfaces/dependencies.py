from typing import Annotated
import os

import jwt
from fastapi import Depends, HTTPException, Request
from app.application.use_cases import (
    CreatePaymentUseCase,
    ProcessPaymentUseCase,
    GetPaymentUseCase,
    GetAllPaymentsUseCase,
    RefundPaymentUseCase,
)
from app.infrastructure.repositories import PaymentRepository

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key")


async def get_current_user_id(request: Request) -> int:
    """Extract user ID from JWT token"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid authorization header"
        )

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return int(sub)
    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_payment_repository(request: Request) -> PaymentRepository:
    """Dependency for payment repository"""
    pool = request.app.state.db_pool
    return PaymentRepository(pool)


async def get_create_payment_use_case(
    repository: Annotated[PaymentRepository, Depends(get_payment_repository)],
) -> CreatePaymentUseCase:
    return CreatePaymentUseCase(repository)


async def get_process_payment_use_case(
    repository: Annotated[PaymentRepository, Depends(get_payment_repository)],
) -> ProcessPaymentUseCase:
    return ProcessPaymentUseCase(repository)


async def get_get_payment_use_case(
    repository: Annotated[PaymentRepository, Depends(get_payment_repository)],
) -> GetPaymentUseCase:
    return GetPaymentUseCase(repository)


async def get_get_all_payments_use_case(
    repository: Annotated[PaymentRepository, Depends(get_payment_repository)],
) -> GetAllPaymentsUseCase:
    return GetAllPaymentsUseCase(repository)


async def get_refund_payment_use_case(
    repository: Annotated[PaymentRepository, Depends(get_payment_repository)],
) -> RefundPaymentUseCase:
    return RefundPaymentUseCase(repository)
