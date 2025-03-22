#!/bin/bash

# Process Logical Segregation Report

myDir="$( dirname "$0" )"
source "${myDir}/incl.sh"

export DATAFOLDER='/tmp/oneidm'

TITLE="GR2-0 / CoreTech ${GREEN}Logical Segregation Report${NORMAL}"
ppwide "$(date) ${TITLE}" 

echo
echo -e "Select Execution Options"
wline

# Go/no-go Check - Cleanup /tmp/oneidm
GO_CLN=$(goNoGoCheck "1. Do you want to clean ${DATAFOLDER}")
echo

# Go/no-go Check - Commercial
GO_COM=$(goNoGoCheck "2. Do you want to run Commercial report")
echo

# Go/no-go Check - GovCloud
GO_GOV=$(goNoGoCheck "3. Do you want to run GovCloud Report")
echo

iDebug "GO_CLN :: $GO_CLN"
iDebug "GO_COM :: $GO_COM"
iDebug "GO_GOV :: $GO_GOV"

echo
echo -e "Selected Execution Options"
wline
[ 0 -eq "$GO_CLN" ] && echo -e "${Green}KEEP${NC} 1. Clean ${DATAFOLDER}"  || echo -e "${Yellow}SKIP 1. Clean ${DATAFOLDER}${NC}"
[ 0 -eq "$GO_COM" ] && echo -e "${Green}KEEP${NC} 2. Run Commercial Report" || echo -e "${Yellow}SKIP 2. Commercial Report${NC} "
[ 0 -eq "$GO_GOV" ] && echo -e "${Green}KEEP${NC} 3. Run GovCloud Report" || echo -e "${Yellow}SKIP 3. Run GovCloud Report${NC}"
wline

# Go/no-go - Final
goNoGo
echo

# Clean 'DATAFOLDER' folder
[ 0 -eq "$GO_CLN" ] && rm -r "$DATAFOLDER"

### I. Get IAM Roles Trust Relationship / Commercial
# Commercial › Setting › Run from whodat dir
if [ 0 -eq "$GO_COM" ]; then
    export AWS_PROFILE=GEAdmin
    export DATAFOLDER='/tmp/oneidm'
    export INPUT='gect-sox-com'
    export INPUT_FILE="inputs/${INPUT}.tab"
    export LOG_FILE="${DATAFOLDER}/${INPUT}.log"
    export LOG_BASH="${DATAFOLDER}/${INPUT}.sh.log"
    export SED_FILT='s/\x1b\[[0-9;]*[a-zA-Z]//g'  # Filter Colors

    # 1. Commercial › Setting › Gos3 Login
    gos3 mmp | tee $LOG_BASH

    # 2. Commercial › Check & Validate Input
    ./oneidm-explorer.sh --input $INPUT | tee $LOG_BASH

    # 3. Commercial › Process Roles & Trust Relationships
    src/iam-list-roles-trust.py --input-file inputs/${INPUT}.tab

    # 4. Commercial Users Credentials
    src/qar_utility.py --datafolder $DATAFOLDER --input-file $INPUT_FILE -cs

    # 4.1 Commercial Users Credentials - rerun
    src/qar_utility.py --datafolder $DATAFOLDER --input-file $INPUT_FILE -cs
fi

### II. Get IAM Roles Trust Relationship / GovCloud
# GovCloud › Setting › Run from whodat dir
if [ 0 -eq "$GO_GOV" ]; then
    export AWS_PROFILE=Gov-GEAdmin
    export DATAFOLDER='/tmp/oneidm'
    export INPUT='gect-sox-gov'
    export INPUT_FILE="inputs/${INPUT}.tab"
    export LOG_FILE="${DATAFOLDER}/${INPUT}.log"
    export LOG_BASH="${DATAFOLDER}/${INPUT}.sh.log"
    export SED_FILT='s/\x1b\[[0-9;]*[a-zA-Z]//g'  # Filter Colors

    # 1. GovCloud › Setting › Gos3 Login
    gos3 mmp-gov | tee $LOG_BASH

    # 2. GovCloud › Check & Validate Input
    ./oneidm-explorer.sh --input $INPUT | tee $LOG_BASH

    # 3. GovCloud › Process Roles & Trust Relationships
    src/iam-list-roles-trust.py --input-file inputs/${INPUT}.tab

    # 4. Commercial Users Credentials
    src/qar_utility.py --datafolder $DATAFOLDER --input-file $INPUT_FILE -cs

    # 4.1 Commercial Users Credentials - rerun
    src/qar_utility.py --datafolder $DATAFOLDER --input-file $INPUT_FILE -cs
fi

## III. Extract DL Groups, Groups Managers, Groups Users & Account Users
# 1. Env Vars
export COM_FILE='/tmp/oneidm/gect-sox-com-dl-list.json'
export GOV_FILE='/tmp/oneidm/gect-sox-gov-dl-list.json'
export OUT_FILE='/tmp/oneidm/gect-sox-LS-Groups-Report.csv'

# 2. Combine Commercial & GovCloud DL names to query string
EC=0
while [ 0 -eq "$EC" ]; do
    # 3. If there is any missing DL name add it $COM_FILE rerutn #2
    # 4. Create new Logical Segregation report & Updaet its data from $OUT_FILE
    QUERY=$(jq -r '.[]' $COM_FILE | tr -d '[]",' | tr '\n' ',';jq -r '.[]' $GOV_FILE | tr -d '[]",' | tr '\n' ',')
    src/oneidm-extract.py --query "$QUERY" --output-file $OUT_FILE --append-file $COM_FILE
    EC="$?"
done


# 5. Commercial Users
if [ 0 -eq "$GO_COM" ]; then
    export USER_IN='/tmp/oneidm/gect-sox-com-LS-Credentials-Report.json'
    export USER_OT='/tmp/oneidm/gect-sox-com-LS-Users-Report.csv'
    src/oneidm-extract.py --input-user $USER_IN --output-file $USER_OT
fi

# 6. GovCloud Users
if [ 0 -eq "$GO_GOV" ]; then
    export USER_IN='/tmp/oneidm/gect-sox-gov-LS-Credentials-Report.json'
    export USER_OT='/tmp/oneidm/gect-sox-gov-LS-Users-Report.csv'
    src/oneidm-extract.py --input-user $USER_IN --output-file $USER_OT
fi

echo -e "
## IV. Consolidate All to One File
1. Create **new Logical Segration folder** from `template`
    - Copy Source: 'LS-2024-Template'
    - Rename Copy: LS-2024-'MM'-'DD'-CT-SOX
2. Copy data form 'DATAFOLDER' to **new Logical Segration folder** 'data-files'
3. From **new Logical Segration folder** open Excel file
4. Copy/Paste 'data-files/gect-sox-LS-Groups-Report.csv'
5. Copy/Paste 'data-files/gect-sox-com-LS-Users-Report.csv'
6. Copy/Paste 'data-files/gect-sox-gov-LS-Users-Report.csv'
7. Make sure all rows with data has relevant formula
8. Make sure all rows without data has no invalid formula
9. Upload to Box
"