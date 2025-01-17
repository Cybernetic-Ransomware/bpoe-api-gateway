from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, SecurityScopes

from fastapi_auth0 import Auth0, Auth0User

from src.auth.exceptions import ExchangeTokenException


class Auth0HTTPBearer(HTTPBearer):
    async def __call__(self, request: Request):
        return await super().__call__(request)

class CustomAuth0(Auth0):
    def __init__(self, domain: str, api_audience: str, scopes: dict = None, **kwargs):
        if scopes is None:
            scopes = {}

        super().__init__(domain, api_audience, scopes, **kwargs)

    async def get_user(self,
                       security_scopes: SecurityScopes,
                       creds: HTTPAuthorizationCredentials | None = Depends(Auth0HTTPBearer(auto_error=False)),
                       raw_request: Request = None
                       ) -> Auth0User | None:
        if creds is None:
            access_token = raw_request.session.get("access_token") if raw_request else None
            if not access_token:
                access_token = raw_request.cookies.get("session") if raw_request else None

            if not access_token:
                raise ExchangeTokenException(code=403, verbose="Missing bearer token")

            creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=access_token)

        return await super().get_user(security_scopes, creds)
