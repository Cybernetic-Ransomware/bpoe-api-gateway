from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from starlette.middleware.sessions import SessionMiddleware

from src.auth.router import router as auth_router
from src.config import APP_SECRET_KEY
from src.observability import init_sentry

init_sentry()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:8080/",
    "http://localhost:8070/",
    "http://127.0.0.1:8070/",
    "*",
]


if not APP_SECRET_KEY:
    raise RuntimeError("APP_SECRET_KEY must be defined before starting the API gateway.")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=APP_SECRET_KEY)
app.include_router(auth_router, prefix="/log", tags=["auth"])


@app.get("/")
async def root():
    return {"message": "Hello World"}
