#!/bin/bash

# shellcheck disable=SC1083,SC2001,SC2015,SC2016,SC2028,SC2034,SC2046,SC2059,SC2119,SC2120,SC2128,SC2154,SC2162,SC2178,SC2183,SC2206,SC2207,SC2317
#  SC1083: "This } is literal. Check expression (missing ;/\\n?) or quote it.",
#  SC2001: "See if you can use ${variable//search/replace} instead.",
#  SC2015: "Note that A && B || C is not if-then-else. C may run when A is true.",
#  SC2016: "Expressions don't expand in single quotes, use double quotes for that.",
#  SC2028: "echo may not expand escape sequences. Use printf.",
#  SC2034: "bBlack appears unused. Verify use (or export if used externally).",
#  SC2046: "Quote this to prevent word splitting.",
#  SC2059: "Don't use variables in the printf format string. Use printf '..%s..' \"$foo\".",
#  SC2119: "Use get_fmtdate \"$@\" if function's $1 should mean script's $1.",
#  SC2120: "list_funcs references arguments, but none are ever passed.",
#  SC2128: "Expanding an array without an index only gives the first element.",
#  SC2154: "Ciyan is referenced but not assigned (did you mean 'Cyan'?).",
#  SC2162: "read without -r will mangle backslashes.",
#  SC2178: "Variable was used as an array but is now assigned a string.",
#  SC2183: "This format string has 3 variables, but is passed 1 argument.",
#  SC2206: "Quote to prevent word splitting/globbing, or split robustly with mapfile or read -a.",
#  SC2207: "Prefer mapfile or read -a to split command output (or quote to avoid splitting).",
#  SC2317: "Command appears to be unreachable. Check usage (or ignore if invoked indirectly).",


# Usage: source in target script as shown below - assuming both have the same path
# myDir="$( dirname "$0" )"
# source "${myDir}/incl.sh"

# Unittest:
#   bash incl.sh
MY_SRC="${BASH_SOURCE[0]}"

[ -n "$(which python3)" ] && PY="$(which python3)"
[ -z "$PY" ] && PY="$(which python)"

function log() {
    # usage: export LOGLEVEL=TRACE|DEBUG|INFO|SUCCESS|WARNING|ERROR|CRITICAL ###
    # Local log - colored
    [ "$LOGLEVEL"  ==  "TRACE"    ] && LV=0
    [ "$LOGLEVEL"  ==  "DEBUG"    ] && LV=1
    [ "$LOGLEVEL"  ==  "INFO"     ] && LV=10
    [ "$LOGLEVEL"  ==  "SUCCESS"  ] && LV=20
    [ "$LOGLEVEL"  ==  "WARNING"  ] && LV=30
    [ "$LOGLEVEL"  ==  "ERROR"    ] && LV=40
    [ "$LOGLEVEL"  ==  "CRITICAL" ] && LV=50

    # Default: INFO level 10
    [ -z "$LOGLEVEL" ] && LOGLEVEL='INFO' && LV=10

    lv=$1; lv=$(( lv )); shift
    [[  0 -eq "$lv" && "$lv" -ge "$LV" ]] && echo -e "${Gray}TRACE${NC}: $*" >&2
    [[  1 -eq "$lv" && "$lv" -ge "$LV" ]] && echo -e "${Yellow}DEBUG${NC}: $*" >&2
    [[ 10 -eq "$lv" && "$lv" -ge "$LV" ]] && echo -e "${Green}INFO${NC}: $*" >&2
    [[ 20 -eq "$lv" && "$lv" -ge "$LV" ]] && echo -e "${Green}SUCCESS${NC}: $*" >&2
    [[ 30 -eq "$lv" && "$lv" -ge "$LV" ]] && echo -e "${Red}WARNING${NC}: $*" >&2
    [[ 40 -eq "$lv" && "$lv" -ge "$LV" ]] && echo -e "${Red}ERROR${NC}: $*" >&2 && exit 1
    [[ 50 -eq "$lv" && "$lv" -ge "$LV" ]] && echo -e "${Red}CRITICAL${NC}: $*" >&2 && exit 1
    true
    return
}

function sLog() {
    # usage: export LOGLEVEL=TRACE|DEBUG|INFO|SUCCESS|WARNING|ERROR|CRITICAL ###
    # Sys log - no color
    [ "$LOGLEVEL"  ==  "TRACE"    ] && LV=0
    [ "$LOGLEVEL"  ==  "DEBUG"    ] && LV=1
    [ "$LOGLEVEL"  ==  "INFO"     ] && LV=10
    [ "$LOGLEVEL"  ==  "SUCCESS"  ] && LV=20
    [ "$LOGLEVEL"  ==  "WARNING"  ] && LV=30
    [ "$LOGLEVEL"  ==  "ERROR"    ] && LV=40
    [ "$LOGLEVEL"  ==  "CRITICAL" ] && LV=50

    # Default: INFO level 10
    [ -z "$LOGLEVEL" ] && LOGLEVEL='INFO' && LV=10

    lv=$1; lv=$(( lv )); shift
    [[  0 -eq "$lv" && "$lv" -ge "$LV" ]] && echo -e "TRACE: $*" >&2
    [[  1 -eq "$lv" && "$lv" -ge "$LV" ]] && echo -e "DEBUG: $*" >&2
    [[ 10 -eq "$lv" && "$lv" -ge "$LV" ]] && echo -e "INFO: $*" >&2
    [[ 20 -eq "$lv" && "$lv" -ge "$LV" ]] && echo -e "SUCCESS: $*" >&2
    [[ 30 -eq "$lv" && "$lv" -ge "$LV" ]] && echo -e "WARNING: $*" >&2
    [[ 40 -eq "$lv" && "$lv" -ge "$LV" ]] && echo -e "ERROR: $*" >&2
    [[ 50 -eq "$lv" && "$lv" -ge "$LV" ]] && echo -e "CRITICAL: $*" >&2 && exit 1
    true
    return
}

## Log Local - Color
function iTrace()    { log 0 "$*"; }
function iDebug()    { log 1 "$*"; }
function iInfo()     { log 10 "$*"; }
function iSuccess()  { log 20 "$*"; }
function iWarning()  { log 30 "$*"; }
function iError()    { log 40 "$*"; }
function iCritical() { log 50 "$*"; }    # exit 1

## Log Sys - No Color
function sTrace()    { sLog 0 "$*"; }
function sDebug()    { sLog 1 "$*"; }
function sInfo()     { sLog 10 "$*"; }
function sSuccess()  { sLog 20 "$*"; }
function sWarning()  { sLog 30 "$*"; }
function sError()    { sLog 40 "$*"; }
function sCritical() { sLog 50 "$*"; }   # exit 1

function getExitCode() {
    local ec
    ec="$?"
    if [ 0 -eq "$ec" ]; then
        iDebug "ExitCode: ${Green}${ec}${NC}"
    else
        iWarning "ExitCode: ${Red}${ec}${NC}"
    fi
}

