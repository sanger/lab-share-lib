# How to use the library

This library provide the tools to use together a Redpanda schema registry and a Rabbitmq queue system to 
consume and publish messages.

# Consumers

A consumer is a process that has the functionality of removing a message from the top of the queue,
 process it, and go to the next message, doing the same with any subsequent messages until the queue
is empty. In that moment it stays waiting until new messages are published in the queue, so it can start 
again.

## How a LabShare consumer process works

A LabShare consumer adds some extra process to the default consumer behaviour. The process of a message using a LabShare consumer can be structured in different stages:

* Message decoding: in this stage the consumer will read the headers attached to the message, and will 
use them to deserialize the contents of the message, by using the format and compresion codec specified 
in the headers.

* Schema validation: after the contents of the message has been extracted, it is validated using the 
schemas provided by the Redpanda Schema registry. To do that, it reads from the headers ... the subject name
and version number of the schema the message was encoded into. With these two fields it will request
the Redpanda service for the schema published using that subject and version number. The schema downloaded
is then processed by the Fastavro library to validate the correction of the message contents.

* Message processing: if the validation is correct, a new instance of the Processor class defined in 
the PROCESSORS field of the config is created and the library will call the method process() with the
contents of the message. Any required behaviour for the processing of the message can be added inside this
method. If the process is correct (returns True), the message is purged, but if the process is incorrect (returns False) the message is sent to the dead letters queue.

## Setting up a consumer

To set up a consumer first we need to define the configuration settings that the consumer will use to run.
These are the settings required for a consumer:

You can copy file ```examples/example1/config.py``` and modify with your settings.

Second, we have to define a new processor for the messages to read. To do it, you have add a new entry in the
```examples/example1/config.py``` we created before with the name of the class we want to use. For example:

```python
# Hash that maps each subject name with a processor class that will be instantiated when
# we consume a message using that subject name (specified in header from rabbitmq: 'subject')
PROCESSORS={
    'example_1_message': Example1MessageProcessor 
}
```

This will define a new processor class Example1MessageProcessor that will process any new messages where the subject name is 'example_1_message'.

In ```examples/example1/processors.py``` we have an example of a processor class skeleton you can use to implement new 
process for messages received with subject 'example_1_message':

```python
class Example1MessageProcessor:
    def __init__(self, schema_registry, basic_publisher, config):
        return

    def process(self, message):
        print(message.message)
        return True
```

The method ```process``` receives a message as argument after being unserialized, so you can perform there the process you require for the message.

Third we have to start our consumer in the app we are working on.  A LabShare consumer will run as a separate thread from the main application after starting. As such there are different options to control how the consumer is performing where. the most basic could be to check inside an infinite loop. For example:

```python
import time
from lab_share_lib.rabbit.rabbit_stack import RabbitStack

settings = "config"

if __name__ == "__main__":
    print("Starting TOL consumer")
    rabbit_stack = RabbitStack(settings)

    rabbit_stack.bring_stack_up()

    try:
        while True:
            if rabbit_stack.is_healthy:
                print("RabbitStack thread is running healthy")
            time.sleep(5)
    except KeyboardInterrupt:
        print("Stopping TOL consumer...")
```

# Publishers

A publisher is any application that publishes a new message in an exchange. The queue system will forward the
message to the required queue/s depending on the configuration created for it (check Rabbitmq documentation).

## How does a publisher serializes a new message

A LabShare publisher requires every message to be serialized in order to be sent. The elements that intervene
in this message serialization are:

* Schema selection: every message requires to be written following a schema defined in the Redpanda Schema registry. The schema is obtained by specifying a subject name and a version number. When we publish a message, the subject name is provided in the 'subject' Rabbitmq header, and the version number in the 'version' Rabbitmq header.
* Message format: in LabShare we can use 2 different types of formats: 'json' or 'binary' which describe how
the data is published in the queue. When publishing a new message the format is provided in the 'encoder_type' Rabbitmq header.
* Message compression: if the selected format is 'binary', in LabShare we can choose among 3 different types of compression: 'null', 'deflate' or 'snappy'. This compression allows to reduce the size of messages being sent. The compression can be inferred from the contents so no header is provided by the publiserh to send.

** Note ** As stated before, the default publisher in LabShare library uses 3 headers: subject, version and encoder_type. There is also another very important setting that is not a header but is also enabled by default: PERSISTENT_DELIVERY_MODE that enables the exchange to persist the messages received so they remain in the queue even after a Rabbitmq service is restarted. 

## Setting up a publisher

With this in mind, in the file ```examples/example1/publisher_example.py``` we have provided an example of what
you can run to publish a message in a LabShare set of services.

# Running the examples

In folder examples/example we have added an example of both publisher and consumer you can use to test.
In order to run this examples first you will need the dependent services: Rabbitmq and Redpanda schema registry. To start them we have provided a docker stack you can start in local with:

```
./examples/dependencies/up.sh
```

After starting, you will be able to access the Rabbitmq admin UI at http://localhost:8080 with credentials user: admin and password: development. The required elements (user, password, queues, exchanges...) are 
created automatically on startup.

After setting up the services, you have to create a python environment for the examples:
```
cd examples
pipenv shell
pipenv install
```

And then you can run the consumer:

```
python ./example1/consumer_example.py
```

Or the publisher:

```
python ./example1/publisher_example.py
```