import time
from collections import defaultdict, deque
from typing import override

from fastapi import Request, Response
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_429_TOO_MANY_REQUESTS
from starlette.middleware.base import BaseHTTPMiddleware


# starlette is installed when fastapi is installed.
# BaseHTTPMiddleware is the class we inherit from to create custom middleware in FastAPI/Starlette.



RATE_LIMIT_REQUESTS = 50
RATE_LIMIT_WINDOW_SECONDS = 3600

# Stores recent request timestamps for each client IP address.
# defaultdict(deque) means a new IP automatically starts with an empty queue.
requests_by_ip: dict[str, deque[float]] = defaultdict(deque)


class RateLimitMiddleware(BaseHTTPMiddleware):
    @override
    async def dispatch(self, request: Request, call_next):
        # If Starlette cannot identify the client, we stop early instead of putting
        # every unknown client into the same "unknown" rate-limit bucket.
        if request.client is None:
            return Response(
                content="Client IP address could not be identified",
                status_code=HTTP_400_BAD_REQUEST,
            )

        # At this point request.client exists, so it is safe to read the client IP
        client_ip = request.client.host

        # Store the current request time once so the same timestamp is used for
        # cleanup and for recording this request if it is allowed.
        current_time = time.time()

        # Clean old timestamps from the global request store before accessing or
        # creating the current client's bucket.
        clear_expired_requests(current_time)

        # Get the timestamp queue for this client IP.
        # If the IP has not been seen before, defaultdict creates an empty deque.
        request_times = requests_by_ip[client_ip]

        # If the client has already used all allowed requests in the current window,
        # return 429 instead of passing the request through to the normal route.
        if len(request_times) >= RATE_LIMIT_REQUESTS:
            return Response(
                content="Rate Limit exceeded",
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                headers={"Retry-After": str(RATE_LIMIT_WINDOW_SECONDS)},
            )
        # Record this request because it is within the allowed limit.
        request_times.append(current_time)

        # Continue to the next middleware or route handler.
        return await call_next(request)


def clear_expired_requests(current_time: float) -> None:
    # Anything before this timestamp is outside the active rate-limit window.
    oldest_allowed_time = current_time - RATE_LIMIT_WINDOW_SECONDS

    # list(...) is used because empty client buckets may be deleted while looping.
    for client_ip, request_times in list(requests_by_ip.items()):
        # Remove request timestamps that are older than the current window.
        while request_times and request_times[0] < oldest_allowed_time:
            request_times.popleft()

        # If the client has no recent requests left, remove the IP from the global
        # store so requests_by_ip does not grow forever.
        if not request_times:
            del requests_by_ip[client_ip]
