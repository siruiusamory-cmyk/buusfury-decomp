import os


def pytest_configure(config):
    base = os.environ.get("PYTEST_DEBUG_TEMPROOT")
    if base:
        os.makedirs(base, exist_ok=True)
