from typing import Annotated

from fastapi import APIRouter, Depends, Security
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_auth0 import Auth0User
from httpx import AsyncClient

from src.auth.config import auth
from src.auth.utils import RoleVerifier
from src.auth.models import TokenRequest
from src.config import AUTH0_DOMAIN, AUTH0_CLIENT_SECRET, APP_CLIENT_ID, APP_ALLLOWED_CALLBACK_URL
from src.exceptions import ExchangeTokenException


router = APIRouter()
token_auth_scheme = HTTPBearer()


def check_token(token: HTTPAuthorizationCredentials = Depends(token_auth_scheme)) -> RedirectResponse | str:
    if not token or not token.credentials:
        login_url = (
            f"https://{auth.AUTH0_DOMAIN}/authorize?"
            f"response_type=token&client_id={APP_CLIENT_ID}"
            f"&redirect_uri={APP_ALLLOWED_CALLBACK_URL}&audience={auth.AUDIENCE}"
        )
        return RedirectResponse(url=login_url)
    return token.credentials

def verify_roles(
        token: Annotated[HTTPAuthorizationCredentials, Depends(check_token)],
        allowed_roles: list[str | None] = None) -> bool:
    verifier = RoleVerifier(token, allowed_roles)
    return verifier.verify()

@router.get("/")
async def public_endpoint():
    return {"message": "This is a public endpoint. No authentication required."}

@router.get("/priv", dependencies=[Depends(auth.implicit_scheme)])
async def get_private(
        user: Annotated[Auth0User, Security(auth.get_user)],
        valid_roles: Annotated[bool, Depends(verify_roles)]) -> dict[str, str]:
    return {"message": f"Hello World but in prvate {user.id}, {user.email}"}


@router.post("/exchange-token")
async def exchange_token(request: TokenRequest):
    token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
    async with AsyncClient() as client:
        response = await client.post(
            token_url,
            json={
                "grant_type": "authorization_code",
                "client_id": APP_CLIENT_ID,
                "client_secret": AUTH0_CLIENT_SECRET,
                "code": request.auth_code,
                "redirect_uri": "http://localhost:8000/log/",  # + endpoint /callback; zrób redirect na fron; request.session (by nie przechowywaćw localstorage, a w cookie tworzonym przez backend)
            },
        )
        print(response.status_code, flush=True)
        print(response.text, flush=True)
        if response.status_code != 200:
            raise ExchangeTokenException(response.status_code)
        return response.json()
