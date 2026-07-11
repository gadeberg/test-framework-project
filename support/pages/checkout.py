from test_framework.ui.pages.base import BasePage


class CheckoutPage(BasePage):
    path = "/checkout-page"
    locators = {
        "item": "#item",
        "place-order": "#place-order",
        "confirmation": "#confirmation",
    }
