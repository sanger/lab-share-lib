from lab_share_lib.rabbit.schema_registry import SchemaRegistry
from lab_share_lib.types import RabbitServerDetails
from lab_share_lib.rabbit.basic_publisher import BasicPublisher
import sys
import os
from typing import Tuple
from importlib import import_module
from types import ModuleType


def get_config(settings_module: str = "") -> Tuple[ModuleType, str]:
    """Get the config for the app by importing a module named by an environment variable. This allows easy switching
    between environments and inheriting default config values.

    Arguments:
        settings_module (str, optional): the settings module to load. Defaults to "".

    Returns:
        Tuple[Config, str]: tuple with the config module loaded and available to use via `config.<param>` and the
        settings module used
    """
    try:
        if not settings_module:
            settings_module = os.environ["SETTINGS_MODULE"]

        config_module = import_module(settings_module)

        return config_module, settings_module
    except KeyError as e:
        sys.exit(f"{e} required in environment variables for config.")


def get_redpanda_schema_registry(config: ModuleType) -> SchemaRegistry:
    redpanda_url = config.REDPANDA_BASE_URI
    return SchemaRegistry(redpanda_url)


def get_rabbit_server_details(config: ModuleType, username: str = "", password: str = "") -> RabbitServerDetails:
    return RabbitServerDetails(
        uses_ssl=config.RABBITMQ_SSL,
        host=config.RABBITMQ_HOST,
        port=config.RABBITMQ_PORT,
        username=config.RABBITMQ_USERNAME if not username else username,
        password=config.RABBITMQ_PASSWORD if not password else password,
        vhost=config.RABBITMQ_VHOST,
    )


def get_basic_publisher(config: ModuleType, username: str = "", password: str = "") -> BasicPublisher:
    return BasicPublisher(
        get_rabbit_server_details(config, username, password),
        config.RABBITMQ_PUBLISH_RETRY_DELAY,
        config.RABBITMQ_PUBLISH_RETRIES,
    )
