from unittest.mock import MagicMock
import pytest

from lab_share_lib.config.rabbit_config import RabbitConfig, ProcessorSchemaConfig
from lab_share_lib.config.rabbit_server_details import RabbitServerDetails
from lab_share_lib.processing.base_processor import BaseProcessor
from lab_share_lib.types import Config
from tests.constants import RABBITMQ_SUBJECT_CREATE_PLATE, RABBITMQ_SUBJECT_UPDATE_SAMPLE


@pytest.fixture
def rabbit_server_details():
    return RabbitServerDetails(
        uses_ssl=False,
        host="testrabbitmq",
        port=1234,
        username="admin",
        password="development",
        vhost="testvhost",
    )


@pytest.fixture
def create_plate_processor():
    processor = MagicMock(BaseProcessor)
    processor.instantiate.return_value = processor.return_value
    yield processor


@pytest.fixture
def update_sample_processor():
    processor = MagicMock(BaseProcessor)
    processor.instantiate.return_value = processor.return_value
    yield processor


@pytest.fixture
def config(rabbit_server_details, create_plate_processor, update_sample_processor):
    config = Config("test_config")
    config.REDPANDA_BASE_URI = "testredpanda"
    config.RABBITMQ_PUBLISH_RETRIES = 36
    config.RABBITMQ_PUBLISH_RETRY_DELAY = 5
    config.RABBITMQ_SERVERS = [
        RabbitConfig(
            consumer_details=rabbit_server_details,
            consumed_queue="test.crud.queue",
            processors={
                RABBITMQ_SUBJECT_CREATE_PLATE: create_plate_processor,
                RABBITMQ_SUBJECT_UPDATE_SAMPLE: update_sample_processor,
            },
            message_subjects={
                "create-plate": ProcessorSchemaConfig(
                    processor=create_plate_processor,
                    reader_schema_version="1"
                ),
                "update-sample": ProcessorSchemaConfig(
                    processor=update_sample_processor,
                    reader_schema_version="1"
                ),
            },
            publisher_details=rabbit_server_details,
        ),
        RabbitConfig(
            consumer_details=rabbit_server_details,
            consumed_queue="test.update.queue",
            processors={
                RABBITMQ_SUBJECT_UPDATE_SAMPLE: update_sample_processor,
            },
            message_subjects={
                "update-sample": ProcessorSchemaConfig(
                    processor=update_sample_processor,
                    reader_schema_version="1"
                )
            },
            publisher_details=rabbit_server_details,
        ),
    ]

    return config
