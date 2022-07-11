import pytest


@pytest.fixture
def config():
    return type("Config", (object,), {"PROCESSORS": {}})
