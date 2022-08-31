docker exec -t example1-rabbitmq rabbitmqctl add_vhost test
docker exec -t example1-rabbitmq rabbitmqctl set_permissions -p test admin ".*" ".*" ".*"
docker exec -t example1-rabbitmq rabbitmqadmin declare exchange --vhost=test name=test_exchange type=topic -u admin -p development
docker exec -t example1-rabbitmq rabbitmqadmin declare queue --vhost=test name=test.crud-operations durable=true -u admin -p development
docker exec -t example1-rabbitmq rabbitmqadmin --vhost="test" declare binding source="test_exchange" destination_type="queue" destination="test.crud-operations" routing_key="testing_routing_key.#" -u admin -p development
