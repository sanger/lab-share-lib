import json
from unittest.mock import ANY, MagicMock, Mock, patch

import pytest

from lab_share_lib.rabbit.avro_encoder import (
    AvroEncoder,
    AvroEncoderJson,
    AvroEncoderBinary,
    AvroEncoderBinaryFile,
    AvroEncoderBinaryMessage,
)
from lab_share_lib.rabbit.schema_registry import RESPONSE_KEY_SCHEMA, RESPONSE_KEY_VERSION

SUBJECT = "create-plate-map"
SCHEMA_DICT = {"name": "sampleName", "type": "string"}
SCHEMA_RESPONSE = {RESPONSE_KEY_SCHEMA: json.dumps(SCHEMA_DICT), RESPONSE_KEY_VERSION: 7}
MESSAGE_BODY = "The written message."


@pytest.fixture
def logger():
    with patch("lab_share_lib.rabbit.avro_encoder.LOGGER") as logger:
        yield logger


@pytest.fixture
def binary_message():
    with open("tests/data/binary_message.avro", "rb") as f:
        yield f.read()


@pytest.fixture
def schema_registry():
    schema_registry = MagicMock()
    schema_registry.get_schema.return_value = SCHEMA_RESPONSE

    yield schema_registry


@pytest.fixture
def fastavro():
    with patch("lab_share_lib.rabbit.avro_encoder.fastavro") as fastavro:
        yield fastavro


@pytest.fixture
def json_subject(schema_registry):
    return AvroEncoderJson(schema_registry, SUBJECT)


@pytest.fixture
def binary_file_subject(schema_registry):
    return AvroEncoderBinaryFile(schema_registry, SUBJECT)


@pytest.fixture
def binary_message_subject(schema_registry):
    return AvroEncoderBinaryMessage(schema_registry, SUBJECT)


ENCODER_NAMES = [
    "json_subject",
    "binary_file_subject",
    "binary_message_subject",
]


class TestCommonAvroEncoderFunctionality:
    @pytest.mark.parametrize("encoder_name", ENCODER_NAMES)
    def test_constructor_stores_passed_values(self, encoder_name, schema_registry, request):
        subject = request.getfixturevalue(encoder_name)
        assert subject._schema_registry == schema_registry
        assert subject._subject == SUBJECT

    @pytest.mark.parametrize("encoder_name", ENCODER_NAMES)
    @pytest.mark.parametrize("schema_version", [None, "5"])
    def test_schema_response_calls_the_schema_registry(self, encoder_name, schema_registry, schema_version, request):
        subject = request.getfixturevalue(encoder_name)
        response = subject._schema_response(schema_version)

        if schema_version is None:
            schema_registry.get_schema.assert_called_once_with(SUBJECT)
        else:
            schema_registry.get_schema.assert_called_once_with(SUBJECT, schema_version)

        assert response == SCHEMA_RESPONSE

    @pytest.mark.parametrize("encoder_name", ENCODER_NAMES)
    def test_schema_parses_the_returned_schema(self, encoder_name, fastavro, request):
        subject = request.getfixturevalue(encoder_name)
        avro_schema = Mock()
        fastavro.parse_schema.return_value = avro_schema

        parsed_schema = subject._schema(SCHEMA_RESPONSE)

        fastavro.parse_schema.assert_called_once_with(SCHEMA_DICT)
        assert parsed_schema == avro_schema

    @pytest.mark.parametrize("encoder_name", ENCODER_NAMES)
    def test_schema_version_extracts_the_version(self, encoder_name, request):
        subject = request.getfixturevalue(encoder_name)
        assert subject._schema_version(SCHEMA_RESPONSE) == 7

    @pytest.mark.parametrize("encoder_name", ENCODER_NAMES)
    def test_validate_calls_fastavro_validate(self, encoder_name, fastavro, request):
        subject = request.getfixturevalue(encoder_name)

        with patch("lab_share_lib.rabbit.avro_encoder.validate") as validate:
            data_obj = {"key": "value"}
            subject.validate(data_obj, "5")

        validate.assert_called_once_with(data_obj, fastavro.parse_schema.return_value)


class TestAvroEncoderJson:
    def test_encoder_type_returns_json(self, json_subject):
        assert json_subject.encoder_type == "json"

    @pytest.mark.parametrize("schema_version", [None, "5"])
    def test_encode_encodes_the_message(self, json_subject, fastavro, schema_version):
        records = [{"key": "value"}]

        def json_writer(string_writer, schema, record_list):
            assert schema == fastavro.parse_schema.return_value
            assert record_list == records
            string_writer.write(MESSAGE_BODY)

        fastavro.json_writer.side_effect = json_writer

        result = json_subject.encode(records, schema_version)

        assert result.body == MESSAGE_BODY.encode()
        assert result.version == "7"

    @pytest.mark.parametrize("schema_version", ["5", "42"])
    def test_decode_decodes_the_message(self, json_subject, fastavro, schema_version):
        fastavro.json_reader.return_value = SCHEMA_DICT

        result = json_subject.decode(MESSAGE_BODY.encode(), schema_version, "1")

        fastavro.json_reader.assert_called_once_with(ANY, fastavro.parse_schema.return_value)
        string_reader = fastavro.json_reader.call_args.args[0]
        assert string_reader.read() == MESSAGE_BODY

        assert result == SCHEMA_DICT

    @pytest.mark.parametrize("schema_version", ["5", "42"])
    def test_both_encode_and_decode_actions_work_together(self, json_subject, schema_version):
        records = [MESSAGE_BODY]

        message = json_subject.encode(records, schema_version)
        result = json_subject.decode(message.body, schema_version, "1")

        assert list(result) == records


