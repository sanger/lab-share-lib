from processors import Example1MessageProcessor
import os

LOCALHOST = os.getenv("LOCALHOST", "localhost")

# REDPANDA_BASE_URI defines the URL where the Redpanda service is running
REDPANDA_BASE_URI = f"http://{ LOCALHOST }:8081"

# REDPANDA_API_KEY defines the secret api key that redpanda will receive
# to authenticate
REDPANDA_API_KEY = "secret-key"

# RABBITMQ_HOST is the hostname of the machine running Rabbitmq
RABBITMQ_HOST = LOCALHOST

# RABBITMQ_PORT is the port number where the Rabbitmq instance is running
RABBITMQ_PORT = "5672"

# RABBITMQ_USERNAME is the username of the rabbitmq user we will use to consume/publish
RABBITMQ_USERNAME = "admin"

# RABBITMQ_PASSWORD is the password of the rabbitmq user we will use to consume/publish
RABBITMQ_PASSWORD = "development"

# RABBITMQ_VHOST is the virtual host in Rabbitmq we will use to connect
RABBITMQ_VHOST = "test"

# RABBITMQ_CRUD_QUEUE is the name of the queue we will consume messages from
RABBITMQ_CRUD_QUEUE = "test.crud-operations"

# RABBITMQ_PUBLISH_RETRY_DELAY is the number of seconds we will wait in between any publish/consume
# connection to Rabbitmq
RABBITMQ_PUBLISH_RETRY_DELAY = 5

# RABBITMQ_PUBLISH_RETRIES is the number of retries we will perform
RABBITMQ_PUBLISH_RETRIES = 36

# Enable (True) if Rabbitmq has been setup with SSL
RABBITMQ_SSL = False

# RABBITMQ_EXCHANGE is the exchange that the publisher will use to publish a message
RABBITMQ_EXCHANGE = "test_exchange"


# Path to the CA certificates file. Required if SSL is active
# and the CA is not defined in the default path:
#
# REQUESTS_CA_BUNDLE="/etc/ssl/certs/ca-certificates.crt"

# Hash that maps each subject name with a processor class that will be instantiated when
# we consume a message using that subject name (specified in header from rabbitmq: 'subject')
PROCESSORS = {"example_1_message": Example1MessageProcessor}
