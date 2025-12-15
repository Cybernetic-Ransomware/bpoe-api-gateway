from importlib import reload

import src.config as base_config
import src.auth.config as auth_config


def _reload_with_env(monkeypatch, **env):
    for key, value in env.items():
        monkeypatch.setenv(key, value)

    reload(base_config)
    return reload(auth_config)


def test_set_up_returns_expected_keys(monkeypatch):
    reloaded = _reload_with_env(
        monkeypatch,
        AUTH0_DOMAIN="patched-domain.auth0.com",
        AUTH0_API_AUDIENCE="https://patched/api",
        AUTH0_ISSUER="https://patched-domain.auth0.com/",
        AUTH0_ALGORITHMS="RS256",
    )

    config_dict = reloaded.set_up()

    assert config_dict == {
        "DOMAIN": "patched-domain.auth0.com",
        "API_AUDIENCE": "https://patched/api",
        "ISSUER": "https://patched-domain.auth0.com/",
        "ALGORITHMS": "RS256",
    }


def test_auth_instance_exposed(monkeypatch):
    reloaded = _reload_with_env(
        monkeypatch,
        AUTH0_DOMAIN="dummy.auth0.com",
        AUTH0_API_AUDIENCE="https://dummy/api",
        AUTH0_ISSUER="https://dummy.auth0.com/",
        AUTH0_ALGORITHMS="RS256",
    )

    assert hasattr(reloaded, "auth")
    assert reloaded.auth.domain == "dummy.auth0.com"