function getDir() {
    # usage: returns current filr & folder data ###
    SOURCE=${BASH_SOURCE[-1]}
    while [ -L "$SOURCE" ]; do
        DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
        SOURCE=$(readlink "$SOURCE")
        [[ $SOURCE != /* ]] && SOURCE=$DIR/$SOURCE # resolve symlink
    done
    DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
    FileName=$(echo "$SOURCE" | tr '/' ' ' | awk '{print $NF}' )
    Name=$( echo "$FileName" | tr '.' ' ' | awk '{print $1}' )
    name=$(echo "$Name" | tr '\_' '-')
    TITLES=$(echo "$Name" | tr '\-\_' ' ')
    for r in $TITLES; do
        Title+="${r^} "
    done
    echo "CWD': $(pwd)"
    echo "Path': $( realpath -e -- "$DIR")"
    echo "File': $SOURCE"
    echo "FileName': $FileName"
    echo "Name': $Name"
    echo "Title: ${Title}"
}

function isCodeBuild() {
    # usage: [ 0 -eq "$( isCodeBuild ) $?" ] && echo "True" || echo "False" ###
    if [ -n "$CODEBUILD_BUILD_NUMBER" ]; then
        true
        return
    else
        false
        return
    fi 
}

function isDebug() {
    # usage: [ 0 -eq "$( isDebug ) $?" ] && echo "True" || echo "False" ###
    if [[ -n "$LOGLEVEL" && "$LOGLEVEL" = "DEBUG" ]]; then
        true
        return
    else
        false
        return
    fi
}

function isTrace() {
    # usage: [ 0 -eq "$( isTrace ) $?" ] && echo "True" || echo "False" ###
    if [[ -n "$LOGLEVEL" && "$LOGLEVEL" = "TRACE" ]]; then
        true
        return
    else
        false
        return
    fi
}

## Print
function wline() {
    # usage: wline ['-' 90 | 90] # print '-' 90 chars lenght ###
    iTrace "L#$(( LINENO - 2 )) :: ${iYellow}${FUNCNAME[0]}()${NC} ${iCyan}${*}${NC}"
    local i len char res
    char='-'
    len=90
    res=''

    # char len
    if [ -n "$2" ]; then
        char="$1"
        len="$2"
    # char or len
    elif [ -n "$1" ]; then
        if [ 0 -eq "$( isInt "$1" ) $?" ]; then
            iDebug "$1 is an integer"
            len="$1"
        else
            iDebug "$1 is not an integer"
            char="$1"
        fi
    fi

    for (( i=0; i<len; i++ )); do
        res="${res}${char}"
    done
    echo "$res"
}

function spc() {
    # usage: spc lenght # returns space to lenght ###
    iTrace "L#$(( LINENO - 2 )) :: ${BASH_LINENO[*]}, ${iYellow}${FUNCNAME[0]}()${NC} ${iCyan}${*}${NC}"
    local len res
    len="$1"
    [ 1 -eq "$(isInt "$len") $?" ] && iTrace "${len} is not an integer!" && return
    while [ ${#res} -lt "${len}" ]; do res=" ${res}"; done
    echo "$res"
}

function print_table() {
    # Usage: [-t "$title"] [-i "$file"] [-l "$lines"] # prints file or lines as tabular data ###
    iTrace "Line: $(( LINENO - 2 )), ${iYellow}${FUNCNAME[0]}()${NC} ${iCyan}${*}${NC}"
    local WIDTH MAX_LINE_WIDTH COUNTER_WIDTH i TITLE FILE LINES MSG line
    WIDTH=132       # Min wline WIdth
    MAX_LINE_WIDTH="$WIDTH"
    COUNTER_WIDTH=5 # row number width
    EXTRA_WIDTH=4   # 4 = +2 for a dot and a space +2 extra
    i=0
    while [ $# -gt 0 ]; do
        case $1 in
            # kwqrgs
            -t|--title)
                TITLE="$2"
                shift;shift;;
            -f|--file)
                FILE="$2"
                shift;shift;;
            -l|--lines)
                LINES="$2"
                shift;shift;;
            *)
                MSG="$1"
                shift
                ;;
        esac
    done

    [ -n "${TITLE}" ] && echo -e "${TITLE}"

    # --file
    if [[ -n "${FILE}" || -f "${FILE}" ]]; then
        MAX_LINE_WIDTH=$( wc -L ${FILE} | awk '{print $1}' )
        MAX_LINE_WIDTH=$(( MAX_LINE_WIDTH + COUNTER_WIDTH + EXTRA_WIDTH ))
        [ "$MAX_LINE_WIDTH" -gt "$WIDTH" ] && WIDTH="$MAX_LINE_WIDTH"
        wline $WIDTH
        i=0
        while read -r line; do
            if [ '#' = "${line:0:1}" ]; then
                echo -e "$( jstr -w $COUNTER_WIDTH -r "")  ${Green}${line}${NC}"
                continue
            fi
            i=$(( i + 1 ))
            echo "$( jstr -w $COUNTER_WIDTH -r "$i"). ${line}"
        done < "$FILE"
        wline $WIDTH
    fi

    # --lines
    if [ -n "${LINES}" ]; then
        # get MAX_LINE_WIDTH
        while read -r line; do
            [ "${#line}" -gt "$WIDTH" ] && WIDTH="${#line}"
        done < <( echo -e "$LINES" )
        WIDTH=$(( WIDTH + COUNTER_WIDTH + EXTRA_WIDTH )) 
        wline $WIDTH
        i=0
        while read -r line; do
            if [ '#' = "${line:0:1}" ]; then
                echo -e "$( jstr -w $COUNTER_WIDTH -r "")  ${Green}${line}${NC}"
                continue
            fi
            i=$(( i + 1 ))
            echo "$( jstr -w $COUNTER_WIDTH -r "$i"). ${line}"
        done < <( echo -e "$LINES" )
        wline $WIDTH
    fi
    [[ -n "${TITLE}" && "$i" -gt 50 ]] && echo -e "${TITLE}" 
}

function ppwide() {
    # Usage: [-b '-'] [-a '-'] [-w int] ['Message'] # prints bbb 'Message' aaa... # to w chars wide ###
    iTrace "L#$(( LINENO - 2 )) :: ${iYellow}${FUNCNAME[0]}()${NC} ${iCyan}${*}${NC}"
    local str before after color width message oneChar sStr
    before=''
    after=''
    str='#'
    width=90
    while [ $# -gt 0 ]; do
        case $1 in
            # options
            -b|--before)
                before="$2"
                shift;shift;;
            -a|--after)
                after="$2"
                shift;shift;;
            -c|--color)
                color="$2"
                shift;shift;;
            -w|--width)
                width="$2"
                shift;shift;;
            *)
                message="$1"
                shift
                ;;
        esac
    done

    width=$(( width - 1 ))
    rep="$(wline '#' "$width")"
    [ -n "$message" ] && str="### $message"
    [ -n "$before" ] && str=${str//#/$before}
    [[ -n "$before" && -z "$after" ]] && after="${before}"
    if [[ -n "$message" && 1 -eq "${#message}" ]]; then
        oneChar=1
        str="$message"
        rep="#${rep}"
        rep="$( echo "$rep" | tr "#" "$str" )"
    elif [ -z "$message" ]; then
        oneChar=1
        rep="#${rep}"
        str='#'
    fi
    [ -n "$before" ] && str=${str//#/$before}
    [ -n "$after" ] && rep=${rep//#/$after}
    sStr=$( echo -e "$str" | sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' )
    iTrace "--before '$before' --after '$after' --color '$color' --width ${width} '${sStr}'"
    if [ -n "${!color}" ]; then
        [ -n "$oneChar" ] && echo -e "${!color}${str}${!color}${rep:${#sStr}}${NC}" || echo -e "${!color}${str} ${!color}${rep:${#sStr}}${NC}"
    else
        [ -n "$oneChar" ] && echo -e "${str}${rep:${#sStr}}" || echo -e "${str} ${rep:${#sStr}}"
    fi
}

function ppwider() {
    ppwide -w 140 "$*"
}

function pyg_lexers() {
    pygmentize -L "lexers" | grep ':' | tr -d '*:,' | tr -d '\n'
}

function pyg_styles() {
    local CMD
CMD="
from pygments.styles import get_all_styles

for style in list(get_all_styles()):
   print(style)
"
    # shellcheck disable=SC2046,SC2005
    echo $( $PY -c "$CMD" | tr '\n' ' ' )
}

function pyg_out() {
    local lang code
    lang='bash'
    # args & kwargs parser

    if [ -n "$2" ]; then
        code="$2"
        lang="$1"
    else
        code="$1"
    fi
    echo "$code" | pygmentize -l "$lang" -O style=monokai
}

# shellcheck disable=SC2304,SC2181,SC2034
AWSV=$( aws --version | grep 'aws-cli/2' )
# shellcheck disable=SC2304,SC2181,SC2034
[ 0 -eq $? ] && AWS_VERSION=2 || AWS_VERSION=1

# which shell
# zsh colors: \033, bash colors: \e
[ -n "$ZSH_VERSION" ] && Esc='\033' || Esc='\e'

# Color Usage:
#     echo -e "${Green}Green Test${NC}"
#     echo -e "${bGreen}Bold Green Test${NC}"
#     echo -e "${iGreen}Italic GreenTest${NC}"
#     echo -e "${uGreen}Underline Green Test${NC}"

# Reset
function set_color() {
    # ussage: set colors for echo -e "..." & printf ###
    # printf colors
    # A hack fix to avoid codebuild terminal error:
    #   tput: No value for $TERM and no -T specified
    if [ -z "$CODEBUILD_BUILD_NUMBER" ]; then
        NORMAL=$(tput sgr0)
        
        BLACK=$(tput setaf 0)
        RED=$(tput setaf 1)
        GREEN=$(tput setaf 2)
        YELLOW=$(tput setaf 3)
        LIME_YELLOW=$(tput setaf 190)
        POWDER_BLUE=$(tput setaf 153)
        BLUE=$(tput setaf 4)
        MAGENTA=$(tput setaf 5)
        CYAN=$(tput setaf 6)
        WHITE=$(tput setaf 7)
        BRIGHT=$(tput bold)
        BLINK=$(tput blink)
        REVERSE=$(tput smso)
        UNDERLINE=$(tput smul)
    fi

    # which shell
    # zsh colors: \033, bash colors: \e
    [ -n "$ZSH_VERSION" ] && Esc='\033' || Esc='\e'

    # Color Usage:
    #     echo -e "${Green}Green Test${NC}"
    #     echo -e "${bGreen}Bold Green Test${NC}"
    #     echo -e "${iGreen}Italic GreenTest${NC}"
    #     echo -e "${uGreen}Underline Green Test${NC}"

    NC="${Esc}[0m"         # Text Reset

    # 0: Normal Colors
    Black="${Esc}[0;30m"      # Black
    Gray="${Esc}[0;90m"       # Gray
    Red="${Esc}[0;91m"        # Red
    Green="${Esc}[0;92m"      # Green
    Yellow="${Esc}[0;93m"     # Yellow
    Blue="${Esc}[0;94m"       # Blue
    Magenta="${Esc}[0;95m"    # Magenta
    Cyan="${Esc}[0;96m"       # Cyan
    White="${Esc}[0;97m"      # White
    # Extended Normal Colors
    Brown="${Esc}[38;5;136m"  # Brown
    Orange="${Esc}[38;5;208m" # Orange
    Lemon="${Esc}[38;5;48m"   # Lemon
    Rose="${Esc}[38;5;160m"   # Rose
    Pink="${Esc}[38;5;200m"   # Pink

    # 1: Bold Colors
    bBlack="${Esc}[1;30m"   # Black
    bGray="${Esc}[1;90m"    # Gray
    bRed="${Esc}[1;91m"     # Red
    bGreen="${Esc}[1;92m"   # Green
    bYellow="${Esc}[1;93m"  # Yellow
    bBlue="${Esc}[1;94m"    # Blue
    bMagenta="${Esc}[1;95m" # Magenta
    bCyan="${Esc}[1;96m"    # Cyan
    bWhite="${Esc}[1;97m"   # White

    # 3: Italic Colors
    iBlack="${Esc}[3;30m"   # Black
    iGray="${Esc}[3;90m"    # Gray
    iRed="${Esc}[3;91m"     # Red
    iGreen="${Esc}[3;92m"   # Green
    iYellow="${Esc}[3;93m"  # Yellow
    iBlue="${Esc}[3;94m"    # Blue
    iMagenta="${Esc}[3;95m" # Magenta
    iCyan="${Esc}[3;96m"    # Cyan
    iWhite="${Esc}[3;97m"   # White

    # 4: Underline Colors
    uBlack="${Esc}[4;30m"   # Black
    uGray="${Esc}[4;90m"    # Gray
    uRed="${Esc}[4;91m"     # Red
    uGreen="${Esc}[4;92m"   # Green
    uYellow="${Esc}[4;93m"  # Yellow
    uBlue="${Esc}[4;94m"    # Blue
    uMagenta="${Esc}[4;95m" # Magenta
    uCyan="${Esc}[4;96m"    # Cyan
    uWhite="${Esc}[4;97m"   # White
}

set_color

function list_colors() {
    local COLORS bCOLORS iCOLORS uiCOLORS
    COLORS=( Black Gray Red Green Yellow Blue Magenta Cyan White )
    eCOLORS=( Brown Orange Lemon Rose Pink )
    bCOLORS=( bBlack bGray bRed bGreen bYellow bBlue bMagenta bCyan bWhite )
    iCOLORS=( iBlack iGray iRed iGreen iYellow iBlue iMagenta iCyan iWhite )
    uCOLORS=( uBlack uGray uRed uGreen uYellow uBlue uMagenta uCyan uWhite )

    ppwide -b '-' "Colors & Styles / ${Yellow}echo${NC} ${Blue}-e${NC}"
    # shellcheck disable=SC2016
    echo -e 'Usage: echo -e "${Blue}Message${NC} ${bBlue}Message${NC} ${iBlue}Message${NC} ${uBlue}Message${NC}"' 
    wline
    w=8
    echo;echo -e -n "Normal    : "
    for COLOR in "${COLORS[@]}"; do
        COLOR_ID=$(jstr -w "${w}" "${COLOR}")
        echo -e -n "${!COLOR}${COLOR_ID}${NC} "
    done
 
    echo;echo -e -n "Extended  : "
    for COLOR in "${eCOLORS[@]}"; do
        COLOR_ID=$(jstr -w "${w}" "${COLOR}")
        echo -e -n "${!COLOR}${COLOR_ID}${NC} "
    done
 
    echo;echo -e -n "Bold      : "
    for COLOR in "${bCOLORS[@]}"; do
        COLOR_ID=$(jstr -w "${w}" "${COLOR}")
        echo -e -n "${!COLOR}${COLOR_ID}${NC} "
    done
 
    echo;echo -e -n "Italic    : "
    for COLOR in "${iCOLORS[@]}"; do
        COLOR_ID=$(jstr -w "${w}" "${COLOR}")
        echo -e -n "${!COLOR}${COLOR_ID}${NC} "
    done
 
    echo;echo -e -n "Underline : "
    for COLOR in "${uCOLORS[@]}"; do
        COLOR_ID=$(jstr -w "${w}" "${COLOR}")
        echo -e -n "${!COLOR}${COLOR_ID}${NC} "
    done
    echo
    echo -e "Reset     : NC"
    
    # printf
    echo
    ppwide -b '-' "Colors & Styles / ${Yellow}printf${NC}"
    # shellcheck disable=SC2016,SC2028
    echo 'Usage: printf '%s\\n' ${STYLE}${COLOR}Message${NORMAL}' 
    # shellcheck disable=SC2016,SC2028
    echo 'Usage: printf '%s\\n' ${COLOR}Message${NORMAL} # if no STYLE given defaults to NORMAL' 
    wline

    local PCOLORS PSTYLES COL_WIDTH SPC COL_DATA
    PSTYLES=( NORMAL BRIGHT BLINK REVERSE UNDERLINE )
    PCOLORS=( BLACK RED GREEN YELLOW LIME_YELLOW POWDER_BLUE BLUE MAGENTA CYAN WHITE )
    COL_WIDTH="%-9s : %s\n"

    printf "$COL_WIDTH" "Style" "Colors for printf"
    wline

    SPC='  '
    for STYLE in "${PSTYLES[@]}"; do
        COL_DATA=''
        for COLOR in "${PCOLORS[@]}"; do
            COLOR_ID="${COLOR}"
            COL_DATA="${COL_DATA}${SPC}${!STYLE}${!COLOR}${COLOR_ID}${NORMAL}"
        done
        printf "$COL_WIDTH" "$STYLE" "$COL_DATA"
    done

    echo -e "Reset     : NORMAL" 
}

function ansi_colors() {
    local i iStr
    for i in {0..255}; do
        iStr=$(ndigits "$i")
        echo -e -n "${Esc}[38;5;${i}m ${iStr}. Test ${NC}"
        [[ 0 -eq $(( i % 8 )) ]] && echo
    done
    echo
}

### Str, Int & Array
function clean_path() {
    # usage: returns removed '../' from middle of given absolute path###
    path="$1"
$PY -c "
path = '$1'
paths = path.split('/')

while '..' in paths:
    if paths[0] == '..': break
    for i, path in enumerate(paths):
        if path == '..' and i > 0:
            try:
                paths.pop( i )
                paths.pop( i - 1 )
            except Exception:
                pass


res = '/'.join(paths)

print(res)
"
}

function fmtInt() {
    # usage: int [decimal] returns thousands comma separated int [with given decimal] ###
    local num decimal
    num="$1"
    [ -n "$2" ] && decimal="$2" || decimal=0
    $PY -c "num=$num;decimal=$decimal;print(f'{num:,.{decimal}f}')"
}

function dedent() {
    # usage: returns remove leading spaces of input lines ###
    echo "$1" | sed 's/^[[:space:]]*//'
}

function int_fmt() {
    # usage: print $int with thousands separator ###
    [ 0 -eq "$(isInt "$1") $?" ] && $PY -c "num=$1;print(f'{num:,}')"
}

function s2n() {
    # usage: returns one char per line for ascii value of all chars input ###
    printf '%s' "$1" | awk -l ordchar -v RS='.{1}' '{s+ord(RT)} END{print s+0}'
}

function inarr() {
    # usage: [ 0 -eq "$( inarr "needle" "${arr[@]}" ) $?" ] && echo "True" || echo "False" ###
    local ne arr
    ne=$1; shift
    # shellcheck disable=SC2206
    arr=( $* )
    for k in "${arr[@]}";do
        if [ "$k" = "$ne" ]; then
            true
            return
        fi
    done
    false
    return
}

function isInt() {
    # usage: [ 0 -eq "$(isInt "$chk") $?" ] && echo true || echo false ###
    iTrace "L#$(( LINENO - 2 )) :: ${iYellow}${FUNCNAME[0]}()${NC} ${iCyan}${*}${NC}"
    if [[ "$1" =~ ^[0-9]+$ ]]; then
        iTrace "$1 is an integer"
        true
        return
    else
        iTrace "$1 is not an integer!"
        false
        return
    fi
}

function title_case() {
    # usage: "$text" # returns Title Case ###
    iTrace "L#$(( LINENO - 2 )) :: ${iYellow}${FUNCNAME[0]}()${NC} ${iCyan}${*}${NC}"
    "$PY" -c "print('$*'.title())"
}

function ltrim() {
    # usage: returns right trimed ###
    # shellcheck disable=SC2317
    echo "$*" | sed 's/^ *//'
}

function ltrim() {
    # usage: returns left trimed ###
    echo "$*" | sed 's/ *$//'
}

function trim() {
    # usage: returns left & right trimed whitespace ###
    # echo "$*" | sed 's/^ *//' | sed 's/ *$//' 
    echo "$*" | awk '{$1=$1};1'
}

function strip() {
    # usage: returns left & right trimed whitespace ###
    echo "$*" | awk '{$1=$1};1'
}

function prcnt() {
    # usage: percent 5.2 10 # returns 52.00% ###
    local chk total res
    chk="$1"
    total="$2"
    $PY -c "print(float(format($chk/$total*100, '.2f')))"
}

function get_maxlen() {
    # usage: get_maxlen "abc "abc abcdf abcdef" # returns 6 ###
    local maxLen ele
    maxLen=0
    for ele in $1; do
        [[ "${#ele}" -ge "$maxLen" ]] && maxLen=${#ele}
    done
    return "$maxLen"
}

function camel2() {
    # usage: [-|_] "$CamelCase" # - returns spinal case, _ returns snake case ###
    local r="$1"
    local str="$2" 
local CMD="
res = ''
str = '$str'
for i in str:
    if i.isupper(): res += '$r'
    res += i.lower()
print(res[1:])
"
    "$PY" -c "$CMD"
}

function snake2camel() {
    # usage: snake_text_to_test # returns SnakeTextToTest ###
    "$PY" -c "print('$1'.replace('-',' ').replace('_',' ').title().replace(' ',''))"
}

function spinal2camel() {
    # usage: spinal-text-to-test # returns SpinalTextToTest ###
    "$PY" -c "print('$1'.replace('-',' ').replace('_',' ').title().replace(' ',''))"
}

function camel2snake() {
    # usage: SnakeTextToTest # returns snake_text_to_test ###
    camel2 '_' "$1"
}

function camel2spinal() {
    # usage: SpinalTextToTest # returns spinal-text-to-test ###
    camel2 '-' "$1"
}

function snake2title() {
    # usage: snake_text_to_test # returns Snake Text To Test ###
    "$PY" -c "print('$1'.replace('-',' ').replace('_',' ').title())"
}

function spinal2title() {
    # usage: spinal-text-to-test # returns Spinal Text To Test ###
    "$PY" -c "print('$1'.replace('-',' ').replace('_',' ').title())"
}

function ndigits() {
    # usage: ndigits "int" [digits] # echo left zero str ###
    iTrace "L#$(( LINENO - 2 )) :: ${iYellow}${FUNCNAME[0]}()${NC} ${iCyan}${*}${NC}"
    local int digits
    int="$1"
    digits=3
    [ -n "$2" ] && digits="$2" && shift;
    [ "${#int}" -gt "$digits" ] && echo "$int" && return
    for (( i=${#int};i<$digits; i++ )); do
        int="0${int}"
    done
    echo "$int"
}

function press_any_key() {
    read -n 1 -s -r -p "Press any key to continue ... "
}

function goNoGoCheck() {
    # usage: [$message] # shows a message and waits for user y/n input then retunes 0 for go ###
    local message key
    message='Do you want to proceed'
    [ -n "$1" ] && message="$1"
    read -n 1 -s -r -p "${message}? Y/n " key
    if [ 'y' = "$key" ] || [ 'Y' = "$key" ]; then
        echo 0
    else
        echo 1
    fi
}

function goNoGo() {
    # usage: shows Go/no-go message and waits for user y/n input ###
    local key
    read -n 1 -s -r -p "Do you want to proceed? Y/n " key
    echo
    if [ 'y' = "$key" ] || [ 'Y' = "$key" ]; then
        true
        return
    else
        exit 1
    fi
}

function is_int() {
    # usage: [ 0 -eq "$( is_int ) $?" ] && echo "True" || echo "False" ###
    isInt "$*"
}

function jstr-help() {
        echo "Justify String"
        wline
        echo "args:"
        echo "  -h              show this help and exit"
        echo "  -c --center     center align"
        echo "  -l --left       left align, default"
        echo "  -r --right      right align"
        echo "  -w --width      final width"
}

function jstr() {
    # usage [-l|-c|-r] -w "int" "Message" # return justified to -w lenght ### 
    local args align width str
    iTrace "Given: $*"
    args=()
    align='left'
    while [ $# -gt 0 ]; do
        case "$1" in
        ### start custom parameter checks
            -l|--left)
                align='left'
                shift;;
            -c|--center)
                align='center'
                shift;;
            -r|--right)
                align='right'
                shift;;
            -w|--width)
                width="$2"
                shift;shift;;
        ### end custom parameter checks
            -h|--help)
                jstr-help
                return;;
            -|--)
                while [ $# -gt 0 ]; do args+=("$1"); shift; done;
                break;;
            --*)
                echo "**Bad parameter: $1**" >&2
                jstr-help
                exit 1
                ;;
            *)
                str="$1"
                args+=("$1");
                shift;;
        esac
    done

    iTrace "Print: ${Green}--width ${width}${NC} ${Blue}--${align}${NC} ${Yellow}${str}${NC}"
    [ -z "$width" ] && iTrace "Missing required arg -w or --width" && exit 1

    # process
    if [ 'left' = "$align" ]; then
        while [ ${#str} -lt "$width" ]; do str="$str "; done
        iTrace "${Blue}'${str}'${NC}"
    elif [ 'center' = "$align" ]; then
        while [ "${#str}" -lt "$width" ]; do str=" $str "; done
        iTrace "${Green}'${str}'${NC}"
    elif [ 'right' = "$align" ]; then
        while [ ${#str} -lt "$width" ]; do str=" $str"; done
        iTrace "${Red}'${str}'${NC}"
    fi
    echo "${str}"
}

## Date, Time
function get_dt() {
    date +%FT%R:%S.%6N
}

function get_ts() {
    # Formats: +%s.%3N +%s.%6N +%s.%9N +%s.%12N or +%s.%N
    date +%s.%6N
}

function iso_dt() {
    date +%Y-%m-%dT%H:%M:%S%:z
}

function took_ts() {
    if [ -n "$1" ]; then
        local ts now took
        ts=$1
        now="$( date +%s.%6N )"
        $PY -c "print(float(format($now - $ts, '.6f')))"
    fi
}

function demo_ts() {
    local ts took
    ts=$( get_ts )
    sleep 0.234567
    took=$( took_ts "${ts}" )
    echo "${took}"
}

function get_fmtdate() {
    # usage: [-f] # returns full human readable date with -f, or prints brief data ###
    [ -n "$1" ] && date '+%A %d %B %Y  %H:%M:%S.%3N %z %Z' || date '+%a %d-%b-%Y  %H:%M:%S'
}

function dt2ts() {
    date --date="${1}" +"%s"
}

function ts2dt() {
    date -d "@${1}" +%FT%R:%S%:z
}

function timeit() {
    echo "$( get_ts ) ${1}"
}

function timedelta_mhsm() {
    secs="${1}"
    # shellcheck disable=SC2046,SC2183
    printf '%02d:%02d:%06.3f\n' $($PY -c "print(int($secs/3600));print(int($secs%3600/60));print(float(format($secs%60,'.6f')))")
}

function set_timer() {
    [ ! -r "$TIMER_FILE" ] && TIMER_FILE=$( mktemp  )
    echo "$( get_ts ) ${1}" >> "${TIMER_FILE}"    
}

function rm_timer() {
    rm -rf "${TIMER_FILE}"
}

function get_timer() {
    # usage: [width] # int of table width, default 90 ### 
    [ ! -r "${TIMER_FILE}" ] && return
    local tsArr=()
    local width=132
    [ -n "$1" ] && width="$1"
    while read -r line; do 
        tsArr+=( "${line}" )
    done < "${TIMER_FILE}"

    local total=0
    local i=0

    local HEAD_COLS="%3s %-15s %-12s %-s\n"
    local ROWS_COLS="%3s %-15s %-12s %-s\n"
    local FOOT_COLS="%3s %-15s %-12s %-s\n"

    local old_ts=0
    local t=''
    local cur_ts=0
    local desc=''
    local took=0
    local total=0
    local took_str=''
    local total_str=''
    # shellcheck disable=SC2059
	printf "$HEAD_COLS" " " "Took" "Total Time" "Description"
    wline "$width"
    for t in "${tsArr[@]}"; do
        # shellcheck disable=SC2004
        i=$(( $i+1 ))
        cur_ts=$( echo "${t}" | awk '{ print $1 }' )
        desc=$( echo "${t}" | awk '{$1=""; print $0}' )
        [ 1 -eq "$i" ] && old_ts="${cur_ts}"    # for first is init with 0 time elapsed
        
        took=$( $PY -c "print($cur_ts - $old_ts)" )
        total=$( $PY -c "print($total + $took)" )

        took_str=$( timedelta_mhsm "$took" )
        total_str=$( timedelta_mhsm "$total" )

        # shellcheck disable=SC2059
	    printf "$ROWS_COLS" "${i}." "$took_str" "$total_str" "${desc}"
        old_ts=$( echo "${t}" | awk '{ print $1 }') # last ts woud be start of next duration 
    done
    # shellcheck disable=SC2059
    wline "$width"
	printf "$HEAD_COLS" " " "Took" "Total Time" "Description"
    wline "$width"
    printf "$FOOT_COLS" " " "$total_str" "$total_str" " "
}

### AWS
function boto2cli() {
    # boto2cli [securityhub] get_administrator_account -> [securityhub] get-administrator-account
    [ -n "$2" ] && echo -n "${1,,} " && shift
    echo "$1" | tr '_' '-'
}

function boto2iam() {
    # boto2iam [securityhub] get_administrator_account -> [securityhub:]GetAministratorAccount
    [ -n "$2" ] && echo -n "${1,,}:" && shift
    snake2camel "$1"
}

function cli2boto() {
    # cli2boto get-administrator-account -> get_administrator_account
    [ -n "$2" ] && shift
    echo "$1" | tr '-' '_'
}

function cli2iam() {
    # cli2iam [securityhub] get-administrator-account -> [securityhub:]GetAministratorAccount
    [ -n "$2" ] && echo -n "${1,,}:" && shift
    spinal2camel "$1"
}

function iam2boto() {
    # iam2boto [securityhub:]GetAministratorAccount -> [securityhub ]get_administrator_account
    local arg svc
    arg="$1"
    if [[ "$1" == *":"* ]]; then
        svc=$( echo "${1,,}" | tr ':' ' ' | awk '{print $1}' )
        arg=$( echo "$1" | tr ':' ' ' | awk '{print $2}' )
        iTrace "svc: $svc"
        iTrace "arg: $arg"
        echo -n "$svc " 
    fi
    camel2snake "$arg"
}

function iam2cli() {
    # iam2cli [securityhub:]GetAministratorAccount -> [aws securityhub ]get-administrator-account
    local arg svc
    arg="$1"
    if [[ "$1" == *":"* ]]; then
        svc=$( echo "${1,,}" | tr ':' ' ' | awk '{print $1}' )
        arg=$( echo "$1" | tr ':' ' ' | awk '{print $2}' )
        iTrace "svc: $svc"
        iTrace "arg: $arg"
        echo -n "aws $svc " 
    fi
    camel2spinal "$arg"
}

function test_aws_cnv() {
    # Print help for AWS Conversions of Boto3, CLI & IAM with examples 
    local width svc sBoto sCli sIam i client session
    width=132 
    svc='securityhub'
    sBoto='get_administrator_account'
    sCli='get-administrator-account'
    sIam='GetAdminstratorAccount'

    local HEAD_COLS='%-4s %-10s %-50s %-50s\n'
    local ROWS_COLS=' %3d %-10s %-50s %-50s\n'

    echo
    echo "Data Model Brief"
    wline $width
    echo -e "${Yellow}Service${NC} : ${Orange}${svc}${NC}"
    echo -e "${Yellow}Boto3${NC}   : ${Lemon}${sBoto}${NC}"
    echo -e "${Yellow}CLI${NC}     : ${Lemon}${sCli}${NC}"
    echo -e "${Yellow}IAM${NC}     : ${Lemon}${sIam}${NC}"

    echo
    echo "Data Model Usage"
    wline $width
    echo -e "${Blue}Boto3 in Python${NC}"
    wline $width
    echo -e "${Cyan}session${NC} = ${Green}boto3${NC}.${Green}Session()${NC}"
    echo -e "${Cyan}client${NC} = ${Green}boto3${NC}.${Yellow}client(${Orange}'${svc}'${NC}${Yellow})${NC}"
    echo -e "${Cyan}response${NC} = ${Cyan}client${NC}.${Lemon}${sBoto}${NC}(${Cyan}**args${NC}, ${Cyan}**kwargs${NC})"

    echo
    echo -e "${Blue}CLI in Terminal, bash, zsh & PS${NC}"
    wline $width
    echo -e "${Yellow}aws${NC} ${Orange}${svc}${NC} ${Lemon}${sCli}${NC} [args] [kwargs]"

    echo
    echo -e "${Blue}IAM in JSON & YAML${NC}"
    wline $width
    echo -e "${Orange}${svc}${NC}:${Lemon}${sIam}${NC}"

    echo
    printf "$HEAD_COLS" "" "Function" "Input" "Output"
    wline $width
    printf "$ROWS_COLS" "$(( ++i ))" "cli2boto" "${sCli}" "$(cli2boto ${sCli})"
    printf "$ROWS_COLS" "$(( ++i ))" "cli2iam" "${svc} ${sCli}" "$(cli2iam ${svc} ${sCli})"
    printf "$ROWS_COLS" "$(( ++i ))" "iam2boto" "${svc}:${sIam}" "$(iam2boto ${svc}:${sIam})"
    printf "$ROWS_COLS" "$(( ++i ))" "iam2cli" "${svc}:${sIam}" "$(iam2cli ${svc}:${sIam})"
    wline $width
    
    echo
    echo "Usage:"
    wline $width
    echo "boto2cli   get_administrator_account"
    echo "boto2iam   securityhub get_administrator_account"
    echo "cli2boto   get-administrator-account"
    echo "cli2iam    securityhub get-administrator-account"
    echo "iam2boto   GetAdminstratorAccount"
    echo "iam2boto   securityhub:GetAdminstratorAccount"
    echo "iam2cli    securityhub:GetAdminstratorAccount"
}

## Functions
function list_funcs() {
    # usage: returns list of functions to review highlighted code, LoC, Start & End Line Numbers ###
    iTrace "L#$(( LINENO - 2 )) :: ${iYellow}${FUNCNAME[0]}()${NC} ${iCyan}${*}${NC}"
    local h scope FFILT FUNCS FUNC LINES GREP TOP BOT CNT TAIL HEAD LOC CODE PS3 HIST

    scope='local'
    FFILT='gawklibpath_append|gawklibpath_default|gawklibpath_prepend|gawkpath_append|gawkpath_default|gawkpath_prepend|quote_readline'
    for arg in "$@"; do
        [ '-h' = "$arg" ] && h=0
        [ '-a' = "$arg" ] && scope='all'
        [ '-l' = "$arg" ] && scope='local' # default
        [ '-s' = "$arg" ] && scope='sys'
        [ '--help' = "$arg" ] && h=0
        [ '--all' = "$arg" ] && scope='all'
        [ '--local' = "$arg" ] && scope='local'
        [ '--sys' = "$arg" ] && scope='sys'
    done

    if [ -n "$h" ]; then
        echo "List functions"
        wline
        echo "args:"
        echo "  -h --help   show this help and exit"
        echo "  -a --all    list all functions"
        echo "  -l --local  list local functions only, default local"
        echo "  -s --sys    list system functions only"
        return
    fi

    declare -F FUNCS
    if [ 'all' = "$scope" ]; then
        FUNCS=$( declare -F | awk '{print $3}' )
    elif [ 'sys' = "$scope" ]; then
        FUNCS=$( declare -F | awk '{print $3}' | grep '^_' )
    elif [ 'local' = "$scope" ]; then
        FUNCS=$( declare -F | awk '{print $3}' | grep -v '^_' | grep -E -v "$FFILT" )
    fi

    FUNCS=($( echo "Quit Clear ${FUNCS}" | tr '\n' ' ' ))
    CNT="${#FUNCS[@]}"
    CNT=$(( CNT - 2 ))
    SCOPE=$(title_case "$scope")
    # shellcheck disable=SC2145
    iTrace "Quit + Functions (${CNT}) ${SCOPE}: ${FUNCS[@]}" 

    declare -a HIST
    while [ 'Quit' != "$FUNC" ]; do
        echo -e "${CNT} ${SCOPE} Functions. 1) Quit, 2) Clear History, 3-${#FUNCS[@]}) Functions"
        wline
        local PS3
        PS3='Select 1 to Quit. Select a function to review #? '
        PS3=$'\e[0;93mSelect\e[0;0m a function to review its \e[0;93mcode\e[0;0m. \e[0;93mSelect\e[0;0m \e[0;91m1\e[0;0m to \e[0;93mQuit\e[0;0m. #? '
        select FUNC in "${FUNCS[@]}"; do
            case $FUNC in
                "$FUNC") break ;;
                *) exit ;;
            esac
        done

        # https://pygments.org/languages/
        # -l c++
        [ 'Clear' = "$FUNC" ] && HIST=() && iInfo "Cleaned up Review History!" && continue
        if [ 'Quit' != "$FUNC" ]; then
            i=0
            for iFunc in "${FUNCS[@]}"; do
                i=$(( i + 1 ))
                [ "$iFunc" = "$FUNC" ] && break
            done

            iTrace "MY_SRC : ${MY_SRC}"
            # shellcheck disable=SC2002
            LINES=$( cat "$MY_SRC" | wc -l | awk '{print $1}' )
            iDebug "LINES : $LINES"

            GREP="^function ${FUNC}()"
            iDebug "GREP  : $GREP"
            [ -z "$FUNC" ] && iWarning "Out of range input! Quitting!" && break

            # shellcheck disable=SC2002
            TOP=$( cat "$MY_SRC" | grep -n "${GREP}" | tr ':' ' ' | awk '{print $1}' )
            iDebug "TOP   : $TOP"
            BOT=0
            while read -r LINE; do
                BOT=$(( BOT + 1 ))
                [ "$BOT" -lt "$TOP" ] && continue
                [ '}' = "$LINE" ] && break
            done < "$MY_SRC"
            iDebug "BOT   : $BOT"
            TAIL=$(( LINES - TOP + 1 ))
            HEAD=$(( BOT - TOP + 1 ))
            LOC="$HEAD"
            iDebug "TAIL  : $TAIL"
            iDebug "HEAD  : $HEAD"
            # shellcheck disable=SC2002
            CODE=$( cat "$MY_SRC" | tail -${TAIL} | head -${HEAD} )

            HIST+=( ${i}.${FUNC} )
            ppwide "Line ${Gray}#${TOP}-${BOT}${NC}, ${Gray}${LOC}${NC} LoC, #${i}. ${Cyan}function${NC} ${Yellow}${FUNC}()${NC}"
            pyg_out "$CODE"
            ppwide "Line ${Gray}#${TOP}-${BOT}${NC}, ${Gray}${LOC}${NC} LoC, #${i}. ${Cyan}function${NC} ${Yellow}${FUNC}()${NC}"
            i=0
            # shellcheck disable=SC2145
            echo -e "${Blue}Review History${NC}: ${Green}${HIST[@]}${NC}"
            press_any_key
            echo
        fi
    done
}

### AWS
function awspf() {
    # Print AWS profiles name, arn, expiration & default region ###
    grep -A 8 "^\[.*\]" < ~/.aws/credentials \
        | grep "\[.*\]\|x_security_token_expires\|x_principal_arn\|region\|^$"
}

function is_aws_profile_expired() {
    # usage: [ 0 -eq "$(is_aws_profile_expired "$chk") $?" ] && echo true || echo false ###
    local chk_dt cur_dt cur_ts chk_ts
    iTrace "${Blue}function${NC} ${Yellow}${FUNCNAME[0]}()${NC}"
    iTrace "AWS_PROFILE: $1"
    chk_dt=$( cat ~/.aws/credentials | grep "\[$1\]" -A 7 | grep 'x_security_token_expires' |  awk '{print $3}' )
    iTrace "chk_dt: $chk_dt"
    [ -z "$chk_dt" ] && iWarning "Unable to find AWS Profile ... '$1'!"
    chk_ts=$( date --date="${chk_dt}" +"%s" )
    iTrace "chk_ts: $chk_ts"
    cur_dt=$( iso_dt )
    iTrace "cur_dt: $cur_dt"
    cur_ts=$( date --date="${cur_dt}" +"%s" )
    iTrace "cur_ts: $cur_ts"
    [ "$cur_ts" -gt "$chk_ts" ] && true || false
    return
}

function is_aws_profile_match() {
    # usage: cleanup if aws & $1 'yaml' match else cleanup assumed roles ###
    local YML_FILE PRIMARY_ROLE_AWS PRIMARY_ROLE_YML
    YML_FILE="$1"

    [ ! -f "$YML_FILE" ] && iError "Given Profile set is not exist!" && return

    PRIMARY_ROLE_AWS=$(awspf | head -1 | tr -d '[]')
    # shellcheck disable=SC2086
    PRIMARY_ROLE_YML=$(cat $YML_FILE | grep -A2 primary_role_arn | head -2 | tail -1 | awk '{print $2'})
    
    iInfo "PRIMARY_ROLE_AWS : $PRIMARY_ROLE_AWS"
    iInfo "PRIMARY_ROLE_YML : $PRIMARY_ROLE_YML"

    # shellcheck disable=SC2086
    [ 'profile:' = "$PRIMARY_ROLE_YML" ] && PRIMARY_ROLE_YML=$(cat $YML_FILE | grep -A2 primary_role_arn | head -2 | tail -1 | awk '{print $3'})
    
    iInfo "PRIMARY_ROLE_AWS : $PRIMARY_ROLE_AWS"
    iInfo "PRIMARY_ROLE_YML : $PRIMARY_ROLE_YML"

    if [ "$PRIMARY_ROLE_AWS" != "$PRIMARY_ROLE_YML" ]; then
        ppwide -b '-' "${Red}Clean-up AWS Credentials${NC}"
        # echo '' > ~/.aws/credentials
    else
        iWarning "New Profile Set AWS vs. YML: ${Blue}${PRIMARY_ROLE_AWS}${NC} ${Red}${PRIMARY_ROLE_YML}${NC}"
        ppwide -b '-' "${Red}Csleans-up AWS Assumed Roles${NC}"
        sed '1,9!d' ~/.aws/credentials > ~/.aws/credentials.tmp
        cat ~/.aws/credentials.tmp > ~/.aws/credentials
        rm ~/.aws/credentials.tmp  
    fi
}

