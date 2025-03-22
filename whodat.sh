#!/bin/bash

# https://github.build.ge.com/CloudPod/whodat
# https://github.build.ge.com/503345432/whodat

myDir="$( dirname "$0" )"
source "${myDir}/incl.sh"


for arg in "$@"; do
    [[ "$arg" = "-h" || "$arg" = "--help" ]] && help='--help'  
    [[ "$arg" = "-b" || "$arg" = "--brief" ]] && brief='--brief'  
    [[ "$arg" = "-f" || "$arg" = "--full" ]] && full='--full'  
    [[ "$arg" = "-o" || "$arg" = "--owner" ]] && show_owners='--owner'  
done

function whodat_help() {
    echo -e "Usage: ACCOUNT_ID | ACCOUNT_ALAIS [--owner] [--brief] [--full]"
    wline
    echo
    echo "required:"
    echo "  csv list of ACCOUNT_ID or ACCOUNT_ALAIS or mix of both"
    echo
    echo "args:"
    echo "  -h  --help      show this help and exit"
    echo "  -b  --brief     show breif report"
    echo "  -f  --full      show full report"
    echo "  -o  --owner     report owners"
    echo
}

# default to brief
[ -z "$full" ] && brief='--brief'

if [[ -z "$1" || -n "$help" ]]; then
    whodat_help
    [ -z "$1" ] && iCritical "Missing reuired 1st csv parameter of ACCOUNT_ID or ACCOUNT_ALAIS!"
    exit 0
fi

[ -z "$CMC_KEY" ] && export CMC_KEY="$( cat $HOME/.CMC_KEY )"


if [ 0 -eq "$(isInt "$1") $?" ]; then
    ACCOUNTS=$( echo "$1" )
    shift;
else
    ACCOUNTS=($( echo "${1,,}" | tr ',' ' ' ))
    shift;
fi

