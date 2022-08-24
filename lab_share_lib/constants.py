from typing import Final

RABBITMQ_HEADER_KEY_SUBJECT: Final[str] = "subject"
RABBITMQ_HEADER_KEY_VERSION: Final[str] = "version"
RABBITMQ_HEADER_KEY_ENCODER_TYPE: Final[str] = "encoder_type"

RABBITMQ_HEADER_VALUE_ENCODER_TYPE_BINARY: Final[str] = "binary"
RABBITMQ_HEADER_VALUE_ENCODER_TYPE_JSON: Final[str] = "json"
RABBITMQ_HEADER_VALUE_ENCODER_TYPE_DEFAULT: Final[str] = "default"


###
# Logger names
###
LOGGER_NAME_RABBIT_MESSAGES: Final[str] = "rabbit_messages"
