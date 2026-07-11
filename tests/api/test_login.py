import pytest
from test_framework import verify
from test_framework.report import requirement
from test_framework.steplog import step


@pytest.mark.api
@requirement("REQ-1024")
def test_reject_login_with_invalid_credentials(api_client):
    with step("POST credentials bad@user.com / wrong"):
        resp = api_client.post("/login", json={"email": "bad@user.com", "password": "wrong"})

    with step("Verify response"):
        verify.status(resp, 401)
        verify.equals(resp.json()["error"], "Invalid credentials", "error message")


@pytest.mark.api
@pytest.mark.parametrize(
    "email,password,status",
    [
        ("bad@user.com", "wrong", 401),
        ("", "", 422),
    ],
)
def test_login_rejects(api_client, email, password, status):
    with step(f"POST credentials {email!r}"):
        resp = api_client.post("/login", json={"email": email, "password": password})
    verify.status(resp, status)
