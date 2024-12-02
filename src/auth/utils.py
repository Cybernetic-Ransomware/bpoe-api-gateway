import jwt

from typing import Any

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.auth.config import set_up
from src.auth.exceptions import TokenVerificationException, InvalidTokenSignatureException, TokenDecodeException, InvalidClaimException, InsufficientClaimException, PermissionsException


token_auth_scheme = HTTPBearer()


class VerifyToken:
    def __init__(self, token: str, permissions: str | None = None, scopes: str | None = None, role: str | None = None):
        self.config = set_up()
        self.token = token
        self.permissions = permissions
        self.scopes = scopes
        self.role = role
        self.signing_key = None

        jwks_url = f'https://{self.config["DOMAIN"]}/.well-known/jwks.json'
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    def verify(self) -> {str: Any}:
        try:
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(
                self.token
            ).key
        except jwt.exceptions.PyJWKClientError as error:
            raise TokenVerificationException(detail=str(error))
        except jwt.exceptions.DecodeError as error:
            raise InvalidTokenSignatureException(detail=str(error))

        try:
            payload = jwt.decode(
                self.token,
                self.signing_key,
                algorithms=self.config["ALGORITHMS"],
                audience=self.config["API_AUDIENCE"],
                issuer=self.config["ISSUER"],
            )
        except jwt.exceptions.ExpiredSignatureError:
            raise TokenDecodeException(detail="Token has expired.")
        except jwt.exceptions.InvalidAudienceError:
            raise TokenDecodeException(detail="Invalid audience in token.")
        except Exception as error:
            raise TokenDecodeException(detail=str(error))

        if 'email' not in payload:
            raise InvalidClaimException('email')

        if self.scopes:
            self._check_claims(payload, 'scope', str, self.scopes.split(' '))

        if self.permissions:
            self._check_claims(payload, 'permissions', list, self.permissions)

        if self.role:
            self._check_claims(payload, 'customField/roles', list, self.role)

        return payload

    @staticmethod
    def _check_claims(payload: {str: Any}, claim_name: str, claim_type: Any, expected_value: [str]) -> {str: Any}:
        if claim_name not in payload or not isinstance(payload[claim_name], claim_type):
            raise InvalidClaimException(claim_name)

        payload_claim = payload[claim_name]

        if claim_name == 'scope':
            payload_claim = payload[claim_name].split(' ')

        if claim_name == 'customField/roles':
            payload_claim = payload[claim_name]

        for value in expected_value:
            if value not in payload_claim:
                raise InsufficientClaimException(claim_name, value)

        return {"status": "success", "status_code": 200}


class RoleVerifier:
    def __init__(self, token: HTTPAuthorizationCredentials, allowed_roles: list[str] | None):
        self.token = token
        self.allowed_roles = allowed_roles

    def verify(self) -> bool:
        auth = VerifyToken(self.token.credentials).verify()

        if not self.allowed_roles:
            return True

        if any(role in auth.get('customField/roles') for role in self.allowed_roles):
            return True
        else:
            raise PermissionsException()
