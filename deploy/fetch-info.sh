#!/bin/bash

# this will make the update not to happen if any of the intermediate
# steps fail
set -e

CLOUD_INFO_DIR="$1"
CLOUD_INFO_CLOUD="cloud-info"
CLOUD_INFO_CONTAINER="cloud-info"

DIR="$(mktemp -d)"
for f in $(openstack --os-cloud "$CLOUD_INFO_CLOUD" \
	object list "$CLOUD_INFO_CONTAINER" -f json | jq -r -n 'inputs[] | values[]'); do
  echo "Downloading: $f"
  openstack --os-cloud "$CLOUD_INFO_CLOUD" object save \
	  "$CLOUD_INFO_CONTAINER" --file "$DIR/$(dirname "$f").json" "$f"
done

rsync -a --delete-after "$DIR/" "$CLOUD_INFO_DIR"

