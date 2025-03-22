#!/bin/bash

# shellcheck disable=SC2086,SC2155,SC2068,SC1091,SC2145

# https://github.build.ge.com/503345432/whodat

# whois --input-file /tmp/oneidm/jump-roles.txt # see whois.sh
# whois --input-file /tmp/oneidm/sox-roles.txt  # see whois.sh

myDir="$( dirname "$0" )"
source "${myDir}/incl.sh"

[ -z "$HRUS_KEY" ] && export HRUS_KEY="$( cat $HOME/.HRUS_KEY )"
[ -z "$CMC_KEY" ] && export CMC_KEY="$( cat $HOME/.CMC_KEY )"
[ -z "$HOST" ] && export HOST="$( cat $HOME/.HOST )"
[ -z "$PORT" ] && export PORT="$( cat $HOME/.PORT )"
[ -z "$USER" ] && export USER="$( cat $HOME/.USER )"
[ -z "$PASS" ] && export PASS="$( cat $HOME/.PASS )"

for arg in "$@"; do
    [[ "$arg" = "-i" || "$arg" = "--input-file" ]] && FILE="$2"  
done

if [ -n "$FILE" ]; then
    lineCount=$(cat $FILE | grep -Ecv '^#|^$' )

    # Start Timer
    set_timer "From $( get_fmtdate )"

    i=0
    while read -r line; do
        i=$(( i + 1 ))
        [ '#' == "${line:0:1}" ] && continue
        [ -z "${line}" ] && continue
        echo -e ":::: ${i}/${lineCount}. Start ${line} ::::"
        $HOME/whodat/src/whois.py "${line}"
        echo -e ":::: ${i}/${lineCount}. Done!  ${line} ::::"
        set_timer "Process ${line} $( get_fmtdate )"
        wline
    done < $FILE

    # Report Timer Data
    set_timer "Upto $( get_fmtdate )"
    ppwide "Whois / DL Summary Report / From File ${FILE}"
    get_timer

    # Cleanup Timer temp file
    # rm_timer

    exit $?
fi


[ "@" == "${1:0:1}" ] && QUERY="$1" && shift
iTrace "Query: $QUERY $@"

[ -n "${QUERY}" ] && $HOME/whodat/src/whois.py "${QUERY}" $@
[ -z "${QUERY}" ] && $HOME/whodat/src/whois.py $@
