#!/bin/bash

# shellcheck disable=SC1091,SC2154,SC2001,SC2155,SC2207,SC2116,SC2086,SC2068,SC2145,SC2034

# https://github.build.ge.com/CloudPod/whodat
# https://github.build.ge.com/503345432/whodat


myDir="$( dirname "$0" )"
source "${myDir}/incl.sh"

function whodat_help() {
    echo -e "Usage: SSO [--brief] [--owner] [--title <title>]"
    echo -e "Usage: --idm {email | groupID | name | sso}=<value of given key>"
    wline
    echo "Aruments"
    echo "  -b --brief  breif report"
    echo "  -i --idm    idm reports, requires one of below arg:"
    echo "                  email="email address of idm DL""
    echo "                  groupId="groupId of idm DL""
    echo "                  name="name of idm DL""
    echo "                  sso="sso of user in idm DLs""
    echo "  -o --owner  show owner info if sso requested from account info of whois"
    echo "  -t --title  show sso info with given title"
    echo
    echo "Unittest Brief"
    echo -e "  whodatpeep ${Blue}--idm${NC} ${Yellow}email=aws-p-jump-elevated-admin_432375862099@ge.com${NC} ${Blue}--brief${NC}       ${Green}# 1 Primary Manger, 3 Other Managers, 4 Members${NC}"
    echo -e "  whodatpeep ${Blue}--idm${NC} ${Yellow}email=aws-p-jump-elevated-approver_432375862099@ge.com${NC} ${Blue}--brief${NC}    ${Green}# 1 Primary Manger, 3 Other Managers, 4 Members${NC}"
    echo -e "  whodatpeep ${Blue}--idm${NC} ${Yellow}email=aws-p-jump-elevated-admin_589623221417@ge.com${NC} ${Blue}--brief${NC}       ${Green}# 1 Primary Manger, 3 Other Managers, 30 Members${NC}"
    echo
    echo "Unittest Full"
    echo -e "  whodatpeep ${Blue}--idm${NC} ${Yellow}email=aws-p-jump-elevated-admin_432375862099@ge.com${NC}               ${Green}# 1 Primary Manger, 3 Other Managers, 4 Members${NC}"
    echo -e "  whodatpeep ${Blue}--idm${NC} ${Yellow}email=aws-p-jump-elevated-approver_432375862099@ge.com${NC}            ${Green}# 1 Primary Manger, 3 Other Managers, 4 Members${NC}"
    echo -e "  whodatpeep ${Blue}--idm${NC} ${Yellow}email=aws-p-jump-elevated-admin_589623221417@ge.com${NC}               ${Green}# 1 Primary Manger, 3 Other Managers, 30 Members${NC}"

    iCritical "Missing reuired 1st parameter of SSO! or --idm [email=...|name=...|groupId=...|sso=...]"
}

[ 0 -eq $# ] && whodat_help

# extract args and kwargs
iTrace "Args: $#"
while [ $# -gt 0 ]; do
    case $1 in
        # options
        -b|--brief)
            brief=1
            iTrace "--brief"
            shift;;
        -i|--idm)
            idm="$2"
            iTrace "IDM: $idm"
            shift;shift;;
        -o|--owner)
            owner='--owner' && TITLE="Owner Info"
            iTrace "--owner"  
            shift;;
        -t|--title)
            TITLE="$2"
            iTrace "Title: $TITLE"
            shift;shift;;
        -h|--help)
            whodat_help
            shift;;
        *)
            sso="$1"
            iTrace "SSO: $sso"
            shift;;
    esac
done


# [[ -z "$idm" && -z "$soo" ]] && whodat_help

[ -z "$HRUS_KEY" ] && export HRUS_KEY="$( cat $HOME/.HRUS_KEY )"

ACTION=''
QUERY=''
TAB='  '

if [ -n "$sso" ]; then
    [ -z "$TITLE" ] && TITLE="Person Info"
    TITLE="${TITLE} on $( date +%d-%b-%Y )"

    if [ 0 -eq "$(isInt "$sso") $?" ]; then
        # /user?sso=$sso # if 9 digits 
        ACTION='SSO'
        QUERY="user?sso=${sso}"
        shift;
    fi

    if [[ "$sso" == *", "* ]]; then
        # /user?firstName=$firstName&lastName=$lastName # if has ,
        arr=$( echo "$sso" | tr ' ' '_' | sed 's/,_/,/g' )
        shift;
        IFS=', ' read -ra name_arr <<< "$arr"
        lastName="${name_arr[0]}"
        firstName="${name_arr[1]}"
        
        LastName=$(echo "${lastName}" | sed 's/_/ /g' )
        FirstName=$(echo "${firstName}" | sed 's/_/ /g' )
        
        echo "Last  Name: ${LastName}"
        echo "First Name: ${FirstName}"

        lastName=$(echo "${lastName}" | sed 's/_/%20/g' )
        firstName=$(echo "${firstName}" | sed 's/_/%20/g' )

        ACTION='USER_NAME'
        QUERY="user?lastName=${lastName}&firstName=${firstName}"
    fi

    if [[ "$sso" == *"@ge.com"* ]]; then
        # /user?email=$email # if has @ge.com
        email="$sso"
        shift;
        ACTION='EMAIL'
        QUERY="user?email=$email"
    fi
fi

if [ -n "$idm" ]; then
    TITLE="Identity Manager Report"
    TITLE="${TITLE} on $( date +%d-%b-%Y )"

    idm=$( echo "$idm" | sed 's/ /%20/g' )
    QUERY="idm?$idm"

    [[ "$idm" == "name="* ]] && ACTION="IDM_NAME"
    [[ "$idm" == "email="* ]] && ACTION="IDM_EMAIL"
    [[ "$idm" == "groupId="* ]] && ACTION="IDM_GROUP"
