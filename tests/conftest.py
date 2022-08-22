import pytest


CONFIG = {
    ###
    # RabbitMQ details
    ###
    "RABBITMQ_HOST": "testrabbitmq",
    "RABBITMQ_SSL": False,
    "RABBITMQ_PORT": 1234,
    "RABBITMQ_USERNAME": "admin",
    "RABBITMQ_PASSWORD": "development",
    "RABBITMQ_VHOST": "testvhost",
    "RABBITMQ_CRUD_QUEUE": "test.crud.queue",
    "RABBITMQ_FEEDBACK_EXCHANGE": "test.exchange",
    "RABBITMQ_PUBLISH_RETRY_DELAY": 5,
    "RABBITMQ_PUBLISH_RETRIES": 36,  # 3 minutes of retries
    ###
    # RedPanda details
    ###
    "REDPANDA_BASE_URI": "testredpanda",
    "REDPANDA_API_KEY": "test",
    "PROCESSORS": {},
}


@pytest.fixture
def config():
    return type("Config", (object,), CONFIG)
