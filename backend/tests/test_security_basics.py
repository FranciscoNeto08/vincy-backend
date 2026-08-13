import os
import pytest

os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_security.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-" + "x" * 40)

from app.config.settings import settings
from app.utils.ssrf import SSRFValidationError, validate_outbound_url
from app.utils.unsubscribe import generate_unsubscribe_token, verify_unsubscribe_token


def test_ssrf_rejects_loopback():
    with pytest.raises(SSRFValidationError):
        validate_outbound_url("http://127.0.0.1:8000")


def test_ssrf_rejects_private_ip():
    with pytest.raises(SSRFValidationError):
        validate_outbound_url("http://10.0.0.1")


def test_unsubscribe_token_roundtrip():
    token = generate_unsubscribe_token(10, 20)
    assert verify_unsubscribe_token(token) == (10, 20)


def test_unsubscribe_token_tampering_fails():
    token = generate_unsubscribe_token(10, 20)
    tampered = token[:-1] + ("A" if token[-1] != "A" else "B")
    assert verify_unsubscribe_token(tampered) is None
