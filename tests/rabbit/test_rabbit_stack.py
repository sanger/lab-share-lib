from unittest.mock import MagicMock, call, patch
import pytest

from lab_share_lib.rabbit.rabbit_stack import RabbitStack


@pytest.fixture(autouse=True)
def get_config(config):
    with patch("lab_share_lib.rabbit.rabbit_stack.get_config", return_value=(config, "test")) as get_config:
        yield get_config


@pytest.fixture(autouse=True)
def rabbit_message_processor_class():
    with patch("lab_share_lib.rabbit.rabbit_stack.RabbitMessageProcessor") as rabbit_message_processor:
        yield rabbit_message_processor


@pytest.fixture
def background_consumer_a():
    consumer = MagicMock()
    return consumer


@pytest.fixture
def background_consumer_b():
    consumer = MagicMock()
    return consumer


@pytest.fixture(autouse=True)
def background_consumer_class(background_consumer_a, background_consumer_b):
    with patch(
        "lab_share_lib.rabbit.rabbit_stack.BackgroundConsumer",
        side_effect=[background_consumer_a, background_consumer_b],
    ) as background_consumer:
        yield background_consumer


@pytest.fixture
def subject():
    return RabbitStack()


class TestRabbitStack:
    def test_init_get_and_stores_default_config(self, get_config, config):
        stack = RabbitStack()
        get_config.assert_called_once_with("")
        assert stack._config == config

    def test_init_gets_and_stores_specified_config(self, get_config, config):
        stack = RabbitStack("settings_module_name")
        get_config.assert_called_once_with("settings_module_name")
        assert stack._config == config

    def test_background_consumers_property_returns_2_consumers(
        self, subject, background_consumer_a, background_consumer_b
    ):
        assert subject._background_consumers == [background_consumer_a, background_consumer_b]

    def test_background_consumers_correctly_configured(
        self, subject, config, background_consumer_class, rabbit_message_processor_class
    ):
        subject._background_consumers

        background_consumer_class.assert_has_calls(
            [
                call(
                    config.RABBITMQ_SERVERS[0].consumer_details,
                    config.RABBITMQ_SERVERS[0].consumed_queue,
                    rabbit_message_processor_class.return_value.process_message,
                ),
                call(
                    config.RABBITMQ_SERVERS[1].consumer_details,
                    config.RABBITMQ_SERVERS[1].consumed_queue,
                    rabbit_message_processor_class.return_value.process_message,
                ),
            ]
        )

    def test_is_healthy_returns_true_when_all_consumers_are_healthy(
        self, subject, background_consumer_a, background_consumer_b
    ):
        background_consumer_a.is_healthy = True
        background_consumer_b.is_healthy = True

        assert subject.is_healthy is True

    @pytest.mark.parametrize("is_healthy", [(True, False), (False, True), (False, False)])
    def test_is_healthy_returns_false_when_any_consumer_is_not_healthy(
        self, subject, is_healthy, background_consumer_a, background_consumer_b
    ):
        background_consumer_a.is_healthy = is_healthy[0]
        background_consumer_b.is_healthy = is_healthy[1]

        assert subject.is_healthy is False

    @pytest.mark.parametrize("is_healthy", [(True, True), (True, False), (False, True), (False, False)])
    def test_bring_stack_up_starts_unhealthy_consumers(
        self, subject, is_healthy, background_consumer_a, background_consumer_b
    ):
        background_consumer_a.is_healthy = is_healthy[0]
        background_consumer_b.is_healthy = is_healthy[1]

        subject.bring_stack_up()

        if is_healthy[0]:
            background_consumer_a.start.assert_not_called()
        else:
            background_consumer_a.start.assert_called_once()

        if is_healthy[1]:
            background_consumer_b.start.assert_not_called()
        else:
            background_consumer_b.start.assert_called_once()
