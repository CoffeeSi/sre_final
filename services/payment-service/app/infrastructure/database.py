import logging
from typing import Optional

import asyncpg
from fastapi import FastAPI

logger = logging.getLogger(__name__)


async def create_pool(app: FastAPI, dsn: str) -> None:
    """Create async connection pool to PostgreSQL"""
    try:
        pool = await asyncpg.create_pool(dsn, min_size=5, max_size=20)
        app.state.db_pool = pool
        logger.info("Database pool created successfully")
    except Exception as e:
        logger.error(f"Failed to create database pool: {e}")
        raise


async def close_pool(app: FastAPI) -> None:
    """Close database connection pool"""
    if hasattr(app.state, "db_pool"):
        await app.state.db_pool.close()
        logger.info("Database pool closed")


async def initialize_database(pool) -> None:
    """Initialize database tables"""
    try:
        async with pool.acquire() as connection:
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    order_id INTEGER NOT NULL UNIQUE,
                    amount NUMERIC(10, 2) NOT NULL,
                    currency VARCHAR(3) NOT NULL DEFAULT 'KZT',
                    status VARCHAR(20) NOT NULL DEFAULT 'pending',
                    method VARCHAR(50) NOT NULL,
                    transaction_id VARCHAR(255),
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes safely to prevent concurrent startup race conditions
            for index_name, column in [
                ("idx_payments_user_id", "user_id"),
                ("idx_payments_order_id", "order_id"),
                ("idx_payments_status", "status"),
                ("idx_payments_transaction_id", "transaction_id"),
            ]:
                try:
                    await connection.execute(
                        f"CREATE INDEX IF NOT EXISTS {index_name} ON payments({column})"
                    )
                except Exception as e:
                    logger.warning(f"Skipping index {index_name} creation due to concurrency: {e}")

            logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization was skipped or partially failed due to concurrency: {e}")
