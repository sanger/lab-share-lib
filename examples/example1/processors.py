import datetime
from typing import Any

from lab_share_lib.processing.base_processor import BaseProcessor
from lab_share_lib.processing.rabbit_message import RabbitMessage
from lab_share_lib.rabbit.basic_publisher import BasicPublisher
from lab_share_lib.rabbit.schema_registry import SchemaRegistry


class Example1MessageProcessor(BaseProcessor):
    def __init__(self, schema_registry: SchemaRegistry, basic_publisher: BasicPublisher, config: Any):
        """Store the provided arguments for use during processing."""
        self._basic_publisher = basic_publisher
        self._schema_registry = schema_registry
        self._config = config

    @staticmethod
    def instantiate(schema_registry: SchemaRegistry, basic_publisher: BasicPublisher, config: Any) -> BaseProcessor:
        """Instantiate the processor."""
        return Example1MessageProcessor(schema_registry, basic_publisher, config)

    def process(self, message: RabbitMessage) -> bool:
        """Process the message from RabbitMQ. Here you should confirm that the message contains the expected contents
        and perform the expected processing for that message.

        If validation fails, return False to send the message to dead letters and begin consuming the next message in
        the queue.

        If processing fails, either return False if the failure would never resolve in subsequent processing attempts,
        of raise a TransientRabbitError if you want the consumer to disconnect, requeuing the message, then reconnect to
        attempt to process the message again.

        If your processing pipeline needs to publish feedback messages, you can use the schema registry and basic
        publisher to do this.

        Returning True will acknowledge the message and remove it from the queue.
        """

        print(f"Message read from the queue at { datetime.datetime.now() }:")
        print("<<")
        print(message.message)
        print(">>")
        return True
