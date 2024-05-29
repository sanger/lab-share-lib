from dataclasses import dataclass
from typing import Dict

from lab_share_lib.processing.base_processor import BaseProcessor


@dataclass
class ProcessorConfig():
    rabbit_server_name: str
    processors: Dict[str, BaseProcessor]
