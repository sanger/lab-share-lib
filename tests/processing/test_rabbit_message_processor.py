from unittest.mock import MagicMock, Mock, patch

import pytest

from fastavro.validation import ValidationError
from logging import ERROR

from lab_share_lib.constants import (
    RABBITMQ_HEADER_KEY_SUBJECT,
    RABBITMQ_HEADER_KEY_VERSION,
)
from lab_share_lib.exceptions import TransientRabbitError
from lab_share_lib.processing.rabbit_message_processor import RabbitMessageProcessor
from lab_share_lib.constants import (
    RABBITMQ_HEADER_VALUE_ENCODER_TYPE_DEFAULT,
    RABBITMQ_HEADER_KEY_ENCODER_TYPE,
    RABBITMQ_HEADER_VALUE_ENCODER_TYPE_JSON,
    RABBITMQ_HEADER_VALUE_ENCODER_TYPE_BINARY,
)
from tests.constants import RABBITMQ_SUBJECT_CREATE_PLATE, RABBITMQ_SUBJECT_UPDATE_SAMPLE

HEADERS = {
    RABBITMQ_HEADER_KEY_SUBJECT: RABBITMQ_SUBJECT_CREATE_PLATE,
    RABBITMQ_HEADER_KEY_VERSION: "3",
}
MESSAGE_BODY = "Body"


@pytest.fixture(autouse=True)
def rabbit_message():
    with patch("lab_share_lib.processing.rabbit_message_processor.RabbitMessage") as rabbit_message:
        rabbit_message.return_value.subject = HEADERS[RABBITMQ_HEADER_KEY_SUBJECT]
        rabbit_message.return_value.encoder_type = RABBITMQ_HEADER_VALUE_ENCODER_TYPE_DEFAULT
        rabbit_message.return_value.reader_schema_version = "1"
        yield rabbit_message


@pytest.fixture
def rabbit_message_json(rabbit_message):
    rabbit_message.return_value.encoder_type = RABBITMQ_HEADER_VALUE_ENCODER_TYPE_JSON
    yield rabbit_message


@pytest.fixture
def rabbit_message_binary(rabbit_message):
    rabbit_message.return_value.encoder_type = RABBITMQ_HEADER_VALUE_ENCODER_TYPE_BINARY
    yield rabbit_message


@pytest.fixture
def build_avro_encoders():
    with patch(
        "lab_share_lib.processing.rabbit_message_processor.RabbitMessageProcessor._build_avro_encoders",
        return_value=[Mock(), Mock()],
    ) as build_avro_encoders:
        yield build_avro_encoders


@pytest.fixture(autouse=True)
def schema_registry():
    with patch("lab_share_lib.processing.rabbit_message_processor.get_redpanda_schema_registry") as schema_registry:
        yield schema_registry.return_value


@pytest.fixture(autouse=True)
def basic_publisher():
    with patch("lab_share_lib.processing.rabbit_message_processor.get_basic_publisher") as basic_publisher:
        yield basic_publisher.return_value


@pytest.fixture
def subject(config):
    return RabbitMessageProcessor(config.RABBITMQ_SERVERS[0], config)


def test_constructor_stored_passed_values(subject, schema_registry, basic_publisher, config):
    assert subject._schema_registry == schema_registry
    assert subject._basic_publisher == basic_publisher
    assert subject._rabbit_config == config.RABBITMQ_SERVERS[0]
    assert subject._app_config == config


def test_processors_are_populated_correctly(subject, create_plate_processor, update_sample_processor):
    assert list(subject._processors.keys()) == [RABBITMQ_SUBJECT_CREATE_PLATE, RABBITMQ_SUBJECT_UPDATE_SAMPLE]
    assert subject._processors[RABBITMQ_SUBJECT_CREATE_PLATE] == create_plate_processor.return_value
    assert subject._processors[RABBITMQ_SUBJECT_UPDATE_SAMPLE] == update_sample_processor.return_value


def test_process_message_decodes_the_message_with_default_encoding(subject, rabbit_message, build_avro_encoders):
    subject.process_message(HEADERS, MESSAGE_BODY)

    rabbit_message.assert_called_once_with(HEADERS, MESSAGE_BODY)

    build_avro_encoders.assert_called_once_with(
        RABBITMQ_HEADER_VALUE_ENCODER_TYPE_DEFAULT, HEADERS[RABBITMQ_HEADER_KEY_SUBJECT]
    )
    rabbit_message.return_value.decode.assert_called_once_with(build_avro_encoders.return_value)