function is_cur_aws_profile_expired() {
    # print info
    local chk exp secs cur_dt cur_ts chk_dt chk_ts
    iTrace "${Blue}function${NC} ${Yellow}${FUNCNAME[0]}()${NC}"
    iTrace "Current AWS_PROFILE: $AWS_PROFILE"
    is_aws_profile_expired "${AWS_PROFILE}"
    chk="$?"
    iTrace "chk: $chk"
    [ -z "$AWS_PROFILE" ] && iWarning "Currently no AWS Profile was set!"
    [ -z "$AWS_PROFILE" ] && return

    [ 0 -eq "$chk" ] && iWarning "AWS Profile '${AWS_PROFILE}' is Expired!"
    
    if [ 1 -eq "$chk" ]; then
        chk_dt=$( aws_profile_expiration "${AWS_PROFILE}" )
        dt_exp=$( date --date="${chk_dt}" '+%H:%M:%S %z %Z' )
        iInfo "Current AWS Profile ${Blue}'${AWS_PROFILE}'${NC} Expires on ${Red}${dt_exp}${NC}"

        cur_dt=$( iso_dt )
        cur_ts=$( date --date="${cur_dt}" +"%s" )
        chk_ts=$( date --date="${chk_dt}" +"%s" )
        secs=$(( chk_ts - cur_ts ))
        iTrace "secs: $secs"
        exp=$( sec_disp "$secs" )
        iInfo "Current AWS Profile ${Blue}'${AWS_PROFILE}'${NC} Expires in ${exp}"
    fi
    return
}

