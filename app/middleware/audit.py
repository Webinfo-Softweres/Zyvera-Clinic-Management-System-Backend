import contextvars
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import decode_token

request_context = contextvars.ContextVar("request_context", default={})

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract IP and Endpoint
        ip_address = request.client.host if request.client else None
        endpoint = request.url.path

        # Try to extract user ID from auth header
        user_id = None
        centre_code = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = decode_token(token)
            if payload:
                user_id = payload.get("sub")
                centre_code = payload.get("centre_code")

        request_context.set({
            "ip_address": ip_address,
            "endpoint": endpoint,
            "user_id": user_id,
            "centre_code": centre_code
        })

        response = await call_next(request)
        return response
