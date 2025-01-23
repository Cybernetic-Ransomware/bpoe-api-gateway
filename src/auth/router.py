from fastapi import APIRouter, Depends, Security, Request
from fastapi.params import Query
from fastapi.security import HTTPBearer
from fastapi_auth0 import Auth0User
from httpx import AsyncClient

from src.config import AUTH0_DOMAIN, AUTH0_CLIENT_SECRET, APP_CLIENT_ID, AUTH0_API_AUDIENCE
from src.auth.exceptions import ExchangeTokenException
from src.auth.utils import CustomAuth0


router = APIRouter()
token_auth_scheme = HTTPBearer()

authorizer = CustomAuth0(domain=AUTH0_DOMAIN, api_audience=AUTH0_API_AUDIENCE, email_auto_error=True)

@router.get("/")
async def public_endpoint():
    return {"message": "This is a public endpoint. No authentication required."}

@router.get("/priv", dependencies=[Depends(authorizer.implicit_scheme)])
async def get_private(
    request: Request,
    user: Auth0User = Security(authorizer.get_user)  # noqa: B008
) -> dict[str, str]:
    user = user
    return {"message": f"Hello World {user.email} but in private."}

@router.get("/exchange-token")
async def exchange_token(request: Request, code: str = Query(..., description="Exchange Token")):
    token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
    async with AsyncClient() as client:
        res = await client.post(
            token_url,
            headers={'content-type': "application/json"},
            json={
                # "grant_type": "client_credentials",
                "grant_type": "authorization_code",
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
