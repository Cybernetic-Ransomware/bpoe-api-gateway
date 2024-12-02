from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.auth.config import auth
from src.auth.utils import RoleVerifier


router = APIRouter()
token_auth_scheme = HTTPBearer()


@router.get("/priv", dependencies=[Depends(auth.implicit_scheme)])
async def get_private():
    return {"message": "Hello World but in prvate"}


def verify_roles(token: HTTPAuthorizationCredentials = Depends(token_auth_scheme), allowed_roles: list[str | None] = None) -> bool:
    verifier = RoleVerifier(token, allowed_roles)
    return verifier.verify()
