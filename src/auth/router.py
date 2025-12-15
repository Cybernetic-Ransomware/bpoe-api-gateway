import base64
import hashlib
import logging
import secrets

from fastapi import APIRouter, Depends, Security, Request, Body
from fastapi.security import HTTPBearer
from fastapi_auth0 import Auth0User
from httpx import AsyncClient
from pydantic import BaseModel

from src.config import (
    AUTH0_DOMAIN,
    AUTH0_CLIENT_SECRET,
    APP_CLIENT_ID,
    AUTH0_API_AUDIENCE,
    APP_ALLLOWED_CALLBACK_URL,
)
from src.auth.exceptions import ExchangeTokenException
from src.auth.utils import CustomAuth0


router = APIRouter()
token_auth_scheme = HTTPBearer()

authorizer = CustomAuth0(domain=AUTH0_DOMAIN, api_audience=AUTH0_API_AUDIENCE, email_auto_error=True)
logger = logging.getLogger(__name__)


class TokenExchangePayload(BaseModel):
    code: str
    state: str


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


def _generate_state() -> str:
    return secrets.token_urlsafe(32)


def _generate_code_verifier() -> str:
    return secrets.token_urlsafe(64)


def _code_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("utf-8")


@router.get("/auth/context")
async def get_auth_context(request: Request) -> dict[str, str]:
    """Returns PKCE parameters and stores them in the session for later verification."""
    state = _generate_state()
    code_verifier = _generate_code_verifier()
    challenge = _code_challenge(code_verifier)

    request.session["oauth_state"] = state
    request.session["pkce_code_verifier"] = code_verifier
    request.session["redirect_uri"] = APP_ALLLOWED_CALLBACK_URL

    return {
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "redirect_uri": APP_ALLLOWED_CALLBACK_URL,
        "client_id": APP_CLIENT_ID,
        "auth0_domain": AUTH0_DOMAIN,
    }


@router.post("/exchange-token")
async def exchange_token(request: Request, payload: TokenExchangePayload = Body(...)):  # noqa: B008
    expected_state = request.session.get("oauth_state")
    if not expected_state or payload.state != expected_state:
        logger.warning("Auth0 code exchange rejected due to state mismatch")
        raise ExchangeTokenException(code=403, verbose="Invalid OAuth state parameter")

    code_verifier = request.session.get("pkce_code_verifier")
    if not code_verifier:
        raise ExchangeTokenException(code=400, verbose="Missing PKCE verifier. Restart login flow.")

    redirect_uri = request.session.get("redirect_uri") or APP_ALLLOWED_CALLBACK_URL
    token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
    logger.info(
        "Starting Auth0 code exchange",
        extra={
            "auth0_domain": AUTH0_DOMAIN,
            "audience": AUTH0_API_AUDIENCE,
            "code_digest": _hash_for_log(payload.code),
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
                "code": payload.code,
                "redirect_uri": redirect_uri,
                "code_verifier": code_verifier,
            },
        )

        if res.status_code != 200:
            logger.warning(
                "Auth0 code exchange failed",
                extra={
                    "status_code": res.status_code,
                    "code_digest": _hash_for_log(payload.code),
                },
            )
            raise ExchangeTokenException(code=res.status_code, verbose=str(res.text))

        token_data = res.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise ExchangeTokenException(code=500)

        # Clean up single-use values
        request.session.pop("oauth_state", None)
        request.session.pop("pkce_code_verifier", None)
        request.session.pop("redirect_uri", None)

        request.session["access_token"] = access_token
        logger.info(
            "Auth0 code exchange succeeded",
            extra={
                "code_digest": _hash_for_log(payload.code),
                "access_token_digest": _hash_for_log(access_token),
            },
        )
        return {"message": "Token exchanged and stored in session"}
