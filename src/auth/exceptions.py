from fastapi import HTTPException


permissions_exception = HTTPException(status_code=403,
                                      detail="Access denied: insufficient permissions")
