from typing import Callable

from lab_share_lib.processing.rabbit_message import RabbitMessage


class BaseProcessor:
    process: Callable[["BaseProcessor", RabbitMessage], bool]
