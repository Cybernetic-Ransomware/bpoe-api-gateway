import sentry_sdk

from src.config import SENTRY_DSN, SENTRY_TRACES_SAMPLE_RATE, SENTRY_PROFILES_SAMPLE_RATE


def init_sentry() -> None:
    """Initialize Sentry only when a DSN is provided."""
    if not SENTRY_DSN:
        return

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        send_default_pii=False,
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
        profiles_sample_rate=SENTRY_PROFILES_SAMPLE_RATE,
    )
