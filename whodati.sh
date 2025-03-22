#!/bin/bash

# https://github.build.ge.com/CloudPod/whodat
# https://github.build.ge.com/503345432/whodat

myDir="$( dirname "$0" )"
source "${myDir}/incl.sh"

[ -z "$1" ] && iCritical "Missing reuired 1st parameter of 'Private IP Address'!"

[ -z "$NAAPI_KEY" ] && export NAAPI_KEY="$( cat $HOME/.NAAPI_KEY )"

IP=$1
IID=$(curl -s -H "x-api-key: $NAAPI_KEY" -H "Content-Type: application/json" \
    "https://naapi-wrappy.gecloudpod.com/aws/ec2/networkinterface?configuration.privateIpAddress=$IP" | \
    jq .hits.hits[0]._source.configuration.attachment.instanceId | sed -e 's/^"//' -e 's/"$//')

curl -s -H "x-api-key: $NAAPI_KEY" -H "Content-Type: application/json" \
    "https://naapi-wrappy.gecloudpod.com/aws/ec2/instance?configuration.instanceId=$IID" | \
    jq .
