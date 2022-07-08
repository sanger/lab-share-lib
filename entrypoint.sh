#!/usr/bin/env bash

#
# This script waits 15 seconds for connection with the database,
# then it will reset the database if RESET_DATABASE is "true"
# and after that will start the we server
set -o errexit
set -o pipefail
set -o nounset

TIMEOUT=120

./wait_for_connection.sh "${REDPANDA_HOST}" "${REDPANDA_PORT}" "${TIMEOUT}"
./wait_for_connection.sh "${RABBITMQ_HOST}" "${RABBITMQ_PORT}" "${TIMEOUT}"

echo "Starting service"
exec python tol-lab-share
