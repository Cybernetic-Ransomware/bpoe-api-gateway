from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from src.auth.router import router as auth_router
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="some-random-string")

app.include_router(auth_router, prefix="/log", tags=["auth"])


@app.get("/")
async def root():
    return {"message": "Hello World"}
