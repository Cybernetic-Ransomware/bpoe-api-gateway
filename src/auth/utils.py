"""Utilities extending the fastapi-auth0 integration for BPOE gateway."""

from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, SecurityScopes

from fastapi_auth0 import Auth0, Auth0User

from src.auth.exceptions import ExchangeTokenException


class Auth0HTTPBearer(HTTPBearer):
    """Wrapper around FastAPI HTTPBearer allowing reuse inside dependency injection."""

    async def __call__(self, request: Request):
        """
        Extract bearer credentials from the incoming request.

        Args:
            request: FastAPI request carrying potential `Authorization` header.

        Returns:
            HTTPAuthorizationCredentials | None: Credentials parsed by the base HTTPBearer.
        """
        return await super().__call__(request)


class CustomAuth0(Auth0):
    """Auth0 helper that falls back to session-stored tokens when headers are missing."""

    def __init__(self, domain: str, api_audience: str, scopes: dict | None = None, **kwargs):
        """
        Initialize the Auth0 helper with optional scope overrides.

        Args:
            domain: Auth0 tenant domain.
            api_audience: API identifier configured in Auth0.
            scopes: Optional mapping of scope names to descriptions.
            **kwargs: Extra arguments forwarded to `fastapi_auth0.Auth0`.
        """
        if scopes is None:
            scopes = {}

        super().__init__(domain, api_audience, scopes, **kwargs)

    async def get_user(
        self,
        security_scopes: SecurityScopes,
        request: Request,
        creds: HTTPAuthorizationCredentials | None = Depends(Auth0HTTPBearer(auto_error=False)),  # noqa: B008
    ) -> Auth0User | None:
        """
        Resolve the Auth0 user, loading the bearer token from the session when missing.

        Args:
            security_scopes: FastAPI security scopes requested by the endpoint.
            request: FastAPI request with session storage (used to fetch `access_token`).
            creds: Bearer credentials supplied via header (optional).

        Returns:
            Auth0User | None: Authenticated user information from Auth0.

        Raises:
            ExchangeTokenException: If neither header nor session provides a bearer token.
        """
        if creds is None:
            access_token = request.session.get("access_token")
            if not access_token:
                raise ExchangeTokenException(code=403, verbose="Missing bearer token")

            creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=access_token)

        return await super().get_user(security_scopes, creds)
