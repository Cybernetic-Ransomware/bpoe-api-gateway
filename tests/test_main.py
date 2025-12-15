import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_docs_endpoint(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_public_endpoint(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/log/")
    assert response.status_code == 200
    assert response.json() == {"message": "This is a public endpoint. No authentication required."}
