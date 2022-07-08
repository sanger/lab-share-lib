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
