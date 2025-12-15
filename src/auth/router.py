import hashlib
import logging

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
logger = logging.getLogger(__name__)


@router.get("/")
async def public_endpoint():
    return {"message": "This is a public endpoint. No authentication required."}


@router.get("/priv", dependencies=[Depends(authorizer.implicit_scheme)])
async def get_private(
    request: Request,
    user: Auth0User = Security(authorizer.get_user),  # noqa: B008
) -> dict[str, str]:
    user = user
    return {"message": f"Hello World {user.email} but in private."}


def _hash_for_log(value: str) -> str:
    """Returns short, non-reversible digest for correlating sensitive values in logs."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


@router.get("/exchange-token")
async def exchange_token(request: Request, code: str = Query(..., description="Exchange Token")):
    token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
    logger.info(
        "Starting Auth0 code exchange",
        extra={
            "auth0_domain": AUTH0_DOMAIN,
            "audience": AUTH0_API_AUDIENCE,
            "code_digest": _hash_for_log(code),
        },
    )
    async with AsyncClient() as client:
        res = await client.post(
            token_url,
            headers={"content-type": "application/json"},
            json={
                "grant_type": "authorization_code",
                "client_id": APP_CLIENT_ID,
                "client_secret": AUTH0_CLIENT_SECRET,
                "audience": AUTH0_API_AUDIENCE,
                "code": code,
                "redirect_uri": "http://127.0.0.1:8070/index.html",
            },
        )

        if res.status_code != 200:
            logger.warning(
                "Auth0 code exchange failed",
                extra={
                    "status_code": res.status_code,
                    "code_digest": _hash_for_log(code),
                },
            )
            raise ExchangeTokenException(code=res.status_code, verbose=str(res.text))

        token_data = res.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise ExchangeTokenException(code=500)

        request.session["access_token"] = access_token
        logger.info(
            "Auth0 code exchange succeeded",
            extra={
                "code_digest": _hash_for_log(code),
                "access_token_digest": _hash_for_log(access_token),
            },
        )
        return {"message": "Token exchanged and stored in session"}
