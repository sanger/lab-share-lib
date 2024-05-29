from dataclasses import dataclass
from types import ModuleType
from typing import Dict

from lab_share_lib.processing.base_processor import BaseProcessor


class RabbitServerDetails(ModuleType):
    """ModuleType class for details to connect to a RabbitMQ server."""

    uses_ssl: bool
    host: str
    port: int
    username: str
    password: str
    vhost: str

    def __init__(self, uses_ssl, host, port, username, password, vhost):
        self.uses_ssl = uses_ssl
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.vhost = vhost or "/"


class Config(ModuleType):
    """ModuleType class for the app config."""

    # RabbitMQ
    RABBITMQ_PUBLISH_RETRY_DELAY: int
    RABBITMQ_PUBLISH_RETRIES: int

    # RedPanda
    REDPANDA_BASE_URI: str


@dataclass
class RabbitConfig():
    consumer_details: RabbitServerDetails
    consumed_queue: str
    processors: Dict[str, BaseProcessor]
    publisher_details: RabbitServerDetails | None = None
