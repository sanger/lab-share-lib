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
use them to deserialize the contents of the message, by using the format and compression codec specified 
in the headers.

* Schema validation: after the contents of the message has been extracted, it is validated using the 
schemas provided by the Redpanda Schema registry. To do that, it reads from the headers the subject name
and version number of the schema the message was encoded into. With these two fields it will request
the Redpanda service for the schema published using that subject and version number. The schema downloaded
is then processed by the [fastavro](https://github.com/fastavro/fastavro) library to validate the correction of the message contents.

* Message processing: if the validation is correct, a new instance of the Processor class defined in 
the PROCESSORS field of the config is created and the library will call the method `process()` with the
contents of the message. Any required behaviour for the processing of the message can be added inside this
method. If the process is correct (returns True), the message is purged, but if the process is incorrect (returns False) the message is rejected.

## Setting up a consumer

To set up a consumer first we need to define the configuration settings that the consumer will use to run.

There is an example of all the settings in the file: [example1/config.py](example1/config.py) that you can modify to adapt to your own settings.

Second, we have to define a new processor for the messages to read. To do it, you have add a new entry in the
[example1/config.py](example1/config.py) file we created before with the name of the class we want to use. For example:

```python
# Hash that maps each subject name with a processor class that will be instantiated when
# we consume a message using that subject name (specified in header from rabbitmq: 'subject')
PROCESSORS={
    'example_1_message': Example1MessageProcessor 
}
```

This will define a new processor class `Example1MessageProcessor` that will process any new messages where the subject name is 'example_1_message'.

In [example1/processors.py](example1/processors.py) we have an example of a processor class skeleton you can use to implement new process for messages received with subject 'example_1_message':

```python
class Example1MessageProcessor:
    def __init__(self, schema_registry, basic_publisher, config):
        return

    def process(self, message):
        print(message.message)
        return True
```

The method `process` receives a message as argument after being unserialized, so you can perform there the process you require for the message.

Third we have to start our consumer in the app we are working on.  A LabShare consumer will run as a separate thread from the main application after starting. As such, there are different options to control how the consumer is performing where, but the most basic could be to check inside an infinite loop. For example:

```python
import time
from lab_share_lib.rabbit.rabbit_stack import RabbitStack

settings = "config"

if __name__ == "__main__":
    print("Starting LabShare consumer")
    rabbit_stack = RabbitStack(settings)

    rabbit_stack.bring_stack_up()

    try:
        while True:
            if rabbit_stack.is_healthy:
                print("RabbitStack thread is running healthy")
            time.sleep(5)
    except KeyboardInterrupt:
        print("Stopping LabShare consumer...")
```

# Publishers

A publisher is any application that publishes a new message in an exchange. The queue system will forward the
message to the required queue/s depending on the configuration created for it (check [RabbitMQ documentation](https://www.rabbitmq.com/tutorials/amqp-concepts.html)).

## How does a publisher serializes a new message

A LabShare publisher requires every message to be serialized in order to be sent. The elements that intervene
in this message serialization are:

* Schema selection: every message requires to be written following a schema defined in the Redpanda Schema registry. The schema is obtained by specifying a subject name and a version number. When we publish a message, the subject name is provided in the 'subject' Rabbitmq header, and the version number in the 'version' RabbitMQ header.
* Message format: in LabShare we can use 2 different types of formats: 'json' or 'binary' which describe how
the data is published in the queue. When publishing a new message the format is provided in the 'encoder_type' RabbitMQ header.
* Message compression: if the selected format is 'binary', in LabShare we can choose among 3 different types of compression: 'null', 'deflate' or 'snappy'. This compression allows to reduce the size of messages being sent. The compression can be inferred from the contents so no header is provided by the publisher to send.

** Note ** As stated before, the default publisher in LabShare library uses 3 headers: subject, version and encoder_type. There is also another very important setting that is not a header but is also enabled by default: PERSISTENT_DELIVERY_MODE that enables the exchange to persist the messages received so they remain in the queue even after a RabbitMQ service is restarted. 

## Setting up a publisher

With this in mind, in the file [example1/publisher_example.py](example1/publisher_example.py) we have provided an example of what
you can run to publish a message in a LabShare set of services. This example will use the schema defined in
[dependencies/schemas/example_1_message/schema.avsc](dependencies/schemas/example_1_message/schema.avsc) and the 'latest' version published for that schema. If you use the dependencies script provided [dependencies/up.sh](dependencies/up.sh) the schemas will be published by default, but if you want to modify this schema to use a different message format, you can make the modification in that schema file and publish again the schema with the command:

```bash
./examples/dependencies/schemas/push_schemas.sh <redpanda_url> <repanda_secret_key_if_any>
```

# Running the examples

In the folder [example1](example1) we have added an example of both publisher and consumer you can use to test.
In order to run this examples first you will need to run the dependent services: RabbitMQ and Redpanda schema registry. 

## Preconditions

To run the examples make sure you match the following requirements:

* docker-compose command available in your PATH. You can check by seeing it can be found with the command:
```
which docker-compose
```
* No applications running in ports 5672, 8080 and 8081. You can check the open ports in your local with the command:
```
netstat -an -ptcp | grep LISTEN
```

## Running dependent services

To be able to run the examples we have provided a docker stack with the dependent services you can start in local with:

```
./examples/dependencies/up.sh
```

After starting, you will be able to access the Rabbitmq admin UI at http://localhost:8080 with credentials user: admin and password: development. The required Rabbitmq elements (user, password, queues, exchanges...) are created automatically on startup. Also the Redpanda schemas are published automatically in this startup.

## Running the examples

After setting up the services, you have to create a python environment for the examples. To facilitate setting up the environment, we provide you with a Docker file that you can use to setup the local running environment with these commands:

```shell
cd examples
docker build . -t examples-lab-share
docker run -v $(pwd):/code --env LOCALHOST=host.docker.internal -ti examples-lab-share bash
```

Then you can run the publisher, that will publish a new message in the queue:

```shell
pipenv run python ./example1/publisher_example.py
```

which will display a message similar to this:

```shell
Sending message: This is the message sent from the publisher at 2022-09-05 10:03:05.610317
```

After that you can consume this message by running the consumer:

```shell
pipenv run python ./example1/consumer_example.py
```

which will display a message like:

```text
Starting LabShare consumer
RabbitStack thread is running healthy
Message read from the queue at 2022-09-05 10:03:09.560891:
<<
This is the message sent from the publisher at 2022-09-05 10:03:05.610317
>>
```

The consumer will keep listening for any more published messages. 

*To stop everything again*:

1. By pressing Control-C you can kill the consumer:

```text
^CStopping LabShare consumer...
```

2. Run the quit command to go out of the bash session from the Docker container:

```shell
exit
```

3. Kill all dependent services Rabbitmq and Redpanda:

```shell
./dependencies/down.sh
```
