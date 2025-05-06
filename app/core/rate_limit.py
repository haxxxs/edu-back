from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import time
from typing import Dict, Tuple
from collections import defaultdict

# Simple in-memory store for rate limiting
# In production, you might want to use Redis or similar
rate_limit_store: Dict[str, Dict[str, Tuple[int, float]]] = defaultdict(dict)

async def check_rate_limit(request: Request, times: int = 100, minutes: int = 1) -> None:
    """
    Check if the request exceeds the rate limit
    :param request: FastAPI request object
    :param times: Number of allowed requests in the time window
    :param minutes: Time window in minutes
    :raises: HTTPException if rate limit is exceeded
    """
    # Get client IP
    client_ip = request.client.host
    endpoint = request.url.path
    key = f"{client_ip}:{endpoint}"

    # Get current timestamp
    now = time.time()
    time_window = minutes * 60

    # Clean up old entries
    rate_limit_store[endpoint] = {
        k: v for k, v in rate_limit_store[endpoint].items()
        if now - v[1] < time_window
    }

    # Check if client has exceeded rate limit
    if key in rate_limit_store[endpoint]:
        count, timestamp = rate_limit_store[endpoint][key]
        if now - timestamp < time_window:
            if count >= times:
                raise HTTPException(
                    status_code=HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Try again in {int(time_window - (now - timestamp))} seconds"
                )
            rate_limit_store[endpoint][key] = (count + 1, timestamp)
        else:
            rate_limit_store[endpoint][key] = (1, now)
    else:
        rate_limit_store[endpoint][key] = (1, now) 