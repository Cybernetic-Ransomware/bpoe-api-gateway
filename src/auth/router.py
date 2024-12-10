from typing import Annotated

from fastapi import APIRouter, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from fastapi_auth0 import Auth0User

from src.auth.config import auth
from src.auth.utils import RoleVerifier


router = APIRouter()
token_auth_scheme = HTTPBearer()

def verify_roles(
        token: Annotated[HTTPAuthorizationCredentials,Depends(token_auth_scheme)],
        allowed_roles: list[str | None] = None) -> bool:
    verifier = RoleVerifier(token, allowed_roles)
    return verifier.verify()

@router.get("/priv", dependencies=[Depends(auth.implicit_scheme)])
async def get_private(
        user: Annotated[Auth0User, Security(auth.get_user)],
        valid_roles: Annotated[bool, Depends(verify_roles)]) -> dict[str, str]:
    return {"message": f"Hello World but in prvate {user.id}, {user.email}"}
