from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.application.schemas import (
    CreatePaymentRequest,
    PaymentResponse,
    PaymentsListResponse,
    PaymentStatusResponse,
    ProcessPaymentRequest,
)
from app.application.use_cases import (
    CreatePaymentUseCase,
    ProcessPaymentUseCase,
    GetPaymentUseCase,
    GetAllPaymentsUseCase,
    RefundPaymentUseCase,
)
from app.domain.exceptions import (
    PaymentNotFoundError,
    InvalidPaymentStatusError,
    PaymentProcessingError,
    InvalidAmountError,
)
from app.interfaces.dependencies import (
    get_current_user_id,
    get_create_payment_use_case,
    get_process_payment_use_case,
    get_get_payment_use_case,
    get_get_all_payments_use_case,
    get_refund_payment_use_case,
)

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {"service": "payment-service", "status": "ok"}


@router.post("/payments", response_model=PaymentResponse, status_code=201)
async def create_payment(
    payload: CreatePaymentRequest,
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    use_case: Annotated[CreatePaymentUseCase, Depends(get_create_payment_use_case)],
) -> PaymentResponse:
    try:
        return await use_case.execute(payload, user_id=current_user_id)
    except InvalidAmountError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PaymentProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/payments", response_model=PaymentsListResponse)
async def get_all_payments(
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    use_case: Annotated[GetAllPaymentsUseCase, Depends(get_get_all_payments_use_case)],
) -> PaymentsListResponse:
    return await use_case.execute(user_id=current_user_id)


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    use_case: Annotated[GetPaymentUseCase, Depends(get_get_payment_use_case)],
) -> PaymentResponse:
    try:
        return await use_case.execute(payment_id=payment_id, user_id=current_user_id)
    except PaymentNotFoundError:
        raise HTTPException(status_code=404, detail="Payment not found")


@router.post("/payments/{payment_id}/process", response_model=PaymentStatusResponse)
async def process_payment(
    payment_id: int,
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    use_case: Annotated[ProcessPaymentUseCase, Depends(get_process_payment_use_case)],
) -> PaymentStatusResponse:
    try:
        return await use_case.execute(payment_id=payment_id, user_id=current_user_id)
    except PaymentNotFoundError:
        raise HTTPException(status_code=404, detail="Payment not found")
    except InvalidPaymentStatusError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PaymentProcessingError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/payments/{payment_id}/refund", response_model=PaymentStatusResponse)
async def refund_payment(
    payment_id: int,
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    use_case: Annotated[RefundPaymentUseCase, Depends(get_refund_payment_use_case)],
) -> PaymentStatusResponse:
    try:
        return await use_case.execute(payment_id=payment_id, user_id=current_user_id)
    except PaymentNotFoundError:
        raise HTTPException(status_code=404, detail="Payment not found")
    except InvalidPaymentStatusError as e:
        raise HTTPException(status_code=400, detail=str(e))
