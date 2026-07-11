"""Copy-paste template for a new API test.

Copy this file, rename it, change the body: arrange (fixtures) -> `with
step(...)` actions -> `verify.*` checks. Add `@requirement("REQ-xxxx")` to
trace it to a requirement.
"""

import pytest
from test_framework import verify
from test_framework.steplog import step


@pytest.mark.api
def test_health_check_responds_ok(api_client):
    with step("GET /health"):
        resp = api_client.get("/health")

    with step("Verify response"):
        verify.status(resp, 200)
        verify.equals(resp.json()["ok"], True, "health flag")
