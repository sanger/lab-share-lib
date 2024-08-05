import logging
import os
import ssl
import time

from pika import BasicProperties, BlockingConnection, ConnectionParameters, PlainCredentials, SSLOptions
from pika.exceptions import UnroutableError
from pika.spec import PERSISTENT_DELIVERY_MODE
from lab_share_lib.processing.rabbit_message import RabbitMessage


from lab_share_lib.constants import (
    LOGGER_NAME_RABBIT_MESSAGES,
    RABBITMQ_HEADER_KEY_ENCODER_TYPE,
    RABBITMQ_HEADER_KEY_SUBJECT,
    RABBITMQ_HEADER_KEY_VERSION,
    RABBITMQ_HEADER_VALUE_ENCODER_TYPE_DEFAULT,
)
from lab_share_lib.config.rabbit_server_details import RabbitServerDetails

LOGGER = logging.getLogger(__name__)
MESSAGE_LOGGER = logging.getLogger(LOGGER_NAME_RABBIT_MESSAGES)


class BasicPublisher:
    def __init__(
        self,
        server_details: RabbitServerDetails,
        publish_retry_delay: int,
        publish_max_retries: int,
        verify_cert: bool = True,
    ):
        self._publish_retry_delay = publish_retry_delay
        self._publish_max_retries = publish_max_retries
        credentials = PlainCredentials(server_details.username, server_details.password)
        self._connection_params = ConnectionParameters(
            host=server_details.host,
            port=server_details.port,
            virtual_host=server_details.vhost,
            credentials=credentials,
        )

        if server_details.uses_ssl:
            cafile = os.getenv("REQUESTS_CA_BUNDLE")
            ssl_context = ssl.create_default_context(cafile=cafile)
            self.configure_verify_cert(ssl_context, verify_cert=verify_cert)
            self._connection_params.ssl_options = SSLOptions(ssl_context)

    def configure_verify_cert(self, ssl_context: ssl.SSLContext, verify_cert: bool = True) -> None:
        verify_mode = ssl.CERT_REQUIRED if verify_cert else ssl.CERT_NONE
        ssl_context.check_hostname = verify_cert
        ssl_context.verify_mode = verify_mode

    def publish_rabbit_message(self, message: RabbitMessage, exchange: str, routing_key: str) -> None:
        self.publish_message(
            exchange=exchange,
            routing_key=routing_key,
            body=message.encoded_body,
            subject=message.subject,
            schema_version=message.writer_schema_version,
            encoder_type=message.encoder_type,
        )

    def publish_message(
        self,
        exchange,
        routing_key,
        body,
        subject,
        schema_version,
        encoder_type=RABBITMQ_HEADER_VALUE_ENCODER_TYPE_DEFAULT,
    ):
        LOGGER.info(
            f"Publishing message to exchange '{exchange}', routing key '{routing_key}', "
            f"schema subject '{subject}', schema version '{schema_version}'."
        )
        MESSAGE_LOGGER.info(f"Published message body:  {body}")
        properties = BasicProperties(
            delivery_mode=PERSISTENT_DELIVERY_MODE,
            headers={
                RABBITMQ_HEADER_KEY_SUBJECT: subject,
                RABBITMQ_HEADER_KEY_VERSION: schema_version,
                RABBITMQ_HEADER_KEY_ENCODER_TYPE: encoder_type,
            },
        )

        connection = BlockingConnection(self._connection_params)
        channel = connection.channel()
        channel.confirm_delivery()  # Force exceptions when Rabbit cannot deliver the message
        self._do_publish_with_retry(
            lambda: channel.basic_publish(exchange=exchange, routing_key=routing_key, body=body, properties=properties)
        )
        connection.close()

    def _do_publish_with_retry(self, publish_method):
        retry_count = 0

        while True:
            try:
                publish_method()
                break  # When no exception is thrown from publish_method we'll break out of the while loop
            except UnroutableError:
                retry_count += 1

                if retry_count == self._publish_max_retries:
                    LOGGER.error(
                        "Maximum number of retries exceeded for message being published to RabbitMQ. "
                        "Message was NOT PUBLISHED!"
                    )
                    return

                time.sleep(self._publish_retry_delay)

        if retry_count > 0:
            LOGGER.error(f"Publish of message to RabbitMQ required {retry_count} retries.")

        LOGGER.info("The message was published to RabbitMQ successfully.")
