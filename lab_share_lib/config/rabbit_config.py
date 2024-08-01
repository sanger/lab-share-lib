from dataclasses import dataclass
from typing import Dict, Type

from lab_share_lib.config.rabbit_server_details import RabbitServerDetails
from lab_share_lib.processing.base_processor import BaseProcessor


@dataclass
class ProcessorSchemaConfig:
    processor: Type[BaseProcessor]
    reader_schema_version: str


@dataclass
class RabbitConfig:
    consumer_details: RabbitServerDetails
    consumed_queue: str
    message_subjects: Dict[str, ProcessorSchemaConfig]
    publisher_details: RabbitServerDetails
