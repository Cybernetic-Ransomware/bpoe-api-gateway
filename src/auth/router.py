from typing import Annotated

from fastapi import APIRouter, Depends, Security
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from fastapi_auth0 import Auth0User

from src.auth.config import auth
from src.config import APP_CLIENT_ID, APP_ALLLOWED_CALLBACK_URL
from src.auth.utils import RoleVerifier


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

@router.get("/priv", dependencies=[Depends(auth.implicit_scheme)])
async def get_private(
        user: Annotated[Auth0User, Security(auth.get_user)],
        valid_roles: Annotated[bool, Depends(verify_roles)]) -> dict[str, str]:
    return {"message": f"Hello World but in prvate {user.id}, {user.email}"}
