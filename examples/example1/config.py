import os

from lab_share_lib.config.rabbit_config import RabbitConfig, ProcessorSchemaConfig
from lab_share_lib.config.rabbit_server_details import RabbitServerDetails
from processors import Example1MessageProcessor

LOCALHOST = os.getenv("LOCALHOST", "localhost")

# REDPANDA_BASE_URI defines the URL where the Redpanda service is running
REDPANDA_BASE_URI = f"http://{ LOCALHOST }:8081"

# Define one (or more) Rabbit servers to consume from and publish to.
RABBIT_SERVER_DETAILS = RabbitServerDetails(
    uses_ssl=False,  # Whether to use SSL/TLS for the connection
    host=LOCALHOST,  # The hostname of the RabbitMQ server
    port=5672,  # The port number of the RabbitMQ server
    username="admin",  # The username to authenticate on RabbitMQ with
    password="development",  # The password to authenticate on RabbitMQ with
    vhost="test",  # The virtual host to connect to on RabbitMQ
)

RABBITMQ_SERVERS = [
    RabbitConfig(
        consumer_details=RABBIT_SERVER_DETAILS,  # The details of the RabbitMQ server to consume from
        consumed_queue="test.crud-operations",  # The name of the queue to consume messages from
        publisher_details=RABBIT_SERVER_DETAILS,  # The details of the server to create a basic publisher
        # Hash that maps each subject name with a processor class that will be instantiated when
        # we consume a message using that subject name (specified in header from rabbitmq: 'subject')
        message_subjects={
            "example_1_message": ProcessorSchemaConfig(processor=Example1MessageProcessor, reader_schema_version="1")
        },
    ),
]

# Path to the CA certificates file. Required if SSL is active
# and the CA is not defined in the default path:
#
# REQUESTS_CA_BUNDLE="/etc/ssl/certs/ca-certificates.crt"

# RABBITMQ_PUBLISH_RETRY_DELAY is the number of seconds we will wait in between any publish/consume
# connection to Rabbitmq
RABBITMQ_PUBLISH_RETRY_DELAY = 5

# RABBITMQ_PUBLISH_RETRIES is the number of retries we will perform
RABBITMQ_PUBLISH_RETRIES = 36
