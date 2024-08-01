import logging
from fastavro.validation import ValidationError
from typing import Any, Dict, List, Optional, Type

from lab_share_lib.config_readers import get_redpanda_schema_registry, get_basic_publisher
from lab_share_lib.constants import (
    RABBITMQ_HEADER_VALUE_ENCODER_TYPE_DEFAULT,
    RABBITMQ_HEADER_VALUE_ENCODER_TYPE_JSON,
    RABBITMQ_HEADER_VALUE_ENCODER_TYPE_BINARY,
)
from lab_share_lib.exceptions import TransientRabbitError
from lab_share_lib.processing.base_processor import BaseProcessor
from lab_share_lib.processing.rabbit_message import RabbitMessage
from lab_share_lib.rabbit.avro_encoder import (
    AvroEncoderBase,
    AvroEncoderBinaryFile,
    AvroEncoderBinaryMessage,
    AvroEncoderJson,
)
from lab_share_lib.types import Config, RabbitConfig

LOGGER = logging.getLogger(__name__)

ENCODERS: Dict[str, List[Type[AvroEncoderBase]]] = {
    RABBITMQ_HEADER_VALUE_ENCODER_TYPE_BINARY: [AvroEncoderBinaryMessage, AvroEncoderBinaryFile],
    RABBITMQ_HEADER_VALUE_ENCODER_TYPE_JSON: [AvroEncoderJson],
    RABBITMQ_HEADER_VALUE_ENCODER_TYPE_DEFAULT: [AvroEncoderJson],
}


class RabbitMessageProcessor:
    def __init__(self, rabbit_config: RabbitConfig, app_config: Config):
        self._rabbit_config = rabbit_config
        self._app_config = app_config

        self._schema_registry = get_redpanda_schema_registry(app_config)
        self._basic_publisher = get_basic_publisher(rabbit_config.publisher_details, app_config)

        self.__processors: Optional[Dict[str, Any]] = None

    @property
    def _processors(self) -> Dict[str, BaseProcessor]:
        if self.__processors is None:
            self.__processors = self._get_processors()

        return self.__processors

    def _get_processors(self) -> Dict[str, BaseProcessor]:
        """
        Extracts processors from message_types.
        Example message_types node:
        message_subjects={
                "update-sample": ProcessorSchemaConfig(
                    processor=update_sample_processor,
                    reader_schema_version="1"
                )
        }
        """
        return {
            subject: self._build_processor(processor_schema_config.processor)
            for subject, processor_schema_config in self._rabbit_config.message_subjects.items()
        }

    def _build_processor(self, processor: Type[BaseProcessor]) -> BaseProcessor:
        return processor.instantiate(self._schema_registry, self._basic_publisher, self._app_config)

    def _build_avro_encoders(self, encoder_type: str, subject: str) -> List[AvroEncoderBase]:
        if encoder_type not in ENCODERS.keys():
            raise Exception(f"Encoder type {encoder_type} not recognised")

        return [encoder(self._schema_registry, subject) for encoder in ENCODERS[encoder_type]]

    def process_message(self, headers, body):
        message = RabbitMessage(headers, body)
        subject = message.subject
        try:
            message.reader_schema_version = self._rabbit_config.message_subjects[subject].reader_schema_version
            used_encoder = message.decode(
                self._build_avro_encoders(
                    message.encoder_type,
                    subject,
                )
            )
        except TransientRabbitError as ex:
            LOGGER.error(f"Transient error while processing message: {ex.message}")
            raise  # Cause the consumer to restart and try this message again.
        except Exception as ex:
            LOGGER.error(f"Unrecoverable error while decoding RabbitMQ message: {type(ex)} {str(ex)}")
            return False  # Send the message to dead letters.

        if not message.contains_single_message:
            LOGGER.error("RabbitMQ message received containing multiple AVRO encoded messages.")
            return False  # Send the message to dead letters.

        try:
            used_encoder.validate(message.message, message.writer_schema_version)
        except ValidationError as ex:
            LOGGER.error(f"Decoded message failed schema validation: {ex}")
            return False

        if subject not in self._processors.keys():
            LOGGER.error(
                f"Received message has subject '{subject}'" " but there is no implemented processor for this subject."
            )
            return False  # Send the message to dead letters.

        return self._processors[subject].process(message)
