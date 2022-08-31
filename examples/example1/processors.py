class Example1MessageProcessor:
    def __init__(self, schema_registry, basic_publisher, config):
        return

    def process(self, message):
        print("Message read: ")
        print(message.message)
        return True
