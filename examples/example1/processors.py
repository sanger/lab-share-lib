import datetime

from lab_share_lib.processing.base_processor import BaseProcessor


class Example1MessageProcessor(BaseProcessor):
    def instantiate(self, schema_registry, basic_publisher, config):
        return Example1MessageProcessor()

    def process(self, message):
        print(f"Message read from the queue at { datetime.datetime.now() }:")
        print("<<")
        print(message.message)
        print(">>")
        return True
