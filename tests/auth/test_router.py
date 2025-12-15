import pytest


@pytest.mark.asyncio
async def test_auth_context_returns_pkce(async_client):
    response = await async_client.get("/log/auth/context")
    assert response.status_code == 200
    data = response.json()
    assert data["code_challenge_method"] == "S256"
    assert data["state"]
    assert data["code_challenge"]
    assert data["redirect_uri"]


@pytest.mark.asyncio
async def test_auth_context_rate_limit(async_client):
    for _ in range(5):
        resp = await async_client.get("/log/auth/context")
        assert resp.status_code == 200

    resp = await async_client.get("/log/auth/context")
    assert resp.status_code == 429
    assert resp.json()["detail"].startswith("Too many authentication context requests")


@pytest.mark.asyncio
async def test_exchange_token_state_mismatch(async_client):
    await async_client.get("/log/auth/context")
    resp = await async_client.post(
        "/log/exchange-token",
        json={"code": "dummy-code", "state": "invalid-state"},
    )
    assert resp.status_code == 403
    assert "Invalid OAuth state parameter" in resp.json()["detail"]
