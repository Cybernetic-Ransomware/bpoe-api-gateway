from typing import Annotated

from fastapi import APIRouter, Depends, Security, Response, Request, Query
from fastapi.params import Query
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_auth0 import Auth0User
from httpx import AsyncClient

from src.auth.config import auth
from src.auth.exceptions import ExchangeTokenException
from src.auth.utils import RoleVerifier
# from src.auth.models import TokenRequest
from src.config import AUTH0_DOMAIN, AUTH0_CLIENT_SECRET, APP_CLIENT_ID, APP_ALLLOWED_CALLBACK_URL

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

# @router.post("cookie")
# async def cookie_callback(request: Request, response: Response):
#     print("Authentication in progress", flush=True)
#     token = request.session.get("access_token")
#     if not token:
#         raise ExchangeTokenException(code=500)
#     response.set_cookie(key="auth_token", value="token", max_age=3600, httponly=True, secure=False)
#     print("Authenticated", flush=True)
#     return{"message": "Session cookie set"}

@router.get("/exchange-token")
async def exchange_token(request: Request, code: str = Query(..., description="Exchange Token")):
    token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
    async with AsyncClient() as client:
        res = await client.post(
            token_url,
            json={
                "grant_type": "authorization_code",
                "client_id": APP_CLIENT_ID,
                "client_secret": AUTH0_CLIENT_SECRET,
                "code": code,
                # "redirect_uri": "http://localhost:8080/log/cookie",  # + endpoint /callback; zrób redirect na fron; request.session (by nie przechowywaćw localstorage, a w cookie tworzonym przez backend)
                # "redirect_uri": "http://127.0.0.1:8080/docs",
                "redirect_uri": "http://127.0.0.1:8070/index.html",
            },
        )
        # print(res.status_code, flush=True)
        # print(res.text, flush=True)

        print(res, flush=True)
        if res.status_code != 200:
            print(res.text, flush=True)
            raise ExchangeTokenException(res.status_code)

        token_data = res.json()
        access_token = token_data.get("access_token")
        print(access_token, flush=True)
        if not access_token:
            raise ExchangeTokenException(code=500)

        request.session["access_token"] = access_token
        return {"message": "Token exchanged and stored in session"}