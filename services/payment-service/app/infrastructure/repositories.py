import logging
from typing import Optional, List

import asyncpg

from app.domain.models import Payment, PaymentStatus, PaymentMethod
from app.domain.repositories import IPaymentRepository

logger = logging.getLogger(__name__)


class PaymentRepository(IPaymentRepository):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def create(
        self,
        user_id: int,
        order_id: int,
        amount: str,
        currency: str,
        method: str,
        transaction_id: Optional[str] = None,
    ) -> Payment:
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(
                """
                INSERT INTO payments 
                (user_id, order_id, amount, currency, status, method, transaction_id)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING id, user_id, order_id, amount, currency, status, method, 
                          transaction_id, created_at, updated_at
                """,
                user_id,
                order_id,
                amount,
                currency,
                PaymentStatus.PENDING.value,
                method,
                transaction_id,
            )
            return self._row_to_payment(row)

    async def get_by_id(self, payment_id: int) -> Optional[Payment]:
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(
                """
                SELECT id, user_id, order_id, amount, currency, status, method,
                       transaction_id, created_at, updated_at
                FROM payments
                WHERE id = $1
                """,
                payment_id,
            )
            return self._row_to_payment(row) if row else None

    async def get_by_id_for_user(
        self, payment_id: int, user_id: int
    ) -> Optional[Payment]:
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(
                """
                SELECT id, user_id, order_id, amount, currency, status, method,
                       transaction_id, created_at, updated_at
                FROM payments
                WHERE id = $1 AND user_id = $2
                """,
                payment_id,
                user_id,
            )
            return self._row_to_payment(row) if row else None

    async def get_all_for_user(self, user_id: int) -> List[Payment]:
        async with self._pool.acquire() as connection:
            rows = await connection.fetch(
                """
                SELECT id, user_id, order_id, amount, currency, status, method,
                       transaction_id, created_at, updated_at
                FROM payments
                WHERE user_id = $1
                ORDER BY created_at DESC
                """,
                user_id,
            )
            return [self._row_to_payment(row) for row in rows]

    async def get_by_order_id(self, order_id: int) -> Optional[Payment]:
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(
                """
                SELECT id, user_id, order_id, amount, currency, status, method,
                       transaction_id, created_at, updated_at
                FROM payments
                WHERE order_id = $1
                """,
                order_id,
            )
            return self._row_to_payment(row) if row else None

    async def update_status(
        self,
        payment_id: int,
        status: PaymentStatus,
        transaction_id: Optional[str] = None,
    ) -> Payment:
        async with self._pool.acquire() as connection:
            query_params = [status.value, payment_id]
            if transaction_id:
                query = """
                    UPDATE payments
                    SET status = $1, transaction_id = $3, updated_at = CURRENT_TIMESTAMP
                    WHERE id = $2
                    RETURNING id, user_id, order_id, amount, currency, status, method,
                              transaction_id, created_at, updated_at
                """
                query_params.insert(2, transaction_id)
            else:
                query = """
                    UPDATE payments
                    SET status = $1, updated_at = CURRENT_TIMESTAMP
                    WHERE id = $2
                    RETURNING id, user_id, order_id, amount, currency, status, method,
                              transaction_id, created_at, updated_at
                """

            row = await connection.fetchrow(query, *query_params)
            return self._row_to_payment(row)

    async def get_pending_payments(self) -> List[Payment]:
        async with self._pool.acquire() as connection:
            rows = await connection.fetch(
                """
                SELECT id, user_id, order_id, amount, currency, status, method,
                       transaction_id, created_at, updated_at
                FROM payments
                WHERE status = $1
                """,
                PaymentStatus.PENDING.value,
            )
            return [self._row_to_payment(row) for row in rows]

    @staticmethod
    def _row_to_payment(row: asyncpg.Record) -> Payment:
        return Payment(
            id=row["id"],
            user_id=row["user_id"],
            order_id=row["order_id"],
            amount=row["amount"],
            currency=row["currency"],
            status=PaymentStatus(row["status"]),
            method=PaymentMethod(row["method"]),
            transaction_id=row["transaction_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
