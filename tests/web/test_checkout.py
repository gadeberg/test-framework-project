import pytest
from playwright.sync_api import expect
from test_framework import verify
from test_framework.steplog import step

from support.pages.checkout import CheckoutPage


@pytest.mark.ui
def test_place_order(page, base_url):
    checkout = CheckoutPage(page, base_url)

    with step("Go to the checkout page"):
        checkout.goto()

    with step('Fill in "item" with "Gadget" and place the order'):
        checkout.locator("item").fill("Gadget")
        checkout.locator("place-order").click()

    with step("Verify confirmation"):
        confirmation = checkout.locator("confirmation")
        expect(confirmation).to_contain_text("Order placed for Gadget")
        verify.contains(confirmation.inner_text(), "Order placed for Gadget", "confirmation text")
