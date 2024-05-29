import pytest
from unittest.mock import patch
from lab_share_lib.config_readers import (
    get_config,
    get_redpanda_schema_registry,
    get_basic_publisher,
)


@pytest.fixture
def schema_registry_class():
    with patch("lab_share_lib.config_readers.SchemaRegistry") as schema_registry:
        yield schema_registry


@pytest.fixture
def basic_publisher_class():
    with patch("lab_share_lib.config_readers.BasicPublisher") as basic_publisher:
        yield basic_publisher


@pytest.fixture
def rabbit_server_details_class():
    with patch("lab_share_lib.config_readers.RabbitServerDetails") as rsd:
        yield rsd


def test_get_config():
    with pytest.raises(ModuleNotFoundError):
        get_config("x.y.z")


def test_get_redpanda_schema_registry(config, schema_registry_class):
    actual = get_redpanda_schema_registry(config)

    assert actual == schema_registry_class.return_value
    schema_registry_class.assert_called_once_with(config.REDPANDA_BASE_URI)


@pytest.mark.parametrize(
    "given_username, expected_username", [[None, "admin"], ["", "admin"], ["username", "username"]]
)
@pytest.mark.parametrize(
    "given_password, expected_password", [[None, "development"], ["", "development"], ["password", "password"]]
)
def test_get_basic_publisher(
    config,
    given_username,
    expected_username,
    given_password,
    expected_password,
    rabbit_server_details_class,
    basic_publisher_class,
):
    actual = get_basic_publisher(config, username=given_username, password=given_password)

    assert actual == basic_publisher_class.return_value

    rabbit_server_details_class.assert_called_once_with(
        uses_ssl=config.RABBITMQ_SSL,
        host=config.RABBITMQ_HOST,
        port=config.RABBITMQ_PORT,
        username=expected_username,
        password=expected_password,
        vhost=config.RABBITMQ_VHOST,
    )

    basic_publisher_class.assert_called_once_with(
        rabbit_server_details_class.return_value, config.RABBITMQ_PUBLISH_RETRY_DELAY, config.RABBITMQ_PUBLISH_RETRIES
    )
