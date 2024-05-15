import json
import logging
from abc import ABC, abstractmethod
from io import StringIO, BytesIO
from typing import Any, Iterable, List, NamedTuple, Optional

import fastavro

from lab_share_lib.rabbit.schema_registry import RESPONSE_KEY_SCHEMA, RESPONSE_KEY_VERSION
from lab_share_lib.constants import AVRO_BINARY_COMPRESSION_CODEC_DEFAULT, EncoderType

LOGGER = logging.getLogger(__name__)


class EncodedMessage(NamedTuple):
    body: bytes
    version: str


class AvroEncoderBase(ABC):
    def __init__(self, schema_registry, subject):
        self._schema_registry = schema_registry
        self._subject = subject

    @property
    @abstractmethod
    def encoder_type(self) -> EncoderType: ...

    @abstractmethod
    def encode(self, records: List, version: Optional[str] = None) -> EncodedMessage: ...

    @abstractmethod
    def decode(self, message: bytes, version: str) -> Iterable: ...

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

    @property
    def encoder_type(self) -> EncoderType:
        return "json"

    def encode(self, records: List, version: Optional[str] = None) -> EncodedMessage:
        LOGGER.debug("Encoding AVRO message.")

        schema_response = self._schema_response(version)
        string_writer = StringIO()
        fastavro.json_writer(string_writer, self._schema(schema_response), records)

        return EncodedMessage(
            body=string_writer.getvalue().encode(), version=str(self._schema_version(schema_response))
        )

    def decode(self, message: bytes, version: str) -> Iterable:
        LOGGER.debug("Decoding AVRO message.")

        schema_response = self._schema_response(version)
        string_reader = StringIO(message.decode())

        return fastavro.json_reader(string_reader, self._schema(schema_response))


class AvroEncoder(AvroEncoderJson):
    """Included for backwards compatibility. This class is now an alias for AvroEncoderJson."""

    def __init__(self, schema_registry, subject):
        LOGGER.warning(
            "AvroEncoder is deprecated. Please now use AvroEncoderJson for the same functionality or "
            "one of the other encoder types."
        )
        super().__init__(schema_registry, subject)


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

    @property
    def encoder_type(self) -> EncoderType:
        return "binary"

    def encode(self, records: List, version: Optional[str] = None) -> EncodedMessage:
        LOGGER.debug("Encoding AVRO message.")

        schema_response = self._schema_response(version)
        bytes_writer = BytesIO()

        fastavro.writer(bytes_writer, self._schema(schema_response), records, codec=self._compression_codec)

        return EncodedMessage(body=bytes_writer.getvalue(), version=str(self._schema_version(schema_response)))

    def decode(self, message: bytes, version: str) -> Iterable:
        LOGGER.debug("Decoding AVRO message.")

        schema_response = self._schema_response(version)
        bytes_reader = BytesIO(message)

        return fastavro.reader(bytes_reader, self._schema(schema_response))


class AvroEncoderBinaryMessage(AvroEncoderBase):
    """An encoder for single-object Avro messages.
    This sort of encoding reduces the overhead of the file encoding by removing the schema from the content of the
    message. This is suitable for sending and receiving messages via a message broker where the schema is stored in a
    schema registry. The schema used for writing is identified by a 64-bit CRC fingerprint of the schema. Note however,
    the fingerprint may be inconsistent between different Avro implementations, so it cannot be relied upon. Therefore
    it is recommended to indicate the schema subject and version in the message metadata.

    Raises:
        ValueError: If the number of records is not exactly 1 while encoding.
        ValueError: If the message binary does not start with the expected two-byte marker.
    """

    TWO_BYTE_MARKER = b"\xC3\x01"  # Used to identify single-object Avro encoding.

    def __init__(self, schema_registry, subject):
        super().__init__(schema_registry, subject)

    def _schema_fingerprint(self, schema_response):
        canonical_form = fastavro.schema.to_parsing_canonical_form(self._schema(schema_response))
        return fastavro.schema.fingerprint(canonical_form, "CRC-64-AVRO")

    @property
    def encoder_type(self) -> EncoderType:
        return "binary"

    def encode(self, records: List, version: Optional[str] = None) -> EncodedMessage:
        if records is None or len(records) != 1:
            raise ValueError("AvroEncoderBinaryMessage only supports encoding exactly one object at a time.")

        return self.encode_single_object(records[0], version)

    def encode_single_object(self, record: Any, version: Optional[str] = None) -> EncodedMessage:
        LOGGER.debug("Encoding AVRO message.")

        schema_response = self._schema_response(version)

        bytes_writer = BytesIO()
        bytes_writer.write(self.TWO_BYTE_MARKER)
        bytes_writer.write(bytes.fromhex(self._schema_fingerprint(schema_response)))
        fastavro.schemaless_writer(bytes_writer, self._schema(schema_response), record)

        return EncodedMessage(body=bytes_writer.getvalue(), version=str(self._schema_version(schema_response)))

    def decode(self, message: bytes, version: str) -> Iterable:
        LOGGER.debug("Decoding AVRO message.")

        schema_response = self._schema_response(version)
        bytes_reader = BytesIO(message)

        marker = bytes_reader.read(2)
        if marker != self.TWO_BYTE_MARKER:
            raise ValueError("Message does not appear to be a single-object Avro encoding.")

        # Skip the schema fingerprint as our schema registry doesn't support looking up by fingerprint.
        bytes_reader.seek(10)

        # There's something wrong with mypy linting for the number of arguments on this method!
        return [fastavro.schemaless_reader(bytes_reader, self._schema(schema_response))]  # type: ignore[call-arg]


class AvroEncoderBinary(AvroEncoderBinaryFile):
    """Included for backwards compatibility. This class is now an alias for AvroEncoderBinaryFile."""

    def __init__(self, schema_registry, subject):
        LOGGER.warning(
            "AvroEncoderBinary is deprecated. Either use AvroEncoderBinaryFile for the same functionality as "
            "before, or AvroEncoderBinaryMessage if you are not trying to store Avro encodings in a file format."
        )
        super().__init__(schema_registry, subject)
