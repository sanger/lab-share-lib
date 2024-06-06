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


def test_get_config():
    with pytest.raises(ModuleNotFoundError):
        get_config("x.y.z")


def test_get_redpanda_schema_registry(config, schema_registry_class):
    actual = get_redpanda_schema_registry(config)

    assert actual == schema_registry_class.return_value
    schema_registry_class.assert_called_once_with(config.REDPANDA_BASE_URI)


def test_get_basic_publisher(
    rabbit_server_details,
    config,
    basic_publisher_class,
):
    actual = get_basic_publisher(rabbit_server_details, config)

    assert actual == basic_publisher_class.return_value

    basic_publisher_class.assert_called_once_with(
        rabbit_server_details, config.RABBITMQ_PUBLISH_RETRY_DELAY, config.RABBITMQ_PUBLISH_RETRIES
    )
