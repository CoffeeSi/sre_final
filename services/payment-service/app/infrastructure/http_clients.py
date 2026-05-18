import logging
import os
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)

ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:8003")


async def get_order_details(order_id: int, user_id: int) -> Optional[dict]:
    """Fetch order details from order service"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{ORDER_SERVICE_URL}/orders/{order_id}",
                headers={"Authorization": f"Bearer {user_id}"},
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None
    except Exception as e:
        logger.error(f"Error fetching order details: {e}")
        return None
