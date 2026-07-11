import pytest
from pytest_bdd import scenarios

scenarios("../../features/web/checkout.feature")

pytestmark = pytest.mark.ui
