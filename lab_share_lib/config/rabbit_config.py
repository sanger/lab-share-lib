from dataclasses import dataclass
from typing import Dict, Type

from lab_share_lib.config.rabbit_server_details import RabbitServerDetails
from lab_share_lib.processing.base_processor import BaseProcessor


@dataclass
class RabbitConfig:
    consumer_details: RabbitServerDetails
    consumed_queue: str
    processors: Dict[str, Type[BaseProcessor]]
    publisher_details: RabbitServerDetails
