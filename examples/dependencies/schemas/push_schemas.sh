#!/bin/bash
if [ $# -ne 2 ]; then
  echo "Syntax:"
  echo "  push.sh <REDPANDA_URL> <API_KEY>"
  echo "where:"
  echo "  <REDPANDA_URL>: URL to connect to RedPanda where the schemas will be uploaded"
  echo "  <API_KEY>: secret key with write permission for redpanda"
  exit 1
fi
REDPANDA_URL=$1
API_KEY=$2
 
CONTENT_TYPE="Content-Type: application/vnd.schemaregistry.v1+json"
API_KEY_HEADER="X-API-KEY: $API_KEY"

pushd "$(dirname "$0")"

for schema in `find . -name "*.avsc"`; do
  schema_name=`dirname $schema | sed 's/\.//g' | sed 's/\///g'`

  # Convert to schema
  echo "{\"schema\":" > $schema.tmp
  jq -c 'tojson' $schema >> $schema.tmp
  echo "}" >> $schema.tmp
  
  echo "Uploading schema $schema_name"
  curl -X POST -d @$schema.tmp -H "$CONTENT_TYPE" -H "$API_KEY_HEADER" "$REDPANDA_URL/subjects/$schema_name/versions"

  # Remove temp file
  rm $schema.tmp
  echo 
done

popd 1>/dev/null
