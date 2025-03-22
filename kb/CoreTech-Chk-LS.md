### I. Get IAM Roles Trust Relationship / Commercial
- Check Accounts with no DL record in LS report.  
- Clean `DATAFOLDER` folder.  

```bash
# Commercial › Setting › Run from whodat dir
export AWS_PROFILE=GEAdmin
export DATAFOLDER='/tmp/oneidm'
export COM_INPUT='gect-chk-com'

export COM_INPUT_FILE="inputs/${COM_INPUT}.tab"
export LOG_FILE="${DATAFOLDER}/${COM_INPUT}.log"
export LOG_BASH="${DATAFOLDER}/${COM_INPUT}.sh.log"
export SED_FILT='s/\x1b\[[0-9;]*[a-zA-Z]//g'  # Filter Colors

cp "$COM_INPUT_FILE" "${DATAFOLDER}/${COM_INPUT}.tab"
gos3 mmp | tee $LOG_BASH
./oneidm-explorer.sh --input $COM_INPUT | tee $LOG_BASH
src/iam-list-roles-trust.py --input-file inputs/${COM_INPUT}.tab
src/qar_utility.py --datafolder $DATAFOLDER --input-file $COM_INPUT_FILE -cs
```

### II. Get IAM Roles Trust Relationship / GovCloud
```bash
# GovCloud › Setting › Run from whodat dir
export AWS_PROFILE=Gov-GEAdmin
export GOV_INPUT='gect-chk-gov'
export GOV_INPUT_FILE="inputs/${GOV_INPUT}.tab"

cp "$GOV_INPUT_FILE" "${DATAFOLDER}/${GOV_INPUT}.tab"
gos3 mmp-gov | tee $LOG_BASH
./oneidm-explorer.sh --input $GOV_INPUT | tee $LOG_BASH
src/iam-list-roles-trust.py --input-file inputs/${GOV_INPUT}.tab
src/qar_utility.py --datafolder $DATAFOLDER --input-file $GOV_INPUT_FILE -cs
```

## III. Extract DL Groups, Groups Managers, Groups Users & Account Users
```bash
# 1. If there is any missing DL name add it $COM_FILE regenerate QUERY & Rerun
# 1.1. Env Vars
export COM_FILE="/tmp/oneidm/$COM_INPUT-dl-list.json"
export OUT_FILE="/tmp/oneidm/$COM_INPUT-LS-Groups-Report.csv"

[ -f $COM_FILE ] && QUERY=$(jq -r '.[]' $COM_FILE | tr -d '[]",' | tr '\n' ',')
QUERY=$(echo $QUERY | sed 's/ @/@/g')
# echo -e "Query: ${iYellow}${QUERY}${NC}\nOut File: ${iBlue}${OUT_FILE}${NC}\nCom File: ${iBlue}${COM_FILE}${NC}"
src/oneidm-extract.py --query "$QUERY" --output-file $OUT_FILE --append-file $COM_FILE

# 1.2. Env Vars
export COM_FILE="/tmp/oneidm/$GOV_INPUT-dl-list.json"
export OUT_FILE="/tmp/oneidm/$GOV_INPUT-LS-Groups-Report.csv"

[ -f $COM_FILE ] && QUERY=$(jq -r '.[]' $COM_FILE | tr -d '[]",' | tr '\n' ',')
QUERY=$(echo $QUERY | sed 's/ @/@/g')
# echo -e "Query: ${iYellow}${QUERY}${NC}\nOut File: ${iBlue}${OUT_FILE}${NC}\nCom File: ${iBlue}${COM_FILE}${NC}"
src/oneidm-extract.py --query "$QUERY" --output-file $OUT_FILE --append-file $COM_FILE

# 2. Create new Logical Segregation report & Updaet its data from $OUT_FILE

# 3.1. Commercial Users
export USER_IN="/tmp/oneidm/$COM_INPUT-LS-Credentials-Report.json"
export USER_OT="/tmp/oneidm/$COM_INPUT-LS-Users-Report.csv"
src/oneidm-extract.py --input-user $USER_IN --output-file $USER_OT

# 3.2. GovCloud Users
export USER_IN="/tmp/oneidm/$GOV_INPUT-LS-Credentials-Report.json"
export USER_OT="/tmp/oneidm/$GOV_INPUT-LS-Users-Report.csv"
src/oneidm-extract.py --input-user $USER_IN --output-file $USER_OT

# 5. LOgical Segregation Data Files
find ${DATAFOLDER}/*-LS-Groups-Report.csv ${DATAFOLDER}/*-LS-Users-Report.csv
```
