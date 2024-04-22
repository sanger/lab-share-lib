#!/bin/bash
if [ $# -ne 2 ]; then
  echo "Syntax:"
  echo "  push.sh <REDPANDA_URL>"
  echo "where:"
  echo "  <REDPANDA_URL>: URL to connect to RedPanda where the schemas will be uploaded"
  exit 1
fi
REDPANDA_URL=$1

CONTENT_TYPE="Content-Type: application/vnd.schemaregistry.v1+json"

pushd "$(dirname "$0")"

for schema in `find . -name "*.avsc"`; do
  schema_name=`dirname $schema | sed 's/\.//g' | sed 's/\///g'`

  echo "Uploading schema $schema_name"
  curl -X POST -d @$schema -H "$CONTENT_TYPE" "$REDPANDA_URL/subjects/$schema_name/versions"

  echo
done

popd 1>/dev/null