class TestAvroEncoderBinaryFile:
    @pytest.fixture
    def file(self):
        with open("tests/data/binary_file.avro", "rb") as f:
            yield f.read()

    def test_encoder_type_returns_binary(self, binary_file_subject):
        assert binary_file_subject.encoder_type == "binary"

    @pytest.mark.parametrize("schema_version", ["5", "42"])
    def test_encode_encodes_the_message(self, binary_file_subject, schema_version):
        records = [MESSAGE_BODY]

        message = binary_file_subject.encode(records, schema_version)

        # The binary file includes a random sequence as a delimiter. Therefore we can't easily test the contents.
        # Another test checks we can decode the message we created.
        assert message.body != records
        assert message.version == "7"

    @pytest.mark.parametrize("schema_version", ["5", "42"])
    def test_decode_decodes_the_message(self, binary_file_subject, schema_version, file):
        records = [MESSAGE_BODY]

        result = binary_file_subject.decode(file, schema_version, "1")

        assert list(result) == records

    @pytest.mark.parametrize("schema_version", ["5", "42"])
    def test_both_encode_and_decode_actions_work_together(self, binary_file_subject, schema_version):
        records = [MESSAGE_BODY]

        message = binary_file_subject.encode(records, schema_version)
        result = binary_file_subject.decode(message.body, schema_version, "1")

        assert list(result) == records


class TestAvroEncoderBinaryMessage:
    @pytest.fixture
    def message(self):
        with open("tests/data/binary_message.avro", "rb") as f:
            yield f.read()

    def test_encoder_type_returns_binary(self, binary_message_subject):
        assert binary_message_subject.encoder_type == "binary"

    @pytest.mark.parametrize("schema_version", ["5", "42"])
    def test_encode_encodes_the_message(self, binary_message_subject, schema_version, message):
        record = MESSAGE_BODY

        result = binary_message_subject.encode([record], schema_version)

        assert result.body == message
        assert result.version == "7"

    @pytest.mark.parametrize("schema_version", ["5", "42"])
    def test_encode_single_object_encodes_the_message(self, binary_message_subject, schema_version, message):
        record = MESSAGE_BODY

        result = binary_message_subject.encode_single_object(record, schema_version)

        assert result.body == message
        assert result.version == "7"

    @pytest.mark.parametrize("schema_version", ["5", "42"])
    def test_decode_decodes_the_message(self, binary_message_subject, schema_version, message):
        records = [MESSAGE_BODY]

        result = binary_message_subject.decode(message, schema_version, "1")

        assert result == records

    @pytest.mark.parametrize("schema_version", ["5", "42"])
    def test_both_encode_and_decode_actions_work_together(self, binary_message_subject, schema_version):
        records = [MESSAGE_BODY]

        message = binary_message_subject.encode(records, schema_version)
        result = binary_message_subject.decode(message.body, schema_version, "1")

        assert result == records

    @pytest.mark.parametrize("schema_version", ["5", "42"])
    def test_both_encode_single_object_and_decode_actions_work_together(self, binary_message_subject, schema_version):
        records = [MESSAGE_BODY]

        message = binary_message_subject.encode_single_object(records[0], schema_version)
        result = binary_message_subject.decode(message.body, schema_version, "1")

        assert result == records


class TestDeprecatedAvroEncoderClasses:
    def test_avro_encoder_is_an_instance_of_avro_encoder_json(self, schema_registry):
        subject = AvroEncoder(schema_registry, SUBJECT)
        assert isinstance(subject, AvroEncoderJson)

    def test_avro_encoder_deprecation(self, schema_registry, logger):
        AvroEncoder(schema_registry, SUBJECT)
        assert logger.warning.called
        assert logger.warning.call_args.args[0].startswith("AvroEncoder is deprecated")

    def test_avro_encoder_binary_is_an_instance_of_avro_encoder_binary_file(self, schema_registry):
        subject = AvroEncoderBinary(schema_registry, SUBJECT)
        assert isinstance(subject, AvroEncoderBinaryFile)

    def test_avro_encoder_binary_deprecation(self, schema_registry, logger):
        AvroEncoderBinary(schema_registry, SUBJECT)
        assert logger.warning.called
        assert logger.warning.call_args.args[0].startswith("AvroEncoderBinary is deprecated")
