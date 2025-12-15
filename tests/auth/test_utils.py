from types import SimpleNamespace

import pytest
from fastapi.security import SecurityScopes

from src.auth.exceptions import ExchangeTokenException
from src.auth.utils import CustomAuth0


@pytest.mark.asyncio
async def test_get_user_uses_session_token(monkeypatch):
    custom = CustomAuth0(domain="dummy.auth0.com", api_audience="https://dummy/api")
    captured = {}

    async def fake_super(self, security_scopes, creds):  # noqa: ARG001
        captured["creds"] = creds
        return {"sub": "user"}

    monkeypatch.setattr("src.auth.utils.Auth0.get_user", fake_super)

    request = SimpleNamespace(session={"access_token": "abc123"}, cookies={})
    user = await custom.get_user(SecurityScopes(), request=request, creds=None)

    assert user == {"sub": "user"}
    assert captured["creds"].credentials == "abc123"


@pytest.mark.asyncio
async def test_get_user_raises_when_session_missing(monkeypatch):
    custom = CustomAuth0(domain="dummy.auth0.com", api_audience="https://dummy/api")

    async def fake_super(self, security_scopes, creds):  # pragma: no cover
        return {}

    monkeypatch.setattr("src.auth.utils.Auth0.get_user", fake_super)

    request = SimpleNamespace(session={}, cookies={})
    with pytest.raises(ExchangeTokenException):
        await custom.get_user(SecurityScopes(), request=request, creds=None)
