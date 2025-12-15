"""Pytest fixtures and environment setup for the BPOE API Gateway."""

from __future__ import annotations

import os
from pathlib import Path
from typing import AsyncIterator
from unittest import mock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

TEST_ENV_FILE = Path(__file__).resolve().parent / ".env.test"


def _load_test_env() -> None:
    """Load key=value pairs from .env.test and inject them into os.environ."""
    if not TEST_ENV_FILE.exists():
        return

    for line in TEST_ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_load_test_env()


def _patch_auth0_jwks() -> None:
    """Avoid real network calls performed by fastapi-auth0 during startup."""
    import json
    import urllib.request

    jwks_payload = {
        "keys": [
            {
                "kty": "RSA",
                "kid": "test-key-id",
                "use": "sig",
                "n": "sXch1ZI5qm4ZQYc5CZ2pT6apnTjearchS9uZH4xFQFU3jtg1pDCzsE1",
                "e": "AQAB",
            }
        ]
    }

    def fake_urlopen(url, *args, **kwargs):  # noqa: ANN001
        if str(url).endswith("/.well-known/jwks.json"):
            response = mock.Mock()
            response.read.return_value = json.dumps(jwks_payload).encode("utf-8")
            return response
        raise RuntimeError(f"Unexpected URL during test: {url}")

    mock.patch.object(urllib.request, "urlopen", side_effect=fake_urlopen).start()


_patch_auth0_jwks()


@pytest.fixture(scope="session")
def app():
    """Return the FastAPI application instance for ASGI tests."""
    from src.main import app as fastapi_app

    return fastapi_app


@pytest_asyncio.fixture
async def async_client(app) -> AsyncIterator[AsyncClient]:
    """HTTPX client bound to the FastAPI ASGI app with cookie support."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