OWNERS_LIST=''
i=0
for ACCOUNT in ${ACCOUNTS[@]}; do
    i=$(( i + 1 ))
    # Translate nnnn-nnnn-nnnn to nnnnnnnnnnn
    [[ '-' == "${ACCOUNT:4:1}" && '-' == "${ACCOUNT:9:1}" ]] && ACCOUNT=$( echo "${ACCOUNT}" | tr -d '-' )

    # Skip if empty for trailing extra comma
    [ -z "$ACCOUNT" ] && continue
    
    # Auto handle missing leading zeros
    [ 0 -eq "$( isInt "$ACCOUNT" ) $?" ] && ACCOUNT=$( ndigits "$ACCOUNT" 12 )

    url="https://cmc.gecloud.io/account/$ACCOUNT"
    [ 1 -eq "$i" ] && echo
    ppwide -b '-' "CMC Lookup for (${Yellow}$url${NC}) on $( date +%d-%b-%Y )"
    res=$(curl -sS -X GET $url \
        -H 'Cache-Control: no-cache' \
        -H 'Content-Type: application/json' \
        -H "x-api-key: $CMC_KEY")

    if [ -z "$brief" ]; then
        echo "$res" | jq .
        echo
    fi

    account=$( echo "$res" | jq .account_id | tr -d '"' )
    alias=$( echo "$res" | jq .account_name | tr -d '"' )
    region=$( echo "$res" | jq .connected_regions  | tr -d '" [\n]' )
    provision=$( echo "$res" | jq .provision_date | tr -d '"' )
    migration=$( echo "$res" | jq .migration_date | tr -d '"' )
    suspended=$( echo "$res" | jq .suspended_date | tr -d '"' )
    ejected=$( echo "$res" | jq .ejected_date | tr -d '"' )
    bu=$(echo "$res" | jq .business_unit  | tr -d '"')
    owner=$(echo "$res" | jq .owner  | tr -d '"' | tr ';' ',')
    status=$(echo "$res" | jq .status  | tr -d '"')
    sku=$(echo "$res" | jq .sku  | tr -d '"')
    error=$(echo "$res" | jq .error  | tr -d '"')

    JOIN_TYPE=''
    [ "${#migration}" -gt 5 ] && JOIN_TYPE='Migration'
    [ "${#provision}" -gt 5 ] && JOIN_TYPE='Provisioning'

    STATUS=''
    [ 'Active' = "$status" ] && STATUS="${Green}${status}${NC} State"
    [ 'Building' = "$status" ] && STATUS="${Blue}${status}${NC} State"
    [ 'Decommissioning' = "$status" ] && STATUS="${uRed}${status}${NC} State"
    [ 'Ejected' = "$status" ] && STATUS="${uRed}${status}${NC} on ${uRed}${ejected}${NC}"
    [ 'Suspended' = "$status" ] && STATUS="${uRed}${status}${NC} on ${uRed}${suspended}${NC}"

    EXTRA=''
    # Could be null, empty or UNKNOWN so len should be gt 7 to validate its existance
    [ "${#region}" -gt 7 ] && EXTRA="${EXTRA}, at ${Blue}${region}${NC} region"
    [ "${#suspended}" -gt 7 ] && EXTRA="${EXTRA}, ${uRed}Suspended${NC} on ${uRed}${suspended}${NC}"
    [ "${#ejected}" -gt 7 ] && EXTRA="${EXTRA}, ${uRed}Ejected${NC} on ${uRed}${ejected}${NC}"
    [ "${#migration}" -gt 7 ] && EXTRA="${EXTRA}, ${Green}Migrated${NC} on ${Green}${migration}${NC}"
    [ "${#provision}" -gt 7 ] && EXTRA="${EXTRA}, ${Blue}Provisioned${NC} on ${Blue}${provision}${NC}"

    TAB='  '
    if [ 'null' = "$error" ]; then
        ppwide -b '-' "${STATUS}"
        echo -e "${TAB}(${Yellow}${account}${NC}) [${Yellow}${alias}${NC}]${EXTRA}"
        echo -e "${TAB}SKU ${Blue}$sku${NC} Owned by ${Green}$owner${NC} in ${Green}$bu${NC}"
        echo
        if [ -n "$show_owners" ]; then
            OWNERS=($( echo "$owner" | tr ';' ' ' | tr ',' ' ' ))
            echo "${TAB}${#OWNERS[@]} Owners Info"
            wline
            for OWNER in ${OWNERS[@]}; do 
                $HOME/whodat/whodatpeep.sh $OWNER $brief $show_owners
            done
        fi
    else
        alias='UNKNOWN'
        [ "$ACCOUNT" = '197171649850' ] && alias='WizAccess-Role'
        owner='UNKNOWN'
        ppwide -b '-' "${uRed}UNKNOWN${NC} Status"
        printf  "%s" "${TAB}${REVERSE}${LIME_YELLOW}(${ACCOUNT}) [${alias}] - External Account!${NORAML}"
        echo -e "${NC} ${NC}"
    fi

    [ -n "$OWNERS_LIST" ] && COMMA=',' || COMMA=''
    OWNERS_LIST="${OWNERS_LIST}${COMMA}${owner}"
done

# OWNERS_LIST Unique
OWNERS_LIST_UNIQ=$( echo "${OWNERS_LIST}" | tr ';' ',' | tr ',' '\n' | sort | uniq | tr '\n' ',' )
[ ',' == ${OWNERS_LIST_UNIQ: -1} ] && OWNERS_LIST_UNIQ="${OWNERS_LIST_UNIQ:0:${#OWNERS_LIST_UNIQ}-1}"
echo -e "Owners List: ${OWNERS_LIST_UNIQ}"


exit 0

## Validation
whodat 720726202926 # Decommissioning
whodat 95058881085  # Decommissioning
whodat 773151204513 # Ejected
whodat 860334990914 # Ejected
whodat 637882043549 # Suspended
whodat 696919637005 # Suspended
whodat 431656361392 # Building
whodat 127366311667 # Building
whodat 204598253536 # Active
whodat 138754820347 # Active
whodat 584190725146 # Active, Provisioned & Migrated
whodat 523084324983 # Active, Provisioned & Migrated
whodat 584190725146 --owner
whodat 584190725146 --owner --brief