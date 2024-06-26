import logging
from functools import lru_cache

from requests import get

from lab_share_lib.exceptions import TransientRabbitError

RESPONSE_KEY_VERSION = "version"
RESPONSE_KEY_SCHEMA = "schema"

LOGGER = logging.getLogger(__name__)


@lru_cache
def get_json_from_url(url: str, verify: bool) -> dict:
    try:
        return (dict)(get(url, verify=verify).json())
    except Exception:
        raise TransientRabbitError(f"Unable to connect to schema registry at {url}")


class SchemaRegistry:
    def __init__(self, base_uri: str, verify: bool = True):
        self._base_uri = base_uri
        self._verify = verify

    def get_schema(self, subject: str, version: str = "latest") -> dict:
        schema_url = f"{self._base_uri}/subjects/{subject}/versions/{version}"
        LOGGER.debug(f"Getting schema from registry at {schema_url}.")

        return get_json_from_url(schema_url, self._verify)
