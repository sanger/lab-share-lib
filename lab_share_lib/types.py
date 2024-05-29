from types import ModuleType
from typing import List

from lab_share_lib.config.rabbit_config import RabbitConfig


class Config(ModuleType):
    """ModuleType class for the app config."""

    # RabbitMQ
    RABBITMQ_SERVERS: List[RabbitConfig]
    RABBITMQ_PUBLISH_RETRY_DELAY: int
    RABBITMQ_PUBLISH_RETRIES: int

    # RedPanda
    REDPANDA_BASE_URI: str
