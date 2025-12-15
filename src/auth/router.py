import base64
import hashlib
import logging
import secrets
import time

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
from src.auth.exceptions import ExchangeTokenException, AuthContextRateLimitException
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
    """
    Health-style endpoint showing the gateway responds without authentication.

    Returns:
        dict[str, str]: Static message confirming the service is reachable.
    """
    return {"message": "This is a public endpoint. No authentication required."}


@router.get("/priv", dependencies=[Depends(authorizer.implicit_scheme)])
async def get_private(
    request: Request,
    user: Auth0User = Security(authorizer.get_user),  # noqa: B008
) -> dict[str, str]:
    """
    Return greeting visible only to authenticated users resolved by Auth0.

    Args:
        request: Incoming FastAPI request (unused but kept for parity with other handlers).
        user: Auth0-resolved user injected via dependency.

    Returns:
        dict[str, str]: Message containing the authenticated user's email.
    """
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


AUTH_CONTEXT_RATE_WINDOW_SECONDS = 60
AUTH_CONTEXT_RATE_LIMIT = 5


def _enforce_auth_context_rate_limit(request: Request) -> None:
    now = time.time()
    history_key = "auth_context_hits"
    hits = request.session.get(history_key, [])
    hits = [ts for ts in hits if now - ts < AUTH_CONTEXT_RATE_WINDOW_SECONDS]
    if len(hits) >= AUTH_CONTEXT_RATE_LIMIT:
        retry_after = int(AUTH_CONTEXT_RATE_WINDOW_SECONDS - (now - hits[0])) if hits else None
        raise AuthContextRateLimitException(retry_after_seconds=retry_after)

    hits.append(now)
    request.session[history_key] = hits


@router.get("/auth/context")
async def get_auth_context(request: Request) -> dict[str, str]:
    """
    Generate PKCE/state parameters and persist them in the session for later validation.

    Args:
        request: FastAPI request containing session storage used to persist PKCE values.

    Returns:
        dict[str, str]: Payload with state, code challenge, redirect URI and metadata used by the SPA.
    """
    _enforce_auth_context_rate_limit(request)
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
    """
    Exchange Auth0 authorization code for tokens after validating state and PKCE verifier.

    Args:
        request: FastAPI request containing the session that stores PKCE/context values.
        payload: Body with the authorization `code` and `state` returned from Auth0 redirect.

    Returns:
        dict[str, str]: Confirmation message informing that the access token is stored in session.
    """
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
