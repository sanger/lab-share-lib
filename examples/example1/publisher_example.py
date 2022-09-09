import config
import datetime
from lab_share_lib.rabbit.schema_registry import SchemaRegistry
from lab_share_lib.rabbit.basic_publisher import BasicPublisher
from lab_share_lib.rabbit.avro_encoder import AvroEncoderBinary
from lab_share_lib.constants import RABBITMQ_HEADER_VALUE_ENCODER_TYPE_BINARY
from lab_share_lib.types import RabbitServerDetails

TIMESTAMP = datetime.datetime.utcnow()
MESSAGE = f"This is the message sent from the publisher at {TIMESTAMP}"
SUBJECT = "example_1_message"
RABBITMQ_ROUTING_KEY = "testing_routing_key.34"

registry = SchemaRegistry(config.REDPANDA_BASE_URI, config.REDPANDA_API_KEY, verify=False)

rabbitmq_details = RabbitServerDetails(
    uses_ssl=False,
    host=config.RABBITMQ_HOST,
    port=config.RABBITMQ_PORT,
    username=config.RABBITMQ_USERNAME,
    password=config.RABBITMQ_PASSWORD,
    vhost=config.RABBITMQ_VHOST,
)
publisher = BasicPublisher(rabbitmq_details, publish_retry_delay=5, publish_max_retries=36, verify_cert=False)

encoder = AvroEncoderBinary(registry, SUBJECT)
encoder.set_compression_codec("snappy")
encoded_message = encoder.encode([MESSAGE], version="latest")

print(f"Sending message: {MESSAGE}")
publisher.publish_message(
    config.RABBITMQ_EXCHANGE,
    RABBITMQ_ROUTING_KEY,
    encoded_message.body,
    SUBJECT,
    encoded_message.version,
    RABBITMQ_HEADER_VALUE_ENCODER_TYPE_BINARY,
)
