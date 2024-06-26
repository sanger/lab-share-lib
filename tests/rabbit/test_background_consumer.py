from unittest.mock import Mock, patch

import pytest

from lab_share_lib.rabbit.background_consumer import BackgroundConsumer
from lab_share_lib.config.rabbit_server_details import RabbitServerDetails

DEFAULT_SERVER_DETAILS = RabbitServerDetails(
    uses_ssl=False, host="host", port=5672, username="username", password="password", vhost="vhost"
)


@pytest.fixture
def subject():
    return BackgroundConsumer(DEFAULT_SERVER_DETAILS, "queue", Mock())


def test_init_sets_the_correct_name(subject):
    assert subject.name == "BackgroundConsumer"


def test_init_sets_daemon_thread_true(subject):
    assert subject.daemon is True


@pytest.mark.parametrize("uses_ssl", [True, False])
@pytest.mark.parametrize("host", ["", "host"])
@pytest.mark.parametrize("port", [8080, 5672])
@pytest.mark.parametrize("username", ["", "username"])
@pytest.mark.parametrize("password", ["", "password"])
@pytest.mark.parametrize("vhost", ["", "vhost"])
@pytest.mark.parametrize("queue", ["", "queue"])
def test_consumer_is_passed_correct_parameters(uses_ssl, host, port, username, password, vhost, queue):
    server_details = RabbitServerDetails(
        uses_ssl=uses_ssl, host=host, port=port, username=username, password=password, vhost=vhost
    )
    process_message = Mock()
    subject = BackgroundConsumer(server_details, queue, process_message)

    with patch(
        "lab_share_lib.rabbit.background_consumer.AsyncConsumer.__init__", return_value=None
    ) as async_consumer_init:
        # Initiate creation of the AsyncConsumer
        subject._consumer

    async_consumer_init.assert_called_once_with(server_details, queue, process_message)


def test_run_starts_consumer_and_stops_on_keyboard_interrupt(subject):
    with patch("lab_share_lib.rabbit.background_consumer.AsyncConsumer") as consumer:
        consumer.return_value.run.side_effect = KeyboardInterrupt()
        subject.run()

    consumer.return_value.run.assert_called_once()
    consumer.return_value.stop.assert_called_once()


def test_maybe_reconnect_sleeps_longer_each_time(subject):
    with patch("lab_share_lib.rabbit.background_consumer.time.sleep") as sleep_func:
        with patch("lab_share_lib.rabbit.background_consumer.AsyncConsumer") as consumer:
            consumer.return_value.should_reconnect = True
            consumer.return_value.had_transient_error = False
            consumer.return_value.was_consuming = False

            subject._maybe_reconnect()
            sleep_func.assert_called_with(1)
            subject._maybe_reconnect()
            sleep_func.assert_called_with(2)
            subject._maybe_reconnect()
            sleep_func.assert_called_with(3)

            subject._reconnect_delay = 28
            subject._maybe_reconnect()
            sleep_func.assert_called_with(29)
            subject._maybe_reconnect()
            sleep_func.assert_called_with(30)
            subject._maybe_reconnect()  # Maximum delay is 30 seconds
            sleep_func.assert_called_with(30)

            assert consumer.return_value.stop.call_count == 6


def test_maybe_reconnect_sleeps_zero_seconds_if_consumer_was_consuming(subject):
    with patch("lab_share_lib.rabbit.background_consumer.time.sleep") as sleep_func:
        with patch("lab_share_lib.rabbit.background_consumer.AsyncConsumer") as consumer:
            consumer.return_value.should_reconnect = True
            consumer.return_value.had_transient_error = False
            consumer.return_value.was_consuming = True

            for _ in range(5):
                subject._maybe_reconnect()
                sleep_func.assert_called_with(0)

            assert consumer.return_value.stop.call_count == 5


def test_maybe_reconnect_sleeps_30_seconds_if_consumer_had_transient_error(subject):
    with patch("lab_share_lib.rabbit.background_consumer.time.sleep") as sleep_func:
        with patch("lab_share_lib.rabbit.background_consumer.AsyncConsumer") as consumer:
            consumer.return_value.should_reconnect = True
            consumer.return_value.had_transient_error = True

            for _ in range(5):
                subject._maybe_reconnect()
                sleep_func.assert_called_with(30)

            assert consumer.return_value.stop.call_count == 5
