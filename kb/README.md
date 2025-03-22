# Logical Segregation

## Process & Steps
Below shows the top-down steps to extract DLs from AWS accounts by API calls then processing it to generate Users & Groups detailed data by making DB calls and finally storing data in excel file.  

| # | Description | Source | Input | Output | File Types |  
| --- | --- | --- | --- | --- | --- |  
| 1 | Process Roles Trust to Extract DL | AWS Commercial | Account List | DL List | csv, json |  
| 2 | Process Users Credentials Reports | AWS Commercial | Account List | Users Credentials | csv, json |  
| 3 | Process Roles Trust to Extract DL | AWS GovCloud | Account List | DL List | csv, json |  
| 4 | Process Users Credentials Reports | AWS GovCloud | Account List | Users Credentials | csv, json |  
| 5 | Process DL Lists | Data Files | DL Lists | DL Disposition List | csv, json |  
| 6 | Process Users Data | AWS Commercial | csv, json | User Dispositon List | csv, json, xlsx |  
| 7 | Process Users Data | AWS GovCloud | csv, json | User Dispositon List | csv, json, xlsx |  
| 8 | Combine DL & Users Data | Data Files | csv | Dispositon List | xlsx |  


### I. Get IAM Roles Trust Relationship / Commercial
- Clean `DATAFOLDER` folder  
```bash
# Commercial › Setting › Run from whodat dir
export AWS_PROFILE=GEAdmin
export DATAFOLDER='/tmp/oneidm'
export COM_INPUT='gect-sox-com'
export COM_INPUT_FILE="inputs/${COM_INPUT}.tab"
export LOG_FILE="${DATAFOLDER}/${COM_INPUT}.log"
export LOG_BASH="${DATAFOLDER}/${COM_INPUT}.sh.log"
export SED_FILT='s/\x1b\[[0-9;]*[a-zA-Z]//g'  # Filter Colors
cp "$COM_INPUT_FILE" "${DATAFOLDER}/${COM_INPUT}.tab"

# 1. Commercial › Setting › Gos3 Login
gos3 mmp | tee $LOG_BASH

# 2. Commercial › Check & Validate Input
./oneidm-explorer.sh --input $COM_INPUT | tee $LOG_BASH

# 3. Commercial › Process Roles & Trust Relationships
src/iam-list-roles-trust.py --input-file inputs/${COM_INPUT}.tab

# 4. Commercial Users Credentials - Repeat untill all Credential report as COMPLETE
src/qar_utility.py --datafolder $DATAFOLDER --input-file $COM_INPUT_FILE -cs
```

### II. Get IAM Roles Trust Relationship / GovCloud
```bash
# GovCloud › Setting › Run from whodat dir
# export AWS_PROFILE=Gov-GEAdmin
# export DATAFOLDER='/tmp/oneidm'
# export GOV_INPUT='gect-sox-gov'
# export GOV_INPUT_FILE="inputs/${GOV_INPUT}.tab"
# export LOG_FILE="${DATAFOLDER}/${GOV_INPUT}.log"
# export LOG_BASH="${DATAFOLDER}/${GOV_INPUT}.sh.log"
# export SED_FILT='s/\x1b\[[0-9;]*[a-zA-Z]//g'  # Filter Colors
# cp "$GOV_INPUT_FILE" "${DATAFOLDER}/${GOV_INPUT}.tab"

# # 1. GovCloud › Setting › Gos3 Login
# gos3 mmp-gov | tee $LOG_BASH

# # 2. GovCloud › Check & Validate Input
# ./oneidm-explorer.sh --input $GOV_INPUT | tee $LOG_BASH

# # 3. GovCloud › Process Roles & Trust Relationships
# src/iam-list-roles-trust.py --input-file inputs/${GOV_INPUT}.tab

# # 4. Commercial Users Credentials
# src/qar_utility.py --datafolder $DATAFOLDER --input-file $GOV_INPUT_FILE -cs
```

## III. Extract DL Groups, Groups Managers, Groups Users & Account Users
```bash
# 1. Env Vars
export COM_FILE="/tmp/oneidm/$COM_INPUT-dl-list.json"
export GOV_FILE="/tmp/oneidm/$GOV_INPUT-dl-list.json"
export OUT_FILE="/tmp/oneidm/$COM_INPUT-LS-Groups-Report.csv"

# 2. Combine Commercial & GovCloud DL names to query string - Repeat below 4 lines to process all DLs
[ -f $COM_FILE ] && QUERY=$(jq -r '.[]' $COM_FILE | tr -d '[]",' | tr '\n' ',')
[ -f $GOV_FILE ] && QUERY=$(echo $QUERY;jq -r '.[]' $GOV_FILE | tr -d '[]",' | tr '\n' ',')
QUERY=$(echo $QUERY | sed 's/ @/@/g')
src/oneidm-extract.py --query "$QUERY" --output-file $OUT_FILE --append-file $COM_FILE

# 3. If there is any missing DL name add it $COM_FILE rerutn #2
# 4. Create new Logical Segregation report & Updaet its data from $OUT_FILE

# 5. Commercial Users
export USER_IN="/tmp/oneidm/$COM_INPUT-LS-Credentials-Report.json"
export USER_OT="/tmp/oneidm/$COM_INPUT-LS-Users-Report.csv"
src/oneidm-extract.py --input-user $USER_IN --output-file $USER_OT

# # 6. GovCloud Users
# export USER_IN="/tmp/oneidm/$GOV_INPUT-LS-Credentials-Report.json"
# export USER_OT="/tmp/oneidm/$GOV_INPUT-LS-Users-Report.csv"
# src/oneidm-extract.py --input-user $USER_IN --output-file $USER_OT

# 7. LOgical Segregation Data Files
find ${DATAFOLDER}/*-LS-Groups-Report.csv ${DATAFOLDER}/*-LS-Users-Report.csv
```

## IV. Consolidate All to One File
1. Create **new Logical Segration folder** from `template`
    - Duplicate Template Dir: `LS-2025-Template-CT-SOX`
    - Rename Duplicated Template Dir: LS-2024-`MM`-`DD`-CT-SOX
2. Copy data form `DATAFOLDER` to **new Logical Segration folder** `data-files`
3. From **new Logical Segration folder** open Excel file
4. Copy/Paste `data-files/gect-sox-LS-Groups-Report.csv`
5. Copy/Paste `data-files/gect-sox-com-LS-Users-Report.csv`
6. Copy/Paste `data-files/gect-sox-gov-LS-Users-Report.csv` - If there is GovCloud 
7. Make sure all rows with data has relevant formula
8. Make sure all rows without data has no invalid formula
9. Upload to Box

### OneIDM Database & API ACCESS
```bash
# API Keys
export CMC_KEY='********'
export HRUS_KEY='********'

# OneIDM Database 'TSA_LOOKER' Access
export USER='********'
export PASS='********'
export HOST='p91-2-3-scan.corporate.ge.com'

# Call Python to read DB Data
```

## AWS Users & Password Policy

```bash
# Filter Credentials Report
find /tmp/oneidm/ | grep 'gect-all' | grep 'LS-Credentials-Report'


cat /tmp/oneidm/gect-all-com-LS-Credentials-Report.json | jq . | grep 
```

### Support
For OneIDM Mark Ritchie (212598369) moved out of the team that has good understanding of these issues but Andrew Smiley (503415873) could help if OneIDM ticket takes long time to resolve.  

