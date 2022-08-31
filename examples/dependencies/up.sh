#!/bin/bash

cd "$(dirname "$0")"
docker-compose up -d

# Initialise the Rabbitmq instance
sleep 15
printf "\n\nInitialising the Rabbimq instance...\n\n"
./rabbitmq_setup.sh

# Initialise the schemas
printf "\n\nInitialising the Redpanda instance...\n\n"
./schemas/push_schemas.sh http://localhost:8081 secret-key