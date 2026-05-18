import logging
import os
from typing import Optional

import aiohttp
import jwt

logger = logging.getLogger(__name__)

ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:8003")
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


async def get_order_details(order_id: int, user_id: int) -> Optional[dict]:
    """Fetch order details from order service"""
    try:
        # Build a signed JWT so order-service can validate the caller's identity
        token = jwt.encode({"sub": str(user_id)}, JWT_SECRET, algorithm=JWT_ALGORITHM)
        headers = {"Authorization": f"Bearer {token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{ORDER_SERVICE_URL}/orders/{order_id}",
                headers=headers,
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None
    except Exception as e:
        logger.error(f"Error fetching order details: {e}")
        return None
