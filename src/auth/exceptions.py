from fastapi import HTTPException


class PermissionsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=403,
            detail="Access denied: insufficient permissions"
        )

class TokenVerificationException(HTTPException):
    def __init__(self, detail: str = "Token verification failed."):
        super().__init__(
            status_code=401,
            detail=detail
        )

class InvalidTokenSignatureException(HTTPException):
    def __init__(self, detail: str = "Invalid token signature."):
        super().__init__(
            status_code=401,
            detail=detail
        )

class TokenDecodeException(HTTPException):
    def __init__(self, detail: str = "Failed to decode token."):
        super().__init__(
            status_code=400,
            detail=detail
        )

class InvalidClaimException(HTTPException):
    def __init__(self, claim_name: str):
        super().__init__(
            status_code=400,
            detail=f"No valid claim '{claim_name}' found in token or invalid type."
        )

class InsufficientClaimException(HTTPException):
    def __init__(self, claim_name: str, missing_value: str):
        super().__init__(
            status_code=403,
            detail=(
                f"Insufficient {claim_name}. Missing required value: '{missing_value}'."
            )
        )

class ExchangeTokenException(HTTPException):
    def __init__(self, code, verbose: str = ""):
        super().__init__(
            status_code=code,
            detail=f"Failed to exchange authorization code. {verbose}"
        )
