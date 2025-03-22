#!/bin/bash

# Usage:
# 
# Lookup accounts based on their product SKU. For example to list all "Classic Complete on AWS" accounts run:
#
#  ./whodey.sh cc
#
# https://github.build.ge.com/CloudPod/whodat
# https://github.build.ge.com/503345432/whodat
# https://github.build.ge.com/PublicCloudServices/cloud-master-catalog-api

myDir="$( dirname "$0" )"
source "${myDir}/incl.sh"

[ -z "$CMC_KEY" ] && export CMC_KEY="$( cat $HOME/.CMC_KEY )"

BUS=( 'Appliances and Lighting' 'Aviation' 'Baker Hughes GE' 'Capital' 'CoreTech' 'Corporate CoreTech' 'Corporate Cyber' 'Corporate DT - Finance' 'Corporate DT - Global Functions' 'Corporate Staff' 'Current' 'Current and Lighting' 'DT - HQ' 'Digital Core' 'Digital Core - Predix' 'Espresso - Current' 'GE Aviation' 'GE Capital' 'GE Corporate' 'GE Digital' 'GE Healthcare' 'GE Oil & Gas' 'GE Power' 'GE Renewable Energy' 'GE Transportation' 'GE Vernova' 'GE Water' 'Gas Power' 'Global Research Center' 'Harvest - Lighting - Tungsram' 'Healthcare' 'Jameson - Capital - AerCap' 'Liberty - Power - ABB' 'Lighting' 'Monaco - Healthcare - Danaher' 'Nuclear' 'Opal - Lighting - Savant Systems LLC' 'Power Conversion' 'Predix' 'Renewable Energy' 'Risk' 'SMO - Separation - Aerospace' 'SMO - Separation - HealthCare' 'SMO - Separation - Vernova' 'Snowflake - Digital - Silver Lake Partners' 'Steam Power' 'TSA - HealthCare' 'X - Transportation - Wabtec' )
SKUS=( "Classic on AWS" "Classic on AWS - Predix" "GovCloud" "Guardrails GovCloud Limited on AWS" "Guardrails GovCloud Standard on AWS" "Guardrails Limited Commercial on AWS" "Guardrails Limited on AWS" "Guardrails Specialty on AWS" "Guardrails Standard on AWS" "Managed Cloud - Nexus" "Managed Cloud - Origin" )
SUBTYPES=( 'AMS Accelerate' 'AMS Advanced' 'Acquisition' 'Admin' 'Amazon AMS' 'Connected' 'GovCloud' 'GovCloud Commercial' 'Healthcloud' 'Inspection Zone' 'Investigation' 'Legacy' 'Limited' 'Master Payer' 'Migration' 'Predix Guardrails' 'Predix Legacy' 'Special Project' 'Specialty' 'Standard' )

ppwide '-' "CMC Lookup Accounts By SKU"
RS=( 'Quit' "${SKUS[@]}" )
PS3='Select 1 to Quit. Select a SKU #? '
select SKU in "${RS[@]}"; do
    case $SKU in
        "$SKU") break ;;
        *) exit ;;
    esac
done

[ 'Quit' = "$SKU" ] && exit 0 
SKU_ENCODE=$( echo "$SKU" | sed 's/ /%20/g' | tr -d "'" )
iTrace "Urlencode SKU : $SKU_ENCODE"
ts=$(get_ts)
RES=$(curl -sS -X GET https://cmc.gecloud.io/accounts/sku/$SKU_ENCODE \
    -H 'Cache-Control: no-cache' \
    -H 'Content-Type: application/json' \
    -H "x-api-key: $CMC_KEY")
    
echo "$RES" | jq .

echo
LEN=$( echo "$RES" | jq length )
ppwide -b '-' "CMC Summary by SKU ${Blue}${SKU}${NC} has ${Green}${LEN}${NC} Accounts. Took ${Yellow}$(took_ts ${ts})${NC}s"
echo

exit 0
### Dev
# DEV=$(curl -s -X GET https://l471kt85hf.execute-api.us-east-1.amazonaws.com/dev/sku/$SKU \
#     -H 'Cache-Control: no-cache' \
#     -H 'Content-Type: application/json' \
#     -H "x-api-key: $CMC_KEY")

# echo "$DEV" | jq .

# echo
# LEN=$( echo "$DEV" | jq length )
# ppwide -b '=' -w 110 "CMC Dev Summary by SKU ${Blue}${SKU}${NC} has ${Green}${LEN}${NC} Accounts. Took ${Yellow}$(took_ts ${ts})${NC}s"
# echo

