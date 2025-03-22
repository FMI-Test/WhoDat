#!/bin/bash

# shellcheck disable=SC1091,SC2154,SC2001,SC2155,SC2207,SC2116,SC2068,SC2086,SC2059

# https://github.build.ge.com/CloudPod/whodat
# https://github.build.ge.com/503345432/whodat

myDir="$( dirname "$0" )"
source "${myDir}/incl.sh"


for arg in "$@"; do
    [[ "$arg" = "-h" || "$arg" = "--help" ]] && help='--help'  
    [[ "$arg" = "-b" ||  "$arg" == "--brief" ]] && brief=1  
    [[ "$arg" = "-o" ||  "$arg" == "--owner" ]] && owner='--owner' && TITLE="Owner Info"  
done

function whois_help() {
    echo -e "Usage: SSO [--brief] [--full]"
    wline
    echo
    echo "required:"
    echo "  csv list of SSO"
    echo
    echo "args:"
    echo "  -h  --help      show this help and exit"
    echo "  -b  --brief     show breif report"
    echo "  -o  --owner     report owners"
    echo
}

# default to brief
[ -z "$full" ] && brief='--brief'

if [[ -z "$1" || -n "$help" ]]; then
    whois_help
    iCritical "Missing reuired 1st csv parameter of SSO!"
    exit 0
fi

[ -z "$HRUS_KEY" ] && export HRUS_KEY="$( cat $HOME/whodat/.HRUS_KEY )"

ACTION=''
QUERY=''

if [ 0 -eq "$(isInt "$1") $?" ]; then
    SSOS=$( echo "$1" )
    shift;
else
    SSOS=($( echo "${1}," | tr ',' ' ' ))
    shift;
fi


HEAD='%5s %-1s %-12s %-40s %-13s %-35s %-45s %-30s %-20s\n'
COLS='%5s %-1s %-12s %-40s %-24s %-35s %-45s %-30s %-20s\n'
WIDTH=205

TITLE="US HR Lookup for (${#SSOS[@]}) SSOs on $( date +%d-%b-%Y )"
ppwide -a '~' -b '~' -w $WIDTH "${TITLE}"
wline $WIDTH
printf "$HEAD" "" A SSO Name Type Title Role eMail Mobile 
wline $WIDTH
i=0

ACTIVES=0
INACTIVES=0
TS=$( get_ts )
for SSO in ${SSOS[@]}; do
    i=$(( i + 1 ))
    URL="https://hr-us.gecloud.io/user?sso=${SSO}"
    res=$( curl -sS -X GET $URL \
        -H 'Cache-Control: no-cache' \
        -H 'Content-Type: application/json' \
        -H "x-api-key: $HRUS_KEY")

    iTrace "${SSO}"
    iTrace "$res | jq ."

    status=$(echo "$res" | jq .gessostatus --raw-output ) # must be 'A'
    sso=$( echo "$res" | jq .uid --raw-output  )
    fullName=$( echo "$res" | jq .cn --raw-output  | sed 's/, Service//g' )
    email=$(echo "$res" | jq .mail  --raw-output )
    mobile=$( echo "$res" | jq .mobile --raw-output  )
    type=$(echo "$res" | jq .employeeType  --raw-output )
    title=$(echo "$res" | jq .title  --raw-output )
    bu=$(echo "$res" | jq .gehrbusinesssegment  --raw-output )

    [ 'null' == "$status" ] && status=''
    [ 'null' == "$sso" ] && sso=''
    [ 'null' == "$fullName" ] && fullName=''
    [ 'null' == "$email" ] && email=''
    [ 'null' == "$mobile" ] && mobile=''
    [ 'null' == "$type" ] && type=''
    [ 'null' == "$title" ] && title=''
    [ 'null' == "$bu" ] && bu=''

    if [ 'A' != "$status" ]; then
        INACTIVES=$(( INACTIVES + 1 ))
        [ 'Contractor' == "$type" ] && type="Ex Contractor"
        status="${RED}${status}${NORMAL}"
        type="${RED}${type}${NORMAL}"
    else
        ACTIVES=$(( ACTIVES + 1 ))
        status="${GREEN}${status}${NORMAL}"
        [ 'Contractor' == "$type" ] && type="${YELLOW}${type}${NORMAL}"
        [ 'Employee' == "$type" ] && type="${BLUE}${type}${NORMAL}"
        [ 'Ex Employee' == "$type" ] && type="${RED}${type}${NORMAL}"
        [ 'Functional' == "$type" ] && type="${GREEN}${type}${NORMAL}"
    fi

    printf "$COLS" "${i}." "$status" "$sso" "$fullName" "$type" "$bu" "$title" "$email" "$mobile"
done

TOOK=$( took_ts "${TS}" )
wline $WIDTH
echo -e "${Green}${ACTIVES}/${#SSOS[@]}${NC} Active, ${Red}${INACTIVES}/${#SSOS[@]}${NC} Inactive SSO!"
iInfo "Took : ${TOOK}"
echo
iWarning "${Red}I${NC}: Inactive user! ${Green}A${NC}: Active User"


# Test
# whois 210057070,212069299,212320905,212535329,212587208,212599646,212602782,212605880,212617715,212627328,212627556,212679694,212725396,212727721,212732158,212738388,502812200,502817031,502819756,502820180,502820976,502821436,502825324,502832507,502832508,502832752,502833665,502834352,502834816,502834818,502834819,503316567,503319645,503345432,503387629,503388826