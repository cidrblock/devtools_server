"""Fixtures for the tests."""

import subprocess
import time

from typing import Generator

import pytest


@pytest.fixture(scope="session")
def server() -> Generator[str, None, None]:
    """Run the server."""
    with subprocess.Popen(["devtools-server", "runserver"]) as proc:
        time.sleep(2)  # allow the server to start
        yield "http://localhost:8000"
        proc.terminate()
