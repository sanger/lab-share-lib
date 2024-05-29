from lab_share_lib.rabbit.schema_registry import SchemaRegistry
from lab_share_lib.config.rabbit_server_details import RabbitServerDetails
from lab_share_lib.rabbit.basic_publisher import BasicPublisher
import sys
import os
from typing import Tuple, cast
from importlib import import_module

from lab_share_lib.types import Config


def get_config(settings_module: str = "") -> Tuple[Config, str]:
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

        config_module = cast(Config, import_module(settings_module))

        return config_module, settings_module
    except KeyError as e:
        sys.exit(f"{e} required in environment variables for config.")


def get_redpanda_schema_registry(config: Config) -> SchemaRegistry:
    redpanda_url = config.REDPANDA_BASE_URI
    return SchemaRegistry(redpanda_url)


def get_basic_publisher(server_details: RabbitServerDetails, config: Config) -> BasicPublisher:
    return BasicPublisher(
        server_details,
        config.RABBITMQ_PUBLISH_RETRY_DELAY,
        config.RABBITMQ_PUBLISH_RETRIES,
    )
