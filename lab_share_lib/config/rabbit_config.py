from dataclasses import dataclass
from typing import Dict, Type, Any

from lab_share_lib.config.rabbit_server_details import RabbitServerDetails
from lab_share_lib.processing.base_processor import BaseProcessor


@dataclass
class RabbitConfig:
    consumer_details: RabbitServerDetails
    consumed_queue: str
    processors: Dict[str, Type[BaseProcessor]]
    message_subjects: Dict[str, Dict[str, Any]]
    publisher_details: RabbitServerDetails
