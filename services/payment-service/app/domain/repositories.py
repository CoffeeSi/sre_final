from abc import ABC, abstractmethod
from typing import Optional, List

from app.domain.models import Payment, PaymentStatus


class IPaymentRepository(ABC):
    @abstractmethod
    async def create(
        self,
        user_id: int,
        order_id: int,
        amount: str,
        currency: str,
        method: str,
        transaction_id: Optional[str] = None,
    ) -> Payment:
        pass

    @abstractmethod
    async def get_by_id(self, payment_id: int) -> Optional[Payment]:
        pass

    @abstractmethod
    async def get_by_id_for_user(
        self, payment_id: int, user_id: int
    ) -> Optional[Payment]:
        pass

    @abstractmethod
    async def get_all_for_user(self, user_id: int) -> List[Payment]:
        pass

    @abstractmethod
    async def get_by_order_id(self, order_id: int) -> Optional[Payment]:
        pass

    @abstractmethod
    async def update_status(
        self,
        payment_id: int,
        status: PaymentStatus,
        transaction_id: Optional[str] = None,
    ) -> Payment:
        pass

    @abstractmethod
    async def get_pending_payments(self) -> List[Payment]:
        pass
