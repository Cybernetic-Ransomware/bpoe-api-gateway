"""Environment configuration helper for the BPOE API Gateway."""

from decouple import config, Csv


config.search_path = "./docker"

AUTH0_CLIENT_ID = config("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = config("AUTH0_CLIENT_SECRET")
AUTH0_DOMAIN = config("AUTH0_DOMAIN")
APP_SECRET_KEY = config("APP_SECRET_KEY")
APP_CLIENT_ID = config("APP_CLIENT_ID")
APP_ALLLOWED_CALLBACK_URL = config("APP_ALLLOWED_CALLBACK_URL")
AUTH0_API_AUDIENCE = config("AUTH0_API_AUDIENCE")
AUTH0_ISSUER = config("AUTH0_ISSUER")
AUTH0_ALGORITHMS = config("AUTH0_ALGORITHMS")
SENTRY_DSN = config("SENTRY_DSN", default=None)
SENTRY_TRACES_SAMPLE_RATE = config("SENTRY_TRACES_SAMPLE_RATE", default=0.0, cast=float)
SENTRY_PROFILES_SAMPLE_RATE = config("SENTRY_PROFILES_SAMPLE_RATE", default=0.0, cast=float)
raw_cors_origins = config(
    "CORS_ALLOWED_ORIGINS",
    cast=Csv(),
    default="http://localhost,http://localhost:8080,http://127.0.0.1:8080,http://localhost:8070,http://127.0.0.1:8070",
)

if not raw_cors_origins:
    raise RuntimeError("CORS_ALLOWED_ORIGINS cannot be empty. Provide at least one allowed origin.")

for origin in raw_cors_origins:
    if not origin.startswith(("http://", "https://")):
        raise RuntimeError(f"Invalid CORS origin '{origin}'. Use explicit scheme (http/https).")

CORS_ALLOWED_ORIGINS = [origin.strip().rstrip("/") for origin in raw_cors_origins if origin]
