import json
import logging
from abc import ABC, abstractmethod
from io import StringIO, BytesIO
from typing import Any, List, NamedTuple, Optional

import fastavro

from lab_share_lib.rabbit.schema_registry import RESPONSE_KEY_SCHEMA, RESPONSE_KEY_VERSION
from lab_share_lib.constants import AVRO_BINARY_COMPRESSION_CODEC_DEFAULT

LOGGER = logging.getLogger(__name__)


class EncodedMessage(NamedTuple):
    body: bytes
    version: str


class AvroEncoderBase(ABC):
    def __init__(self, schema_registry, subject):
        self._schema_registry = schema_registry
        self._subject = subject

    @abstractmethod
    def encode(self, records: List, version: Optional[str] = None) -> EncodedMessage: ...

    @abstractmethod
    def decode(self, message: bytes, version: str) -> Any: ...

    def _schema_response(self, version):
        if version is None:
            return self._schema_registry.get_schema(self._subject)
        else:
            return self._schema_registry.get_schema(self._subject, version)

    def _schema(self, schema_response):
        schema_obj = json.loads(schema_response[RESPONSE_KEY_SCHEMA])
        return fastavro.parse_schema(schema_obj)

    def _schema_version(self, schema_response):
        return schema_response[RESPONSE_KEY_VERSION]


class AvroEncoderJson(AvroEncoderBase):
    """An encoder for Avro messages being encoded as JSON. This can be useful for debugging purposes, but shouldn't be
    used in production where performance can be improved via binary encodings.
    """

    def encode(self, records: List, version: Optional[str] = None) -> EncodedMessage:
        LOGGER.debug("Encoding AVRO message.")

        schema_response = self._schema_response(version)
        string_writer = StringIO()
        fastavro.json_writer(string_writer, self._schema(schema_response), records)

        return EncodedMessage(
            body=string_writer.getvalue().encode(), version=str(self._schema_version(schema_response))
        )

    def decode(self, message: bytes, version: str) -> Any:
        LOGGER.debug("Decoding AVRO message.")

        schema_response = self._schema_response(version)
        string_reader = StringIO(message.decode())

        return fastavro.json_reader(string_reader, self._schema(schema_response))


class AvroEncoderBinaryFile(AvroEncoderBase):
    """An encoder for Avro messages that are stored long term in a file. This encoding is not intended for sending
    messages via a message broker where the messages are short lived. The encoding will include the schema in the
    content of the message which inflates the size of the encoded message vastly.
    """

    def __init__(self, schema_registry, subject):
        super().__init__(schema_registry, subject)
        self._compression_codec = AVRO_BINARY_COMPRESSION_CODEC_DEFAULT

    def set_compression_codec(self, compression_codec: str = AVRO_BINARY_COMPRESSION_CODEC_DEFAULT) -> None:
        self._compression_codec = compression_codec

    def encode(self, records: List, version: Optional[str] = None) -> EncodedMessage:
        LOGGER.debug("Encoding AVRO message.")

        schema_response = self._schema_response(version)
        bytes_writer = BytesIO()

        fastavro.writer(bytes_writer, self._schema(schema_response), records, codec=self._compression_codec)

        return EncodedMessage(body=bytes_writer.getvalue(), version=str(self._schema_version(schema_response)))

    def decode(self, message: bytes, version: str) -> Any:
        LOGGER.debug("Decoding AVRO message.")

        schema_response = self._schema_response(version)
        bytes_reader = BytesIO(message)

        return fastavro.reader(bytes_reader, self._schema(schema_response))


class AvroEncoderBinary(AvroEncoderBinaryFile):
    """Included for backwards compatibility. This class is now an alias for AvroEncoderBinaryFile."""

    def __init__(self, schema_registry, subject):
        LOGGER.warn(
            "AvroEncoderBinary is now deprecated. Either use AvroEncoderBinaryFile for the same functionality as "
            "before, or AvroEncoderBinaryMessage if you are not trying to store Avro encodings in a file format."
        )
        super().__init__(schema_registry, subject)


AvroEncoder = AvroEncoderJson
