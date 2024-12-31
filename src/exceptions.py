from fastapi import HTTPException


class ExchangeTokenException(HTTPException):
    def __init__(self, code):
        super().__init__(
            status_code=code,
            detail="Failed to exchange authorization code."
        )
