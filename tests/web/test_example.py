"""Copy-paste template for a new UI test.

Copy this file, rename it, change the body: arrange (page object) -> `with
step(...)` actions -> `verify.*` checks. Selectors live only in the page
object (`support/pages/`), never here.
"""

import pytest
from test_framework import verify
from test_framework.steplog import step

from support.pages.login import LoginPage


@pytest.mark.ui
def test_login_page_shows_email_field(page, base_url):
    login = LoginPage(page, base_url)

    with step("Go to the login page"):
        login.goto()

    with step("Verify the email field is visible"):
        verify.is_true(login.locator("email").is_visible(), "email field visible")
