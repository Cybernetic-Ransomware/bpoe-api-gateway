from fastapi import APIRouter, Depends, Security, Request
from fastapi.params import Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, SecurityScopes
from fastapi_auth0 import Auth0, Auth0User
from httpx import AsyncClient

from src.auth.config import auth
from src.auth.exceptions import ExchangeTokenException
from src.auth.utils import RoleVerifier
# from src.auth.models import TokenRequest
from src.config import AUTH0_DOMAIN, AUTH0_CLIENT_SECRET, APP_CLIENT_ID, AUTH0_API_AUDIENCE


class Auth0HTTPBearer(HTTPBearer):
    async def __call__(self, request: Request):
        return await super().__call__(request)

class CustomAuth0(Auth0):
    def __init__(self, domain: str, api_audience: str, scopes: dict = {}, **kwargs):
        super().__init__(domain, api_audience, scopes, **kwargs)

    async def get_user(self, security_scopes: SecurityScopes, creds: HTTPAuthorizationCredentials | None = Depends(Auth0HTTPBearer(auto_error=False)), raw_request: Request = None) -> Auth0User | None:
        if creds is None:
            access_token = raw_request.session.get("access_token") if raw_request else None
            if not access_token:
                access_token = raw_request.cookies.get("session") if raw_request else None

            if not access_token:
                raise ExchangeTokenException(code=403, verbose="Missing bearer token")

            creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=access_token)

        return await super().get_user(security_scopes, creds)

router = APIRouter()
token_auth_scheme = HTTPBearer()

authorizer = CustomAuth0(domain=AUTH0_DOMAIN, api_audience=AUTH0_API_AUDIENCE, email_auto_error=True)

@router.get("/")
async def public_endpoint():
    return {"message": "This is a public endpoint. No authentication required."}

@router.get("/priv", dependencies=[Depends(authorizer.implicit_scheme)])
async def get_private(
    request: Request,
    user: Auth0User = Security(authorizer.get_user)
) -> dict[str, str]:
    scheme = authorizer.implicit_scheme
    user = user
    return {"message": f"Hello World {user.email} but in private."}

@router.get("/exchange-token")
async def exchange_token(request: Request, code: str = Query(..., description="Exchange Token")):
    token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
    async with AsyncClient() as client:
        res = await client.post(
            token_url,
            json={
                "grant_type": "client_credentials",
                "client_id": APP_CLIENT_ID,
                "client_secret": AUTH0_CLIENT_SECRET,
                "audience": AUTH0_API_AUDIENCE,
                "code": code,
                "redirect_uri": "http://127.0.0.1:8070/index.html",
            },
        )

        if res.status_code != 200:
            raise ExchangeTokenException(code=res.status_code, verbose=str(res.text))

        token_data = res.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise ExchangeTokenException(code=500)
        print(code, flush=True)
        print(access_token, flush=True)
        request.session["access_token"] = access_token
        return {"message": "Token exchanged and stored in session"}
