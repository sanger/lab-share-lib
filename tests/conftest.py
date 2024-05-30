import pytest

from lab_share_lib.config.rabbit_config import RabbitConfig
from lab_share_lib.config.rabbit_server_details import RabbitServerDetails
from lab_share_lib.types import Config

RABBIT_SERVER_DETAILS = RabbitServerDetails(
    uses_ssl=False,
    host="testrabbitmq",
    port=1234,
    username="admin",
    password="development",
    vhost="testvhost",
)


class ConfigForTest(Config):
    RABBITMQ_SERVERS = [
        RabbitConfig(
            consumer_details=RABBIT_SERVER_DETAILS,
            consumed_queue="test.crud.queue",
            processors={},
            publisher_details=RABBIT_SERVER_DETAILS,
        )
    ]

    RABBITMQ_PUBLISH_RETRY_DELAY = 5
    RABBITMQ_PUBLISH_RETRIES = 36

    REDPANDA_BASE_URI = "testredpanda"


@pytest.fixture
def rabbit_server_details():
    return RABBIT_SERVER_DETAILS


@pytest.fixture
def config():
    return ConfigForTest("test_settings_module")
