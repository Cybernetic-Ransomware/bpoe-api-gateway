# Config Module

The `src.config` module centralizes environment-variable access for the API Gateway. It ensures:

- `.env` files are read from `./docker` (matching the template location).
- All Auth0/App/Sentry secrets live in one place.
- CORS origins are validated early to prevent insecure deployments.

---

::: src.config
