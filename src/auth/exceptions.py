"""Custom HTTP exceptions tailored for the BPOE AuthService flows."""

from fastapi import HTTPException


class PermissionsException(HTTPException):
    """Raised when a user lacks sufficient permissions for an operation."""

    def __init__(self):
        super().__init__(status_code=403, detail="Access denied: insufficient permissions")


class TokenVerificationException(HTTPException):
    """Raised when a token cannot be verified against the issuer's public keys."""

    def __init__(self, detail: str = "Token verification failed."):
        super().__init__(status_code=401, detail=detail)


class InvalidTokenSignatureException(HTTPException):
    """Raised when the JWT signature is invalid or tampered with."""

    def __init__(self, detail: str = "Invalid token signature."):
        super().__init__(status_code=401, detail=detail)


class TokenDecodeException(HTTPException):
    """Raised when decoding of the JWT payload fails (e.g., malformed token)."""

    def __init__(self, detail: str = "Failed to decode token."):
        super().__init__(status_code=400, detail=detail)


class InvalidClaimException(HTTPException):
    """Raised when a required claim is missing or of incorrect type."""

    def __init__(self, claim_name: str):
        super().__init__(status_code=400, detail=f"No valid claim '{claim_name}' found in token or invalid type.")


class InsufficientClaimException(HTTPException):
    """Raised when the user claim exists but lacks a required value."""

    def __init__(self, claim_name: str, missing_value: str):
        super().__init__(status_code=403, detail=(f"Insufficient {claim_name}. Missing required value: '{missing_value}'."))


class ExchangeTokenException(HTTPException):
    """Raised when exchanging the authorization code for tokens fails."""

    def __init__(self, code, verbose: str = ""):
        super().__init__(status_code=code, detail=f"Failed to exchange authorization code. {verbose}")


class AuthContextRateLimitException(HTTPException):
    """Raised when clients request PKCE/state context too frequently."""

    def __init__(self, retry_after_seconds: int | None = None):
        headers = {}
        if retry_after_seconds is not None:
            headers["Retry-After"] = str(retry_after_seconds)
        super().__init__(
            status_code=429,
            detail="Too many authentication context requests. Please wait before retrying.",
            headers=headers,
        )
