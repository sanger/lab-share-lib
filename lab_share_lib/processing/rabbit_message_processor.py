import logging
from typing import Any, Dict, Optional, cast

from lab_share_lib.exceptions import TransientRabbitError
from lab_share_lib.processing.base_processor import BaseProcessor
from lab_share_lib.processing.rabbit_message import RabbitMessage
from lab_share_lib.rabbit.avro_encoder import AvroEncoderBinary, AvroEncoderJson
from lab_share_lib.config_readers import get_redpanda_schema_registry, get_basic_publisher
from lab_share_lib.constants import (
    RABBITMQ_HEADER_VALUE_ENCODER_TYPE_DEFAULT,
    RABBITMQ_HEADER_VALUE_ENCODER_TYPE_JSON,
    RABBITMQ_HEADER_VALUE_ENCODER_TYPE_BINARY,
)

LOGGER = logging.getLogger(__name__)

ENCODERS = {
    RABBITMQ_HEADER_VALUE_ENCODER_TYPE_BINARY: AvroEncoderBinary,
    RABBITMQ_HEADER_VALUE_ENCODER_TYPE_JSON: AvroEncoderJson,
    RABBITMQ_HEADER_VALUE_ENCODER_TYPE_DEFAULT: AvroEncoderJson,
}


class RabbitMessageProcessor:
    def __init__(self, config):
        self._schema_registry = get_redpanda_schema_registry(config)
        self._basic_publisher = get_basic_publisher(config)
        self._config = config

        self.__processors: Optional[Dict[str, Any]] = None

    @property
    def _processors(self) -> Dict[str, Any]:
        if self.__processors is None:
            self.__processors = {
                subject: self._build_processor_for_subject(subject) for subject in self._config.PROCESSORS.keys()
            }

        return self.__processors

    def _build_processor_for_subject(self, subject: str) -> BaseProcessor:
        processor_instance_builder = self._config.PROCESSORS[subject]
        return cast(
            BaseProcessor, processor_instance_builder(self._schema_registry, self._basic_publisher, self._config)
        )

    def build_avro_encoder(self, encoder_type, subject):
        if encoder_type not in ENCODERS.keys():
            raise Exception(f"Encoder type {encoder_type} not recognised")

        return ENCODERS[encoder_type](self._schema_registry, subject)

    def process_message(self, headers, body):
        message = RabbitMessage(headers, body)
        try:
            message.decode(self.build_avro_encoder(message.encoder_type, message.subject))
        except TransientRabbitError as ex:
            LOGGER.error(f"Transient error while processing message: {ex.message}")
            raise  # Cause the consumer to restart and try this message again.
        except Exception as ex:
            LOGGER.error(f"Unrecoverable error while decoding RabbitMQ message: {type(ex)} {str(ex)}")
            return False  # Send the message to dead letters.

        if not message.contains_single_message:
            LOGGER.error("RabbitMQ message received containing multiple AVRO encoded messages.")
            return False  # Send the message to dead letters.

        if message.subject not in self._processors.keys():
            LOGGER.error(
                f"Received message has subject '{message.subject}'"
                " but there is no implemented processor for this subject."
            )
            return False  # Send the message to dead letters.

        return self._processors[message.subject].process(message)
