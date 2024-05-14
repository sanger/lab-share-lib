import logging
from lab_share_lib.constants import (
    LOGGER_NAME_RABBIT_MESSAGES,
    RABBITMQ_HEADER_KEY_ENCODER_TYPE,
    RABBITMQ_HEADER_KEY_SUBJECT,
    RABBITMQ_HEADER_KEY_VERSION,
    RABBITMQ_HEADER_VALUE_ENCODER_TYPE_DEFAULT,
)

LOGGER = logging.getLogger(__name__)
MESSAGE_LOGGER = logging.getLogger(LOGGER_NAME_RABBIT_MESSAGES)


class RabbitMessage:
    def __init__(self, headers, encoded_body):
        self.headers = headers
        self.encoded_body = encoded_body

        self._decoded_list = None

    @property
    def encoder_type(self):
        return self.headers.get(RABBITMQ_HEADER_KEY_ENCODER_TYPE, RABBITMQ_HEADER_VALUE_ENCODER_TYPE_DEFAULT)

    @property
    def subject(self):
        return self.headers[RABBITMQ_HEADER_KEY_SUBJECT]

    @property
    def schema_version(self):
        return self.headers[RABBITMQ_HEADER_KEY_VERSION]

    def decode(self, possible_encoders):
        exceptions = []
        for encoder in possible_encoders:
            try:
                LOGGER.debug(f"Attempting to decode message with encoder class '{type(encoder).__name__}'.")
                self._decoded_list = list(encoder.decode(self.encoded_body, self.schema_version))
                if encoder.encoder_type == "binary":
                    MESSAGE_LOGGER.info(f"Decoded binary message body:\n{self._decoded_list}")
                return
            except ValueError as ex:
                LOGGER.debug(f"Failed to decode message with encoder class '{type(encoder).__name__}': {ex}")
                exceptions.append(ex)

        raise ValueError(f"Failed to decode message with any encoder. Exceptions: {exceptions}")

    @property
    def contains_single_message(self):
        return self._decoded_list is not None and len(self._decoded_list) == 1

    @property
    def message(self):
        if self._decoded_list:
            return self._decoded_list[0]