fi


URL="https://hr-us.gecloud.io/$QUERY"
ppwide -b '-' "US HR Lookup for (${Yellow}$URL${NC})"
res=$( curl -sS -X GET $URL \
    -H 'Cache-Control: no-cache' \
    -H 'Content-Type: application/json' \
    -H "x-api-key: $HRUS_KEY")

iTrace "ec: $?"
iTrace "$res"
if [ -z "$brief" ]; then
    echo "$res" | jq .
    echo
fi

## SSO Report
if [ -n "$sso" ]; then
    ACTIONS=( SSO USER_NAME EMAIL )

    if [ 0 -eq "$( inarr "${ACTION}" "${ACTIONS[@]}" ) $?" ]; then
        status=$(echo "$res" | jq .gessostatus --raw-output ) # must be 'A'
        sso=$( echo "$res" | jq .uid --raw-output  )
        fullName=$( echo "$res" | jq .cn --raw-output  )
        email=$(echo "$res" | jq .mail  --raw-output )
        mobile=$( echo "$res" | jq .mobile --raw-output  )

        startDate=$( echo "$res" | jq .gessoeffectivestartdate --raw-output  )
        endDate=$( echo "$res" | jq .gessoeffectiveenddate --raw-output  ) # must be less than today 

        type=$(echo "$res" | jq .employeeType  --raw-output )
        title=$(echo "$res" | jq .title  --raw-output )

        company=$( echo "$res" | jq .gessocompanyname --raw-output  )
        role=$(echo "$res" | jq .gessojobfunction  --raw-output )
        bu=$(echo "$res" | jq .gehrbusinesssegment  --raw-output )
    fi

    [ 'A' == "$status" ] && color="${Green}" || color="${uRed}"
    [ 'I' == "$status" ] && status_name=" as ${uRed}Inactive${NC}"
    [ 'Contractor' == "$type" ] && eColor="${Yellow}" || eColor="${Blue}"
    [ 'I' == "$status" ] && eColor="${uRed}"

    echo -e "${TAB}$TITLE"
    wline
    C1=35
    echo -e "${TAB}Status: ${color}$( jstr -l -w $C1 "${status}" )${NC} ${TAB}Type  : ${eColor}${type}${NC}"
    echo -e "${TAB}SSO   : $( jstr -l -w $C1 "${sso}" ) ${TAB}Title : ${title}"
    echo -e "${TAB}Name  : $( jstr -l -w $C1 "${fullName}" ) ${TAB}Comp. : $company"
    echo -e "${TAB}eMail : $( jstr -l -w $C1 "${email}" ) ${TAB}Func. : $role"
    echo -e "${TAB}Mobile: $( jstr -l -w $C1 "${mobile}" ) ${TAB}Role  : $bu"
    echo -e "${TAB}Start : $( jstr -l -w $C1 "${startDate}" ) ${TAB}End   : $endDate"

    echo

    [ 'A' != "$status" ] && iWarning "User Status is ${uRed}${status}${NC}${status_name}! It must be '${Green}A${NC}' as ${Green}Active${NC}"
    [ 'null' == "$sso" ] && iWarning "User not found! Make sure you entered a valid SSO!" 
fi

## IDM Report
if [ -n "$idm" ]; then
    ACTIONS=( IDM_NAME IDM_EMAIL IDM_GROUP IDM_SSO )

    primaryManager=$( echo "$res" | jq .primaryManager --raw-output )
    otherManagers=$( echo "$res" | jq .otherManagers | tr -d '[],"' | grep -v '^$' | awk '{print $1}' | tr '\n' ' ' )
    otherManagers=($( echo "$otherManagers" ))
    managerCount="${#otherManagers[@]}"


    members=$( echo "$res" | jq .members | tr -d '[],"' | grep -v '^$' | awk '{print $1}' | tr '\n' ' ' )
    members=($( echo "$members" ))
    membersCount="${#members[@]}"

    # primary manager
    ${myDir}/whodatpeep.sh "$primaryManager" --brief --title "${Red}DL Primary Manager${NC}"

    if [ -z "$brief" ]; then
        if [ '{}' != "$res" ]; then
            # other managers
            i=0
            for SSO in ${otherManagers[@]}; do
                i=$(( i + 1 ))
                iStr=$( jstr -r -w 2 $i )
                ${myDir}/whodatpeep.sh "$SSO" --brief --title "${iStr}/${managerCount}. ${Blue}DL Other Managers${NC}"
            done

            # members
            i=0
            for SSO in ${members[@]}; do
                i=$(( i + 1 ))
                iStr=$( jstr -r -w 2 $i )
                ${myDir}/whodatpeep.sh "$SSO" --brief --title "${iStr}/${membersCount}. ${Green}DL Members${NC}"
            done
        fi
    else
        echo -e "${TAB}${managerCount} Other Managers: ${otherManagers[@]}"
        echo -e "${TAB}${membersCount} Members: ${members[@]}"
    fi
fi

# Unittest
# whodatpeep --idm email=aws-p-jump-elevated-admin_432375862099@ge.com
# whodatpeep --idm email=aws-p-jump-elevated-approver_432375862099@ge.com
# whodatpeep --idm email=aws-p-jump-elevated-admin_589623221417@ge.com
# whodatpeep 503345432


# @GE Genpact Edison Cloud OPS
# Description :- GEHC Edison Cloud Ops
# Type : Public
# Email : GEHC.Genpact.Edison.CloudOPS@ge.com
# GroupID : g01396261