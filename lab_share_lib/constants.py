from typing import Final, Literal

RABBITMQ_HEADER_KEY_SUBJECT: Final[str] = "subject"
RABBITMQ_HEADER_KEY_VERSION: Final[str] = "version"
RABBITMQ_HEADER_KEY_ENCODER_TYPE: Final[str] = "encoder_type"

EncoderType = Literal["binary", "json"]
ENCODER_TYPE_BINARY: Final[EncoderType] = "binary"
ENCODER_TYPE_JSON: Final[EncoderType] = "json"

RABBITMQ_HEADER_VALUE_ENCODER_TYPE_BINARY: Final[str] = ENCODER_TYPE_BINARY
RABBITMQ_HEADER_VALUE_ENCODER_TYPE_JSON: Final[str] = ENCODER_TYPE_JSON
RABBITMQ_HEADER_VALUE_ENCODER_TYPE_DEFAULT: Final[str] = "default"

###
# Logger names
###
LOGGER_NAME_RABBIT_MESSAGES: Final[str] = "rabbit_messages"

AVRO_BINARY_COMPRESSION_CODEC_NULL = "null"
AVRO_BINARY_COMPRESSION_CODEC_DEFLATE = "deflate"
AVRO_BINARY_COMPRESSION_CODEC_SNAPPY = "snappy"
AVRO_BINARY_COMPRESSION_CODEC_DEFAULT = AVRO_BINARY_COMPRESSION_CODEC_NULL

class RabbitMQConfigKeys:
    HOST: Final[str] = "host"
    SSL: Final[str] = "ssl"
    PORT: Final[str] = "port"
    USERNAME: Final[str] = "username"
    PASSWORD: Final[str] = "password"
    VHOST: Final[str] = "vhost"
    CONSUMED_QUEUE: Final[str] = "consumed_queue"