function sec_disp {
    local secs d a h m s
    iTrace "${Blue}function${NC} ${Yellow}${FUNCNAME[0]}()${NC}"
    secs=$1
    d=$((secs/60/60/24))
    iTrace "Day: $d"
    h=$((secs/60/60%24))
    iTrace "Hour: $h"
    m=$((secs/60%60))
    iTrace "Minute: $m"
    s=$((secs%60))
    iTrace "Seconds: $s"
    [ "$d" -gt 0 ] && a=1 && echo -en "${Red}${d} Days ${NC}"
    [ "$h" -gt  0 ] && a=1 && echo -en "${Red}${h} Hours ${NC}"
    [ "$m" -gt 0 ] && a=1 && echo -en "${Red}${m} Minutes ${NC}"
    [ -n "$a" ] && echo -en "${Red}&${NC} "
    echo -e "${Red}${s} Seconds${NC}"
}

function aws_profile_expiration() {
    # returns expiation date of $1 profile
    local chk_dt
    iTrace "${Blue}function${NC} ${Yellow}${FUNCNAME[0]}()${NC}"
    chk_dt=$( cat ~/.aws/credentials | grep "\[${1}\]" -A 7 | grep 'x_security_token_expires' |  awk '{print $3}' )
    [ -z "$chk_dt" ] && iWarning "Unable to find AWS Profile '${1}'!"
    echo "${chk_dt}"
}

