"""Validação de URLs de saída para reduzir risco de SSRF."""
from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


class SSRFValidationError(ValueError):
    pass


def _is_public_ip(value: str) -> bool:
    ip = ipaddress.ip_address(value)
    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def validate_outbound_url(url: str, *, allow_private: bool = False) -> str:
    parsed = urlparse(str(url).strip())

    if parsed.scheme not in {"https", "http"}:
        raise SSRFValidationError("A URL deve usar HTTP ou HTTPS.")

    if not parsed.hostname:
        raise SSRFValidationError("URL sem hostname válido.")

    if parsed.username or parsed.password:
        raise SSRFValidationError("Credenciais embutidas na URL não são permitidas.")

    if parsed.port not in (None, 80, 443):
        raise SSRFValidationError("Porta não permitida.")

    host = parsed.hostname.rstrip(".").lower()

    if allow_private:
        return str(url).rstrip("/")

    try:
        ip = ipaddress.ip_address(host)
        if not _is_public_ip(str(ip)):
            raise SSRFValidationError("A URL aponta para um endereço de rede privada ou reservado.")
    except ValueError:
        try:
            infos = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)
        except socket.gaierror as exc:
            raise SSRFValidationError("Não foi possível resolver o hostname.") from exc

        addresses = {info[4][0] for info in infos}
        if not addresses or any(not _is_public_ip(addr) for addr in addresses):
            raise SSRFValidationError("O hostname pode apontar para uma rede privada ou reservada.")

    return str(url).rstrip("/")
