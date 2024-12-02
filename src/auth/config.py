from src.config import AUTH0_DOMAIN, AUTH0_API_AUDIENCE, AUTH0_ISSUER, AUTH0_ALGORITHMS
from fastapi_auth0 import Auth0

auth = Auth0(domain=AUTH0_DOMAIN, api_audience=AUTH0_API_AUDIENCE)


def set_up():
    """Sets up configuration for the app"""

    config = {
        "DOMAIN": AUTH0_DOMAIN,
        "API_AUDIENCE": AUTH0_API_AUDIENCE,
        "ISSUER": AUTH0_ISSUER,
        "ALGORITHMS": AUTH0_ALGORITHMS,
    }

    return config
