import sentry_sdk

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from starlette.middleware.sessions import SessionMiddleware

from src.auth.router import router as auth_router


sentry_sdk.init(
    dsn="https://49e6307f9d7c96aefb5e6bf8f308576f@o4509011278495745.ingest.de.sentry.io/4509011283935312",
    send_default_pii=True,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:8080/",
    "http://localhost:8070/",
    "http://127.0.0.1:8070/",
    "*",
]


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
app.include_router(auth_router, prefix="/log", tags=["auth"])


@app.get("/")
async def root():
    return {"message": "Hello World"}