function is_expired() {
    local cur_dt cur_ts chk_ts
    iTrace "${Blue}function${NC} ${Yellow}${FUNCNAME[0]}()${NC}"
    cur_dt=$( iso_dt )
    cur_ts=$( date --date="${cur_dt}" +"%s" )
    chk_ts=$( date --date="${1}" +"%s" )
    [ "$cur_ts" -gt "$chk_ts" ] && true || false
    return
}

### Unittest
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    ppwide "UNITTEST / ${0}"
    cDate=$( get_fmtdate )
    echo "Current Date : ${cDate}"

    # Start Timer
    set_timer "From $( get_fmtdate )"

    # Task
    echo
    ppwide "${Green}UNITTEST${NC} / Demo Print Wide Line"
    ppwide
    ppwide "Test"
    ppwide '-'
    ppwide '='
    set_timer "UNITTEST / Demo Print Wide Line"

    echo
    ppwide "${Green}UNITTEST${NC} / Demo Colors"
    ansi_colors
    list_colors
    # printf colors demo
    echo
    ppwide "Colors for printf"
    # shellcheck disable=SC2016,SC1012
    echo 'Usage: printf '%s\n' "${COLOR}Message${NORMAL}"'
    wline
    printf  'Normal    : %s\n' "${BLACK}BLACK${NORMAL}  ${RED}RED${NORMAL}  ${GREEN}GREEN${NORMAL}  ${YELLOW}YELLOW${NORMAL}  ${LIME_YELLOW}LIME_YELLOW${NORMAL}  ${POWDER_BLUE}POWDER_BLUE${NORMAL}  ${BLUE}BLUE${NORMAL}  ${MAGENTA}MAGENTA${NORMAL}  ${CYAN}CYAN${NORMAL} ${WHITE}WHITE${NORMAL}"
    printf  'Style     : %s\n' "       ${BLINK}BLINK${NORMAL}  ${REVERSE}REVERSE${NORMAL}  ${UNDERLINE}UNDERLINE${NORMAL}"
    echo -e "Reset     : NORAML"
    set_timer "UNITTEST / Demo Colors"

    # Task
    echo
    ppwide "UNITTEST / Demo TS"
    ts=$( demo_ts )
    ts_fmt=$( timedelta_mhsm "${ts}" )
    echo "ts     : ${ts}"
    echo "ts fmt : ${ts_fmt}"
    set_timer "UNITTEST / Demo TS"

    # Task
    echo
    ppwide "UNITTEST / Demo Local Console Log Message / Colored"
    iTrace "trace message"
    iDebug "debug message"
    iInfo "info message"
    iSuccess "success message"
    iWarning "warnign message"
    set_timer "Demo Local Console Log Message / Colored"

    # Task
    echo
    ppwide "UNITTEST / Demo System Console Log Message"
    sTrace "trace message"
    sDebug "debug message"
    sInfo "info message"
    sSuccess "success message"
    sWarning "warnign message"
    set_timer "Demo System Console Log Message"

    echo
    ppwide "UNITTEST / Demo AWS Call Convertor"
    test_aws_cnv
    set_timer "Demo AWS Call Convertor"


    set_timer "Upto $( get_fmtdate )"

    # Timing Summary from file
    echo
    ppwide "UNITTEST / Demo Timer Summary Report / From File"
    get_timer

    # Cleanup Timer temp file
    rm_timer

    # list_funcs - run for review
    list_funcs

    # list_funcs - report only
    echo 'list_funcs --help'
    list_funcs --help

    echo
    echo -e "To learn more about list_funcs & other functions review ${iYellow}${BASH_SOURCE[0]}${NC}"

fi
