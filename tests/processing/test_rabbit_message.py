import logging
from unittest.mock import MagicMock, call

import pytest

from lab_share_lib.constants import (
    RABBITMQ_HEADER_KEY_ENCODER_TYPE,
    RABBITMQ_HEADER_VALUE_ENCODER_TYPE_DEFAULT,
    RABBITMQ_HEADER_KEY_SUBJECT,
    RABBITMQ_HEADER_KEY_VERSION,
)
from lab_share_lib.processing.rabbit_message import RabbitMessage

HEADERS = {
    RABBITMQ_HEADER_KEY_SUBJECT: "a-subject",
    RABBITMQ_HEADER_KEY_VERSION: "3",
}

ENCODED_BODY = "Encoded body"
DECODED_LIST = ["Decoded body"]


@pytest.fixture
def subject():
    return RabbitMessage(HEADERS, ENCODED_BODY)


@pytest.fixture
def decoder():
    decoder = MagicMock()
    decoder.decode.return_value = DECODED_LIST

    return decoder


def test_subject_extracts_the_header_correctly(subject):
    assert subject.subject == HEADERS[RABBITMQ_HEADER_KEY_SUBJECT]


def test_schema_version_extracts_the_header_correctly(subject):
    assert subject.schema_version == HEADERS[RABBITMQ_HEADER_KEY_VERSION]


def test_decode_populates_decoded_list(subject, decoder):
    subject.decode([decoder])

    decoder.decode.assert_called_once_with(ENCODED_BODY, HEADERS[RABBITMQ_HEADER_KEY_VERSION])
    assert subject._decoded_list == DECODED_LIST


def test_decode_successfully_decodes_if_second_decoder_works(subject, decoder):
    decoder.decode.side_effect = [ValueError("Invalid 1"), DECODED_LIST]

    subject.decode([decoder, decoder])

    decoder.decode.assert_has_calls([call(ENCODED_BODY, HEADERS[RABBITMQ_HEADER_KEY_VERSION]) for _ in range(2)])
    assert subject._decoded_list == DECODED_LIST


def test_decode_raises_value_error_if_all_decoders_fail(subject, decoder):
    decoder.decode.side_effect = [ValueError("Invalid 1"), ValueError("Invalid 2")]

    with pytest.raises(ValueError, match="Failed to decode message with any encoder.") as ex:
        subject.decode([decoder, decoder])

    assert "Invalid 1" in str(ex.value)
    assert "Invalid 2" in str(ex.value)

def test_decode_does_not_log_json_decoded_body(subject, decoder, caplog):
    caplog.set_level(logging.INFO)
    decoder.encoder_type = "json"
    subject.decode([decoder])

    assert "Decoded binary message body:\n['Decoded body']" not in caplog.text

def test_decode_logs_binary_decoded_body(subject, decoder, caplog):
    caplog.set_level(logging.INFO)
    decoder.encoder_type = "binary"
    subject.decode([decoder])

    assert "Decoded binary message body:\n['Decoded body']" in caplog.text


@pytest.mark.parametrize(
    "decoded_list,expected",
    [
        ([], False),
        (["decoded_1"], True),
        (["decoded_1", "decoded_2"], False),
    ],
)
def test_contains_single_message_gives_correct_response(subject, decoded_list, expected):
    subject._decoded_list = decoded_list
    assert subject.contains_single_message is expected


@pytest.mark.parametrize(
    "decoded_list,expected",
    [
        (["decoded_1"], "decoded_1"),
        # Realistically, you wouldn't be calling `.message` unless `.contains_single_message` returns True.  But anyway!
        (["decoded_1", "decoded_2"], "decoded_1"),
    ],
)
def test_message_returns_first_decoded_list_item(subject, decoded_list, expected):
    subject._decoded_list = decoded_list
    assert subject.message == expected


def test_encoder_type(subject):
    assert subject.encoder_type is RABBITMQ_HEADER_VALUE_ENCODER_TYPE_DEFAULT

    h2 = HEADERS.copy()
    h2[RABBITMQ_HEADER_KEY_ENCODER_TYPE] = "my-encoding"
    m2 = RabbitMessage(h2, ENCODED_BODY)

    assert m2.encoder_type == "my-encoding"
