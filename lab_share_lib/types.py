from types import ModuleType


class RabbitServerDetails(ModuleType):
    """ModuleType class for details to connect to a RabbitMQ server."""

    uses_ssl: bool
    host: str
    port: int
    username: str
    password: str
    vhost: str

    def __init__(self, uses_ssl, host, port, username, password, vhost):
        self.uses_ssl = uses_ssl
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.vhost = vhost or "/"


class Config(ModuleType):
    """ModuleType class for the app config."""

    # RabbitMQ
    RABBITMQ_HOST: str
    RABBITMQ_SSL: bool
    RABBITMQ_PORT: int
    RABBITMQ_USERNAME: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_VHOST: str
    RABBITMQ_CRUD_QUEUE: str
    RABBITMQ_FEEDBACK_EXCHANGE: str

    RABBITMQ_CPTD_USERNAME: str
    RABBITMQ_CPTD_PASSWORD: str
    RABBITMQ_CPTD_CRUD_EXCHANGE: str
    RABBITMQ_CPTD_FEEDBACK_QUEUE: str

    RABBITMQ_PUBLISH_RETRY_DELAY: int
    RABBITMQ_PUBLISH_RETRIES: int

    # RedPanda
    REDPANDA_BASE_URI: str
