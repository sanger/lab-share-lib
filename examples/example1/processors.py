import datetime


class Example1MessageProcessor:
    def __init__(self, schema_registry, basic_publisher, config):
        return

    def process(self, message):
        print(f"Message read from the queue at { datetime.datetime.now() }:")
        print("<<")
        print(message.message)
        print(">>")
        return True
