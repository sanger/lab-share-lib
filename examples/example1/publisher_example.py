import config
import datetime
from lab_share_lib.rabbit.schema_registry import SchemaRegistry
from lab_share_lib.rabbit.basic_publisher import BasicPublisher
from lab_share_lib.rabbit.avro_encoder import AvroEncoderBinaryMessage
from lab_share_lib.constants import RABBITMQ_HEADER_VALUE_ENCODER_TYPE_BINARY

TIMESTAMP = datetime.datetime.utcnow()
MESSAGE = f"This is the message sent from the publisher at {TIMESTAMP}"
SUBJECT = "example_1_message"
RABBITMQ_ROUTING_KEY = "testing_routing_key.34"

registry = SchemaRegistry(config.REDPANDA_BASE_URI, verify=False)

publisher = BasicPublisher(
    config.RABBIT_SERVER_DETAILS, publish_retry_delay=5, publish_max_retries=36, verify_cert=False
)

encoder = AvroEncoderBinaryMessage(registry, SUBJECT)
# When using a BinaryFileEncoder, you can set the compression codec to "snappy" or "deflate"
# encoder.set_compression_codec("snappy")
encoded_message = encoder.encode([MESSAGE], version="latest")

print(f"Sending message: {MESSAGE}")
publisher.publish_message(
    "test.exchange",
    RABBITMQ_ROUTING_KEY,
    encoded_message.body,
    SUBJECT,
    encoded_message.version,
    RABBITMQ_HEADER_VALUE_ENCODER_TYPE_BINARY,
)
