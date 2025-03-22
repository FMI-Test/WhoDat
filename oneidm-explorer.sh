#!/bin/bash

# shellcheck disable=SC2086,SC2155,SC2068,SC1091,SC2145,SC2154,SC2140

# https://github.build.ge.com/503345432/whodat

# whois --input-file /tmp/oneidm/sox-roles.txt  # see whois.sh

myDir="$( dirname "$0" )"
source "${myDir}/incl.sh"

function my_help() {
    echo -e "OneIDM Data Explorer Reports Input/Output Data Files"
    wline
    echo -e "Usage: [--datafolder "\$DATAFOLDER"] [--input "\$INPUT_FILE"]"
    echo
    echo "Aruments"
    echo "  -d --datafolder  DATAFOLDER to read output, default '/tmp/oneidm'"
    echo "  -i --input       INPUT_FILE to read one input, default 'gect-sox'"
    echo
    echo "Example input:"
    echo "   --input gect-sox"
    echo "          Will translates to ./inputs/gect-sox.tab"
    echo "          Respective to working directory to abouslute path"
    echo "          Output will be matched from DATAFOLDER to files gect-sox*.*"
    echo
    exit 0
}

TITLE="$(date) GR2 / OneIDM Data Explorer"

CACHEFOLDER="${myDir}/src/__cache__"
CWD=$(pwd)
DATAFOLDER='/tmp/oneidm'
INPUT_PATH="${CWD}/inputs"
[ -z "$INPUT" ] && INPUT="gect-sox"

# Extract args and kwargs
iTrace "Args: $#"
while [ $# -gt 0 ]; do
    case $1 in
        # options
        -h|--help)
            my_help
            # shellcheck disable=SC2317
            shift;;
        # argument
        -d|--datafolder)
            DATAFOLDER="$2"
            iTrace "--datafolder ${DATAFOLDER}"  
            shift;shift;;
        -i|--input)
            INPUT="$2"
            iTrace "--input ${INPUT}"
            shift;shift;;
        *)
            sso="$1"
            iTrace "SSO: $sso"
            shift;;
    esac
done

[ -z "$HRUS_KEY" ] && export HRUS_KEY="$( cat $HOME/.HRUS_KEY )"
[ -z "$CMC_KEY" ] && export CMC_KEY="$( cat $HOME/.CMC_KEY )"
[ -z "$HOST" ] && export HOST="$( cat $HOME/.HOST )"
[ -z "$PORT" ] && export PORT="$( cat $HOME/.PORT )"
[ -z "$USER" ] && export USER="$( cat $HOME/.USER )"
[ -z "$PASS" ] && export PASS="$( cat $HOME/.PASS )"

ppwide "${TITLE}"

# List input File
INPUTS=$( find $INPUT_PATH -type f -name "*.tab" )
echo
print_table \
    --title "${TITLE} / Input Files :: ${YELLOW}${INPUT_PATH}${NORMAL}" \
    --lines "$INPUTS"

# Input File
INPUT_FILE="${INPUT_PATH}/${INPUT}.tab"
if [ -f "$INPUT_FILE" ]; then
    # Input File data
    echo
    print_table \
        --title "${TITLE} / Input File :: ${YELLOW}${INPUT_FILE}${NORMAL}" \
        --file "$INPUT_FILE"

    # Output Files
    echo
    OUTPUTS=$( find $DATAFOLDER -type f -name "${INPUT}*.*" )
    print_table \
        --title "${TITLE} / Output File :: ${YELLOW}${INPUT_FILE}${NORMAL}" \
        --lines "$OUTPUTS"

fi

[ -n "$CMC_KEY" ] && HAS_CMC_KEY='******' || HAS_CMC_KEY=''
[ -n "$HRUS_KEY" ] && HAS_HRUS_KEY='******' || HAS_HRUS_KEY=''
[ -n "$USER" ] && HAS_USER='******' || HAS_USER=''
[ -n "$PASS" ] && HAS_PASS='******' || HAS_PASS=''
[ -n "$HOST" ] && HAS_HOST='******' || HAS_HOST=''
[ -n "$PORT" ] && HAS_PORT='******' || HAS_PORT=''

FILE_NAME=$(echo $INPUT_FILE | awk -F'/' '{print $NF}' | sed 's/.tab//')
GID_FILE="/tmp/oneidm/${FILE_NAME}-gid-data.json"
UID_FILE="/tmp/oneidm/${FILE_NAME}-uid-data.json"
[ -e "$UID_FILE" ] && GID_COUNT=$(jq '. | length' "$GID_FILE") || GID_COUNT=0
[ -e "$UID_FILE" ] && UID_COUNT=$(jq '. | length' "$UID_FILE") || UID_COUNT=0
OUPUT_FILES_COUNT=$(find "/tmp/oneidm/*.*" -type f | wc -l | awk '{print $1}' )
[ "$OUPUT_FILES_COUNT" -gt 0  ] && OUPUT_FILES_COUNTS='s' || OUPUT_FILES_COUNTS=''

echo
echo -e "Working Dir  :: ${iYellow}${CWD}${NC}"
echo -e "DB & Keys    :: CMC: ${iYellow}${HAS_CMC_KEY}${NC}, HRUS: ${iYellow}${HAS_HRUS_KEY}${NC}, USER: ${iYellow}${HAS_USER}${NC}, PASS: ${iYellow}${HAS_PASS}${NC}, HOST: ${iYellow}${HAS_HOST}${NC}, PORT: ${iYellow}${HAS_PORT}${NC}"
echo -e "AWS_PROFILE  :: ${iYellow}${AWS_PROFILE}${NC}"
echo -e "Cache Folder :: ${iYellow}${CACHEFOLDER}${NC}"
echo -e "Data Folder  :: ${iYellow}${DATAFOLDER}${NC}"
echo -e "Output Files :: ${iYellow}${OUPUT_FILES_COUNT}${NC} File${OUPUT_FILES_COUNTS} in ${iYellow}${DATAFOLDER}${NC}"
echo -e "Input Path   :: ${iYellow}${INPUT_PATH}${NC}"
echo -e "Input        :: ${iYellow}${INPUT}${NC}"
echo -e "Input File   :: ${iYellow}${INPUT_FILE}${NC}"
echo -e "Groups Count :: ${iYellow}$(int_fmt $GID_COUNT)${NC}"
echo -e "Users Count  :: ${iYellow}$(int_fmt $UID_COUNT)${NC}"
echo -e "Log File     :: ${iYellow}${LOG_FILE}${NC}"
echo -e "Date Time    :: Local: ${iYellow}$(date)${NC}, UTC: ${iYellow}$(date -u)${NC}"

# echo
# ppwide "$(date) ${TITLE} / Last 25 Executed Commands"
# tail -n 10 ~/.bash_history | nl
