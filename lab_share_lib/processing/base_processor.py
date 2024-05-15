from abc import ABC, abstractmethod
from typing import Any

from lab_share_lib.processing.rabbit_message import RabbitMessage
from lab_share_lib.rabbit.basic_publisher import BasicPublisher
from lab_share_lib.rabbit.schema_registry import SchemaRegistry


class BaseProcessor(ABC):
    @staticmethod
    @abstractmethod
    def instantiate(
        schema_registry: SchemaRegistry, basic_publisher: BasicPublisher, config: Any
    ) -> "BaseProcessor": ...

    @abstractmethod
    def process(self, message: RabbitMessage) -> bool: ...
