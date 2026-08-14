import re
import time
import uuid
from collections import defaultdict, deque
from threading import Lock

from starlette.datastructures import MutableHeaders
from starlette.responses import JSONResponse

from app.config.settings import settings


class SecurityHeadersMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request_id = None
        for key, value in scope.get("headers", []):
            if key.lower() == b"x-request-id":
                candidate = value.decode("utf-8", "ignore")[:100]
                # Só ecoa identificadores simples; entradas arbitrárias são descartadas.
                if re.fullmatch(r"[A-Za-z0-9._:-]{1,100}", candidate):
                    request_id = candidate
                break
        request_id = request_id or str(uuid.uuid4())
        scope["vynce.request_id"] = request_id

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["X-Content-Type-Options"] = "nosniff"
                headers["X-Frame-Options"] = "DENY"
                headers["Referrer-Policy"] = "no-referrer"
                headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=(), usb=()"
                headers["Content-Security-Policy"] = "default-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"
                headers["Cross-Origin-Opener-Policy"] = "same-origin"
                headers["Cross-Origin-Resource-Policy"] = "same-origin"
                headers["X-Permitted-Cross-Domain-Policies"] = "none"
                headers["Origin-Agent-Cluster"] = "?1"
                headers["Cache-Control"] = "no-store"
                headers["Pragma"] = "no-cache"
                headers["X-Request-ID"] = request_id
                if not settings.DEBUG:
                    headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            await send(message)

        await self.app(scope, receive, send_wrapper)


class RequestBodyLimitMiddleware:
    """Bloqueia payloads grandes mesmo quando chegam em chunks."""

    def __init__(self, app, max_bytes: int):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        for key, value in scope.get("headers", []):
            if key.lower() == b"content-length":
                try:
                    if int(value) > self.max_bytes:
                        response = JSONResponse({"detail": "Requisição muito grande."}, status_code=413)
                        return await response(scope, receive, send)
                except ValueError:
                    pass

        total = 0

        async def limited_receive():
            nonlocal total
            message = await receive()
            if message["type"] == "http.request":
                total += len(message.get("body", b""))
                if total > self.max_bytes:
                    raise RequestTooLarge
            return message

        try:
            await self.app(scope, limited_receive, send)
        except RequestTooLarge:
            response = JSONResponse({"detail": "Requisição muito grande."}, status_code=413)
            await response(scope, receive, send)


class RequestTooLarge(Exception):
    pass


class InMemoryRateLimitMiddleware:
    """
    Proteção de abuso por IP sem dependências externas.
    Funciona por processo; em múltiplas instâncias, complemente com Redis/WAF.
    """

    def __init__(self, app):
        self.app = app
        self._events = defaultdict(deque)
        self._lock = Lock()

    @staticmethod
    def _client_ip(scope) -> str:
        client = scope.get("client")
        return client[0] if client else "unknown"

    @staticmethod
    def _rule(path: str, method: str) -> tuple[str, int, int]:
        if path == "/auth/forgot-password" or path == "/auth/resend-verification":
            return "password-recovery", settings.PASSWORD_RECOVERY_LIMIT_PER_15_MINUTES, 900
        if path.startswith("/auth/"):
            return "auth", settings.AUTH_RATE_LIMIT_PER_15_MINUTES, 900
        # Um bucket geral por IP/método evita cardinalidade alta com paths aleatórios.
        return "api", settings.API_RATE_LIMIT_PER_MINUTE, 60

    def _allowed(self, key: str, limit: int, window: int) -> tuple[bool, int]:
        now = time.monotonic()
        cutoff = now - window
        with self._lock:
            bucket = self._events[key]
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= limit:
                retry_after = max(1, int(window - (now - bucket[0])))
                return False, retry_after
            bucket.append(now)
            # limpeza oportunista
            if len(self._events) > 20000:
                for old_key in list(self._events.keys())[:2000]:
                    if not self._events[old_key] or self._events[old_key][-1] <= cutoff:
                        self._events.pop(old_key, None)
            return True, 0

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        path = scope.get("path", "")
        method = scope.get("method", "GET")

        # healthcheck não deve ser bloqueado pelo próprio monitoramento.
        if path == "/health":
            return await self.app(scope, receive, send)

        bucket, limit, window = self._rule(path, method)
        ip = self._client_ip(scope)
        allowed, retry_after = self._allowed(f"{ip}:{method}:{bucket}", limit, window)

        if not allowed:
            response = JSONResponse(
                {"detail": "Muitas requisições. Aguarde e tente novamente."},
                status_code=429,
                headers={"Retry-After": str(retry_after)},
            )
            return await response(scope, receive, send)

        await self.app(scope, receive, send)
