#!/bin/bash

# this will make the update not to happen if any of the intermediate
# steps fail
set -e

CLOUD_INFO_DIR="$1"
CLOUD_INFO_CLOUD="cloud-info"
CLOUD_INFO_CONTAINER="cloud-info"

DIR="$(mktemp -d)"
chmod 755 "$DIR"
openstack --os-cloud "$CLOUD_INFO_CLOUD" \
	object list "$CLOUD_INFO_CONTAINER" -f json >"$DIR/objs.json"
for f in $(jq -r -n 'inputs[] | values[]' <"$DIR/objs.json"); do
	echo "Downloading: $f"
	openstack --os-cloud "$CLOUD_INFO_CLOUD" object save \
		"$CLOUD_INFO_CONTAINER" --file "$DIR/$f" "$f"
done

rm -f "$DIR/objs.json"

rsync -a --delete-after "$DIR/" "$CLOUD_INFO_DIR"

rm -rf "$DIR"