def test_process_message_decodes_the_message_with_json_encoding(subject, rabbit_message_json, build_avro_encoders):
    modified_headers = HEADERS.copy()
    modified_headers.update({RABBITMQ_HEADER_KEY_ENCODER_TYPE: RABBITMQ_HEADER_VALUE_ENCODER_TYPE_JSON})
    subject.process_message(modified_headers, MESSAGE_BODY)

    rabbit_message_json.assert_called_once_with(modified_headers, MESSAGE_BODY)
    build_avro_encoders.assert_called_once_with(
        RABBITMQ_HEADER_VALUE_ENCODER_TYPE_JSON, HEADERS[RABBITMQ_HEADER_KEY_SUBJECT]
    )
    rabbit_message_json.return_value.decode.assert_called_once_with(build_avro_encoders.return_value)


def test_process_message_decodes_the_message_with_binary_encoding(subject, rabbit_message_binary, build_avro_encoders):
    modified_headers = HEADERS.copy()
    modified_headers.update({RABBITMQ_HEADER_KEY_ENCODER_TYPE: RABBITMQ_HEADER_VALUE_ENCODER_TYPE_BINARY})
    subject.process_message(modified_headers, MESSAGE_BODY)

    rabbit_message_binary.assert_called_once_with(modified_headers, MESSAGE_BODY)
    build_avro_encoders.assert_called_once_with(
        RABBITMQ_HEADER_VALUE_ENCODER_TYPE_BINARY, HEADERS[RABBITMQ_HEADER_KEY_SUBJECT]
    )
    rabbit_message_binary.return_value.decode.assert_called_once_with(build_avro_encoders.return_value)


def test_process_message_handles_exception_during_decode(subject, rabbit_message, caplog):
    rabbit_message.return_value.decode.side_effect = KeyError()
    result = subject.process_message(HEADERS, MESSAGE_BODY)

    assert result is False
    assert any("unrecoverable" in log.message.lower() and log.levelno == ERROR for log in caplog.records)


def test_process_message_handles_transient_error_from_schema_registry(subject, rabbit_message, caplog):
    # We have mocked out the decode method.  The AvroEncoder speaks to the schema registry
    # which could raise this error type so we'll just mock it on the decode method.
    error_message = "Schema registry unreachable"
    rabbit_message.return_value.decode.side_effect = TransientRabbitError(error_message)

    with pytest.raises(TransientRabbitError):
        subject.process_message(HEADERS, MESSAGE_BODY)

    assert any("transient" in log.message.lower() and log.levelno == ERROR for log in caplog.records)


def test_process_message_rejects_rabbit_message_with_multiple_messages(subject, rabbit_message, caplog):
    rabbit_message.return_value.contains_single_message = False
    result = subject.process_message(HEADERS, MESSAGE_BODY)

    assert result is False
    assert any("multiple" in log.message.lower() and log.levelno == ERROR for log in caplog.records)


def test_process_message_calls_validate_on_used_encoder(subject, rabbit_message):
    message = rabbit_message.return_value
    encoder = MagicMock()
    message.decode.return_value = encoder

    subject.process_message(HEADERS, MESSAGE_BODY)

    encoder.validate.assert_called_with(message.message, message.writer_schema_version)


def test_process_message_returns_false_when_validate_raises_validation_error(subject, rabbit_message):
    message = rabbit_message.return_value
    encoder = MagicMock()
    message.decode.return_value = encoder
    encoder.validate.side_effect = ValidationError("Test")

    result = subject.process_message(HEADERS, MESSAGE_BODY)

    assert result is False


def test_process_message_logs_error_when_validate_raises_validation_error(subject, rabbit_message, caplog):
    message = rabbit_message.return_value
    encoder = MagicMock()
    message.decode.return_value = encoder
    validation_error = ValidationError("Test")
    encoder.validate.side_effect = validation_error

    subject.process_message(HEADERS, MESSAGE_BODY)

    assert any(str(validation_error) in log.message and log.levelno == ERROR for log in caplog.records)


def test_process_message_rejects_rabbit_message_with_unrecognised_subject(subject, rabbit_message, caplog):
    wrong_subject = "random-subject"
    rabbit_message.return_value.subject = wrong_subject
    result = subject.process_message(HEADERS, MESSAGE_BODY)

    assert result is False
    assert any(wrong_subject in log.message and log.levelno == ERROR for log in caplog.records)


@pytest.mark.parametrize("return_value", [True, False])
def test_process_message_returns_value_returned_by_processor(subject, create_plate_processor, return_value):
    create_plate_processor.return_value.process.return_value = return_value
    result = subject.process_message(HEADERS, MESSAGE_BODY)

    assert result is return_value


def test_process_message_raises_error_generated_by_processor(subject, create_plate_processor):
    raised_error = TransientRabbitError("Test")
    create_plate_processor.return_value.process.side_effect = raised_error

    with pytest.raises(TransientRabbitError) as ex_info:
        subject.process_message(HEADERS, MESSAGE_BODY)

    assert ex_info.value == raised_error
