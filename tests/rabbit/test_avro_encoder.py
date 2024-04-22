from unittest.mock import ANY, MagicMock, Mock, patch

import pytest

from lab_share_lib.rabbit.avro_encoder import AvroEncoder, AvroEncoderBinary
from lab_share_lib.rabbit.schema_registry import RESPONSE_KEY_SCHEMA, RESPONSE_KEY_VERSION

SUBJECT = "create-plate-map"
SCHEMA_RESPONSE = {RESPONSE_KEY_SCHEMA: '{ "name": "sampleName", "type": "string" }', RESPONSE_KEY_VERSION: 7}
SCHEMA_OBJECT = {"name": "sampleName", "type": "string"}
MESSAGE_BODY = "The written message."


@pytest.fixture
def binary_message():
    f = open("tests/data/test1.avro.dat", "rb")
    data = f.read()
    f.close()

    yield data


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
def subject(schema_registry):
    return AvroEncoder(schema_registry, SUBJECT)


@pytest.fixture
def subject_binary(schema_registry):
    return AvroEncoderBinary(schema_registry, SUBJECT)


def test_constructor_stores_passed_values(subject, schema_registry):
    assert subject._schema_registry == schema_registry
    assert subject._subject == SUBJECT


@pytest.mark.parametrize("schema_version", [None, "5"])
def test_schema_response_calls_the_schema_registry(subject, schema_registry, schema_version):
    response = subject._schema_response(schema_version)

    if schema_version is None:
        schema_registry.get_schema.assert_called_once_with(SUBJECT)
    else:
        schema_registry.get_schema.assert_called_once_with(SUBJECT, schema_version)

    assert response == SCHEMA_RESPONSE


def test_schema_parses_the_returned_schema(subject, fastavro):
    avro_schema = Mock()
    fastavro.parse_schema.return_value = avro_schema

    parsed_schema = subject._schema(SCHEMA_RESPONSE)

    fastavro.parse_schema.assert_called_once_with(SCHEMA_OBJECT)
    assert parsed_schema == avro_schema


def test_schema_version_extracts_the_version(subject):
    assert subject._schema_version(SCHEMA_RESPONSE) == 7


@pytest.mark.parametrize("schema_version", [None, "5"])
def test_encode_encodes_the_message(subject, fastavro, schema_version):
    records = [{"key": "value"}]

    def json_writer(string_writer, schema, record_list):
        assert schema == fastavro.parse_schema.return_value
        assert record_list == records
        string_writer.write(MESSAGE_BODY)

    fastavro.json_writer.side_effect = json_writer

    result = subject.encode(records, schema_version)

    assert result.body == MESSAGE_BODY.encode()
    assert result.version == "7"


@pytest.mark.parametrize("schema_version", ["5", "42"])
def test_decode_decodes_the_message(subject, fastavro, schema_version):
    fastavro.json_reader.return_value = SCHEMA_OBJECT

    result = subject.decode(MESSAGE_BODY.encode(), schema_version)

    fastavro.json_reader.assert_called_once_with(ANY, fastavro.parse_schema.return_value)
    string_reader = fastavro.json_reader.call_args.args[0]
    assert string_reader.read() == MESSAGE_BODY

    assert result == SCHEMA_OBJECT


@pytest.mark.parametrize("schema_version", ["5", "42"])
def test_encode_binary_encodes_the_message(subject_binary, schema_version):
    records = [MESSAGE_BODY]

    message = subject_binary.encode(records, schema_version)

    assert message.body != records
    assert message.version == "7"


@pytest.mark.parametrize("schema_version", ["5", "42"])
def test_decode_binary_decodes_the_message(subject_binary, schema_version, binary_message):
    records = [MESSAGE_BODY]

    result = subject_binary.decode(binary_message, schema_version)

    assert list(result) == records


@pytest.mark.parametrize("schema_version", ["5", "42"])
def test_json_both_encode_and_decode_actions_work_together(subject, schema_version):
    records = [MESSAGE_BODY]

    message = subject.encode(records, schema_version)
    result = subject.decode(message.body, schema_version)

    assert list(result) == records


@pytest.mark.parametrize("schema_version", ["5", "42"])
def test_binary_both_encode_and_decode_actions_work_together(subject_binary, schema_version):
    records = [MESSAGE_BODY]

    message = subject_binary.encode(records, schema_version)
    result = subject_binary.decode(message.body, schema_version)

    assert list(result) == records
