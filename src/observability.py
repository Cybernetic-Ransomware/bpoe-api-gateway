"""Telemetry helpers for the BPOE API Gateway."""

import sentry_sdk

from src.config import SENTRY_DSN, SENTRY_TRACES_SAMPLE_RATE, SENTRY_PROFILES_SAMPLE_RATE


def init_sentry() -> None:
    """
    Initialize Sentry SDK if a DSN is provided via configuration.

    Returns:
        None

    Notes:
        - Enables tracing/profiling using the configured sampling rates.
        - Skips initialization entirely when `SENTRY_DSN` is empty (e.g., local dev).
    """
    if not SENTRY_DSN:
        return

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        send_default_pii=False,
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
        profiles_sample_rate=SENTRY_PROFILES_SAMPLE_RATE,
    )
