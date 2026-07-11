"""Starts the bundled mock app once per session and wires it as the base_url
for both API and UI examples, and registers this project's page objects.

Set the ``BASE_URL`` environment variable to point the suite at a real
deployment instead; the mock is then never started."""

from __future__ import annotations

import os
import socket
import threading
import time
from collections.abc import Generator

import httpx
import pytest
import uvicorn
from test_framework.ui.pages.base import BasePage

from support.mockapp.app import app
from support.pages.checkout import CheckoutPage
from support.pages.login import LoginPage


@pytest.fixture(scope="session")
def mock_server_base_url() -> Generator[str, None, None]:
    # Bind the socket ourselves and hand it to uvicorn: the OS-assigned port
    # is never released in between, so another process (or xdist worker)
    # can't grab it before the server starts listening.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=lambda: server.run(sockets=[sock]), daemon=True)
    thread.start()

    base = f"http://127.0.0.1:{port}"
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        try:
            httpx.get(f"{base}/health", timeout=0.2)
            break
        except httpx.HTTPError:
            time.sleep(0.05)
    else:
        raise RuntimeError("mock server did not start in time")

    yield base

    server.should_exit = True
    thread.join(timeout=5)


@pytest.fixture(scope="session")
def base_url(request: pytest.FixtureRequest) -> str:
    external = os.environ.get("BASE_URL")
    if external:
        # Strip any trailing slash so path concatenation can't produce "//"
        # (the mock's URL below never carries one either).
        return external.rstrip("/")
    # Lazy: the offline mock only starts when no real target is given.
    return request.getfixturevalue("mock_server_base_url")


@pytest.fixture
def page_registry() -> dict[str, type[BasePage]]:
    return {"login": LoginPage, "checkout": CheckoutPage}
