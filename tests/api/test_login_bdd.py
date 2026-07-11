import pytest
from pytest_bdd import scenarios

scenarios("../../features/api/login.feature")

pytestmark = pytest.mark.api
