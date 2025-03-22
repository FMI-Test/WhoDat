#!/bin/bash

# Usage:
# 
# Lookup accounts based on their product SKU. For example to list all "Classic Complete on AWS" accounts run:
#
#  ./whodey.sh cc
#
# https://github.build.ge.com/CloudPod/whodat

[ -z "$CMC_KEY" ] && export CMC_KEY="$( cat $HOME/.CMC_KEY )"

product=$1


if [[ $product == "cc" ]]; then 
    curl -s -X GET https://l471kt85hf.execute-api.us-east-1.amazonaws.com/dev/sku/Classic%20Complete%20on%20AWS \
        -H 'Cache-Control: no-cache' \
        -H 'Content-Type: application/json' \
        -H "x-api-key: $CMC_KEY" \
        | jq .
    exit 0
fi

if [[ $product == "c" ]]; then 
    curl -s -X GET https://l471kt85hf.execute-api.us-east-1.amazonaws.com/dev/sku/Classic%20on%20AWS \
        -H 'Cache-Control: no-cache' \
        -H 'Content-Type: application/json' \
        -H "x-api-key: $CMC_KEY" \
        | jq .
    exit 0
fi

if [[ $product == "gs" ]]; then 
    curl -s -X GET https://l471kt85hf.execute-api.us-east-1.amazonaws.com/dev/sku/Guardrails%20Standard%20on%20AWS \
        -H 'Cache-Control: no-cache' \
        -H 'Content-Type: application/json' \
        -H "x-api-key: $CMC_KEY" \
        | jq .
    exit 0
fi

echo "Lookup accounts based on their product SKU"
echo "-----------------------------------------------"
echo "args:"
echo "  c   Classic on AWS"
echo "  cc  Classic Complete on AWS"
echo "  gs  Guardrails Standard on AWS"

ppwide '=' "CMC Lookup for (${Yellow}$1${NC})"
echo "$res" | jq .

account=$( echo "$res" | jq .account_id | tr -d '"' )
alias=$( echo "$res" | jq .account_name | tr -d '"' )
region=$( echo "$res" | jq .connected_regions  | tr -d '" [\n]' )
migration=$( echo "$res" | jq .migration_date | tr -d '"' )
bu=$(echo "$res" | jq .business_unit  | tr -d '"')
owner=$(echo "$res" | jq .owner  | tr -d '"')
status=$(echo "$res" | jq .status  | tr -d '"')
sku=$(echo "$res" | jq .sku  | tr -d '"')
[ 'Active' = "$status" ] && status="${Green}$status${NC}" || status="${Green}$status${NC}"

echo
echo " Summary"
wline '='
echo -e " (${Yellow}$account${NC}) [${Yellow}$alias${NC}] in ${Yellow}${region}${NC} is ${status} since ${Yellow}${migration}${NC}"
echo -e " ${Green}$owner${NC} from ${Green}$bu${NC} is the Owner of this ${Green}$sku${NC} Account"
echo
