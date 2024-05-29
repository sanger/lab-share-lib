from lab_share_lib.config_readers import get_config
from lab_share_lib.processing.rabbit_message_processor import RabbitMessageProcessor
from lab_share_lib.rabbit.background_consumer import BackgroundConsumer
from lab_share_lib.types import RabbitConfig


class RabbitStack:
    def __init__(self, settings_module=""):
        self._config, _ = get_config(settings_module)

    @property
    def _background_consumers(self):
        if not self.__background_consumers:

            def create_consumer(rabbit_config: RabbitConfig) -> BackgroundConsumer:
                message_processor = RabbitMessageProcessor(rabbit_config, self._config)

                return BackgroundConsumer(
                    rabbit_config.consumer_details, rabbit_config.consumed_queue, message_processor.process_message
                )

            self.__background_consumers = [
                create_consumer(rabbit_config) for rabbit_config in self._config.RABBITMQ_SERVERS
            ]

        return self.__background_consumers

    @property
    def is_healthy(self):
        return all([consumer.is_healthy for consumer in self._background_consumers])

    def bring_stack_up(self):
        for consumer in self._background_consumers:
            if consumer.is_healthy:
                continue

            consumer.start()
