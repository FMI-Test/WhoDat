# Execution

### Execution Script › Commercial
Execution Steps & process:  
1. Set Environment Variables
2. Use `tee` to log shell scripts
3. Re-run `src/oneidm-groups-report.py`
      3.1. If there is any missing group run `whois $gid` for each ones
      3.2. Repeat above steps for all missing groups 
      3.3. Re-run `src/oneidm-groups-report.py`
      3.4. Redo these steps is there is any missing groups
      3.5. If there is no missing group go to next step
4. Run `src/oneidm-users-report.py`  
5. File mamagement
      5.1. Create empty folder with name of input and execution date i.e. `LS-2024-04-22-CT-SOX`
      5.2. Create `data-files` inside folder created in above step
      5.3. Copy input file & data files to `data-files` folder
      5.6. Copy LS Excel File and remove its data  
      5.7. Fill relevant sheets with data
      5.8. Update Disposition sheet
6. Review and validate with OneIDM UI for missing groups
7. Review Python and Shell script Logs
8. Upload to Box

```bash
# Commercial › Setting › Run from whodat dir
whodir
export AWS_PROFILE=GEAdmin
export DATAFOLDER='/tmp/oneidm'
export INPUT_PATH="inputs/${INPUT}.tab"
export INPUT='gect-sox-com'
export LOG_FILE="${DATAFOLDER}/${INPUT}.log"
export LOG_BASH="${DATAFOLDER}/${INPUT}.sh.log"
export SED_FILT='s/\x1b\[[0-9;]*[a-zA-Z]//g'  # Filter Colors - 's///g' - No Filter

# Commercial › Setting › Gos3 Login
gos3 mmp | tee $LOG_BASH

# Check & Validate Input
./oneidm-explorer.sh --input $INPUT | tee $LOG_BASH

# 1. Commercial › Process Roles & Trust Relationships
src/iam-list-roles-trust.py --input-file inputs/${INPUT}.tab

# 2. Commercial › Process DL List to Get User Data & Cache 
time while read -r line; do [ -n "$line" ] && whois "$line"; done < <(cat /tmp/oneidm/${INPUT}-dl-list.json | jq -r . | tr -d '[],"' | awk '{print $1, $2}')

# 3. Commercial › Process DL List & Extract Groups & Users
src/oneidm-groups-report.py --input-file /tmp/oneidm/${INPUT}-dl-list.json

# 4. Commercial › Update Excel Sheets with Extracted Data 
src/oneidm-users-report.py --input-file /tmp/oneidm/${INPUT}-uid-data.json

# Show Log file - In color
cat $LOG_BASH

# Show Log file - No color
cat $LOG_BASH | sed "$SED_FILT"
```

## Execution Steps › Commercial
1. Clear Data folder - /tmp/oneidm
2. clear cache - bin/__cache__
3. Extract IAM Roles & Trust


Took           : 0:06:45.896817
Input File     : inputs/gect-sox.tab
Data Output    : /tmp/oneidm/gect-sox-roles-trusts.json
DL List JSON   : /tmp/oneidm/gect-sox-dl-list.json
DL Output JSON : /tmp/oneidm/gect-sox-gid-data.json
DL Output CSV  : /tmp/oneidm/gect-sox-gid-data.csv



4. Process Groups & Build User Cache Data
time while read -r line; do whois "$line"; done < <(cat /tmp/oneidm/gect-sox-dl-list.json | jq -r . | tr -d '[],"' | awk '{print $1, $2}')

real    8m24.946s
user    2m53.094s
sys     3m38.625s


5. Process DL Groups & Users Data
src/oneidm-groups-report.py --input-file /tmp/oneidm/gect-sox-dl-list.json



## GovCloud
1. Clear Data folder - /tmp/oneidm
2. clear cache - bin/__cache__
3. Extract IAM Roles & Trust


Took           : 0:01:07.776416
Input File     : inputs/gect-sox-gov.tab
Data Output    : /tmp/oneidm/gect-sox-gov-roles-trusts.json
DL List JSON   : /tmp/oneidm/gect-sox-gov-dl-list.json
DL Output JSON : /tmp/oneidm/gect-sox-gov-gid-data.json
DL Output CSV  : /tmp/oneidm/gect-sox-gov-gid-data.csv


4. Process Groups & Build User Cache Data
time while read -r line; do whois "$line"; done < <(cat /tmp/oneidm/gect-sox-gov-dl-list.json | jq -r . | tr -d '[],"' | awk '{print $1, $2}')


      40 Users  in /tmp/oneidm/gect-sox-gov-uid.json
       0 Errors in /tmp/oneidm/gect-sox-gov-err.json
       0 Groups in /tmp/oneidm/gect-sox-gov-grp.json

real    2m6.579s
user    0m31.734s
sys     0m44.203s


5. Process DL Groups & Users Data
src/oneidm-groups-report.py --input-file /tmp/oneidm/gect-sox-gov-dl-list.json


Took              : 0:00:00.192925
Data Folder       : /tmp/oneidm
Input DL List     : /tmp/oneidm/gect-sox-gov-dl-list.json
Input Groups Data : /tmp/oneidm/gect-sox-gov-gid-data.json
Input User Data   : /tmp/oneidm/gect-sox-gov-uid-data.json
Output Data Data  : /tmp/oneidm/gect-sox-gov-Groups-Report.csv
Group               : 9
EmptyGroup          : 0
Users               : 132
Total               : 141
MissingNestedGroups : 1

### GR2-0 / OneIDM Extract Groups Users / Missing Nested Groups
------------------------------------------------------------------------------------------------------------------------
['g01311427']

6. Report Users Data
src/oneidm-users-report.py --input-file /tmp/oneidm/gect-sox-gov-uid-data.json

Took                   : 0:00:00.207735
Input Data             : /tmp/oneidm/gect-sox-gov-uid-data.json
Output CSV             : /tmp/oneidm/gect-sox-gov-Users-Report.csv
Users Count            : 40
Not Active Users Count : 0