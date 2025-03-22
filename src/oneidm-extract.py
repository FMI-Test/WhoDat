#!/usr/bin/env python

import argparse
import concurrent.futures
import requests
import textwrap

from awsutil import *
from common import *
from util import *
from validateutil import *
from DataModels import *
from OneIDM import *

'''
# Nested Groups Test

idm -q '@CORP CoreTech Core WAN Extended Team,@CORP CoreTech Core WAN Team'                     # 23 Members
idm -q '@Digital Monitoring DevOps,@Digital Monitoring Development'                             # 4 Members
idm -q '@Digital Monitoring DevOps,@Digital Monitoring SRE Ops,@Digital Monitoring Development' # 14 Members
idm -q '@GE AWS_bu-iam-admin_619646483517,@Digital Monitoring DevOps,@Digital Monitoring Development,@Digital Monitoring SRE Ops' # 18 Members
idm -q '@GE AWS_bu-terraformer_344180351386,@Digital Network Automation Admins'                 # 13 Members
idm -q '@GE AWS_em-read-only_619646483517,@Digital Monitoring Development'                      # 5 Members
idm -q '@GE AWS_nc/network-engineer_737859062117,@CORP CoreTech Core WAN Extended Team,@CORP CoreTech Core WAN Team'              # 35 Members
idm -q '@GE AWS_netops_480748489013,@CORP CoreTech Core WAN Extended Team,@CORP CoreTech Core WAN Team'                           # 45 Members

idm -q '@CORP CoreTech Core WAN Extended Team,@CORP CoreTech Core WAN Team'                     # 23 Members
idm -q '@CORP Smartsheet Admins,@AEROSPACE DW Productivity Operations'                          # 10 Members
idm -q '@CORP Tech Solutions DevOps,@CORP DW Software - DevOps App Infra Support'               # 34 Members
idm -q '@Digital Monitoring DevOps,@Digital Monitoring Development,@Digital Monitoring SRE Ops' # 14 Members
idm -q '@GE AWS_gear-lab-user_855224342539,@CORP GEAR DT & Cyber'                               # 22 Members

idm -q '@GE AWS_bu-iam-admin_099383845762,@GE Public Cloud Devs'                                # 1 Member - Error: Private or Empty DL

idm -q '@GE AWS_bu-iam-admin_966305512728,@CORP Tech Solutions DevOps,@CORP DW Software - DevOps App Infra Support' # 41 Members
idm -q '@GE AWS_bu-poweruser_960571661179,@CORP CoreTech Core WAN Extended Team,@CORP CoreTech Core WAN Team'       # 45 Members
idm -q '@GE AWS_bu-smartsheet_685016974893,@CORP Smartsheet Admins,@AEROSPACE DW Productivity Operations'           # 11 Members

idm -q '@GE AWS_bu-sre-admin_925449742200,@Digital Monitoring DevOps,@Digital Monitoring Development,@Digital Monitoring SRE Ops' # 20 Members
'''

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''\
    GET SSO & OneIDM data from HR_US 
    ---------------------------------------------------------------------------------------------------------
    Search OneIDM database by SSO, Group ID, & Group Name
                                
    Query Format:
        --query 'SSO1,SSO2,GROUP_ID1,GROUP_ID2, GROUP_NAME1,GROUP_NAME2...'

    Outcome:               
        Query for SSO returns Groups/DL which SSO is belongs to
        Query for Group_ID or Group_Name returns Group data
        Mix Query or csv format will return consolidation of each part OR data

                                
    User Query Format must be singele type of SSO, Display Email, email, 'First, Last' semicolon separated:
        --user 'SSO1,SSO2,...'
        --user 'SSO1;SSO2;...'
        --user 'Last1, First1;Last2, First2;...'
        --user 'email1@..com;email2@...com;

    '''),
    epilog=textwrap.dedent('''\
    Requirement Once:
        - mkdir -p /tmp/oneidm'

    Requirement Always:
        export HRUS_KEY=$( cat ./.HRUS_KEY )
                           
    SOX Report - Run after extracting Commercial & GovCloud data:
        --query ="$QUERY" --oputput-file /tmp/oneidm/gect-sox-LS-Groups-Report.csv

    GitHub: https://github.build.ge.com/GR2-0/Transitional-Master-Payer-Migration
    ''')
)

parser.add_argument('-d', '--debug', action='store_true', help='Debug more to show some underlying data')
parser.add_argument('-q', '--query', metavar='', default='', help='Query to filter the DL data. CSV data of any SSO, Group_ID, & Group_Name')
parser.add_argument('-u', '--user', metavar='', default='', help='Query to filter the Member data. CSV data of any SSO, & EMAIL_DISPLAY_NAME')
parser.add_argument('-i', '--input-user', metavar='', help="Input json user file from credentials report")
parser.add_argument('-o', '--output-file', metavar='', help="Store result to csv output file")
parser.add_argument('-a', '--append-file', metavar='', help="File to append unprocessed Nested Group")
parser.add_argument('-v', '--verbose',  action='store_true', help="Increase verbosity & show data file")
options = parser.parse_args()


CMC_KEY = os.environ.get('CMC_KEY')

dt = get_dt_local()[0:10]
DATAFOLDER = os.environ.get('DATAFOLDER', '/tmp/oneidm')
TITLE = 'OneIDM › Extacrt Data from Oracle Database'

IS_USER = True if options.user else False

# Groups or Users
if IS_USER:
    # Get Users
    query = options.user.replace(',,',',')
    SUBTITLE = 'OneIDM Extract Users Data'
else:
    # Get Groups
    query = options.query.replace(',,',',')
    SUBTITLE = 'OneIDM Extract Groups Data'

query = query.strip()

ENV = {
    'GR2': f"### GR2-0 / {SUBTITLE}",
    'DATAFOLDER': DATAFOLDER,
    'Title': SUBTITLE,
    'Task': SUBTITLE, 
}
rWidth = 132

print(ENV['GR2'])

# Logs
if isDebug() or options.debug: print('Args:', iColor(vars(options), 'iYellow'))

ts = get_ts()

## Dev & test

db = DB(
    user=os.environ.get('USER'), 
    password=os.environ.get('PASS'), 
) 


# Remove trailing comma
while query.endswith(','): query = query[:-1]

# Handle prantises in user query differently
# Ex: --user 'R, Avinash (GE Aerospace, consultant)'
query = query.strip()
if ';' in query:
    query = query.split(';')
elif ',' in query:
    query = query.split(',')

userArns = []
if options.input_user:
    userData = get_json(options.input_user)
    query = []
    for rs in userData:
        user = rs.get('user')
        query.append(user)            
        userArns.append( f"{rs.get('arn')} @ {rs.get('account')}")

    iDebug('Query: ', query)
    iDebug('ARNs: ', userArns)

if isDebug() or options.debug or options.verbose or True:
    print('Query:', iColor(query, 'iYellow'))

res = []
if options.query:
    res = db.get_groups(query)
else:
    res = db.get_users(query)

if res and userArns:
    for i, rs in enumerate(res['Data']):
        if len(userArns) >= i:
            iDebug(f'ARN[{i}]: ', userArns[i])

            # update user info
            if not rs.get('GROUP_ID'):
                try:
                    user = userArns[i].split('@')[0].strip().split('/')[-1]
                    rs['GROUP_ID'] = user
                    rs['GROUP_NAME'] = userArns[i]
                    
                except Exception as err:
                    pass

            # update master data
            res['Data'][i] = rs

sMap = [
    'GROUP_ID', 
    'GROUP_NAME', 
    'GM_SSO', 
    'GM_EMAIL_DISP', 
    'GM_STATUS', 
    # 'GM_TYPE', 
    # 'GM_TITLE', 
    # 'GM_FUNC', 
    # 'GM_BU', 
    # 'GM_BU_SEG', 
    # 'GM_DEP', 
    'GU_SSO', 
    'GU_EMAIL_DISP', 
    'GU_STATUS', 
    'GU_TYPE', 
    # 'GU_TITLE', 
    # 'GU_FUNC', 
    # 'GU_BU', 
    'GU_BU_SEG', 
    # 'GU_DEP', 
]

if IS_USER or options.input_user:
    sMap = [
        'GROUP_NAME', 
        'GU_SSO', 
        'GU_EMAIL_DISP', 
        'GU_EMAIL',
        'GU_STATUS', 
        'GU_TYPE', 
        'GU_EXP',
        'GU_COMP',
        'GU_BU_SEG', 
        'GM_SSO', 
        'GM_EMAIL_DISP', 
        'GM_STATUS', 
   ]

if options.input_user:
    sMap.remove('GU_COMP')

remove_none = [
    'GU_STATUS',
    'GU_BU_SEG',
    'GU_COMP',
]

DL_SEP = ' / '
data = []
groupList = []
groupTree = []
nestedGroups = []
for i, rs in enumerate(res['Data']):
    groupList = append_unique(groupList, rs.get('GROUP_NAME'))
    if rs.get('GU_EMAIL_DISP') and rs.get('GU_EMAIL_DISP').startswith('@'):
        nestedGroups = append_unique(nestedGroups, rs.get('GU_EMAIL_DISP'))

        # Nested Groups Tree - Join by DL_SEP
        nested_group = DL_SEP.join([rs.get('GROUP_NAME'), rs.get('GU_EMAIL_DISP')])
        groupTree.append(nested_group)

    if rs.get('GROUP_NAME') and rs['GROUP_NAME'].startswith('@') and not rs.get('GU_TYPE'):
        rs['GU_TYPE'] = 'GROUP' 

    rec = {}
    for key in sMap:
        rec[key] = rs.get(key)
        
        if key in remove_none and rec[key] is None:
            rec[key] = ''
        
    # Inactive Users without GU_EMAIL_DISP
    if not rs.get('GU_EMAIL_DISP'):
        rec['GU_EMAIL_DISP'] = f"{rs.get('GU_LAST')}, {rs.get('GU_NAME')}"


    data.append(rec)

cMap = OneIDM.get_group_color_map()

# Terminal Report
if data:
    # Remove None GROUP_NAME for Terminal report
    print_data = []
    for ps in data:
        if not ps.get('GROUP_NAME'):
            ps.pop('GROUP_NAME', None)

        # Filter GU_EXP
        if ps.get('GU_EXP'):
            ps['GU_EXP'] = str(ps['GU_EXP'])[:10]

        print_data.append(ps)

    printhh(f"{TITLE} › {SUBTITLE}")
    dm = DataModel()
    dm.print_table(print_data, colors_map=cMap)
else:
    if IS_USER:
        iWarning(f"User does not exist! {iColor(query, 'iYellow')}")
    else:
        iWarning(f"DL does not exist! {iColor(query, 'iYellow')}")

print('Took:', iColor(res['Meta']['Took'], 'iYellow'))

# Stroe to CSV output-file
gMap = {
    'GROUP_ID': 'Group ID',
    'GROUP_NAME': 'Group Name',
    'GM_SSO': 'Manager SSO',
    'GM_EMAIL_DISP': 'Manager Name',
    'GM_STATUS': 'Manager Status',
    # 'GM_TITLE': 'Manager Title',
    # 'GM_FUNC': 'Manager Function',
    # 'GM_BU': 'Manager BU',
    'GM_BU_SEG': 'Manager BU Segment',
    # 'GM_DEP': 'Manager Department',
    'GM_EXP': 'Manager SSO Exp.',
    'GU_SSO': 'Member SSO',
    'GU_EMAIL_DISP': 'Member Name',
    'GU_STATUS': 'Member Status',
    # 'GU_TITLE': 'Member Title',
    # 'GU_COMP': 'Company Name',
    # 'GU_FUNC': 'Member Function',
    # 'GU_BU': 'Member BU',
    'GU_BU_SEG': 'Member BU Segment',
    # 'GU_DEP': 'Member Department',
    'GU_EXP': 'Member SSO Exp.',
}

hasFSSO = False
if options.output_file:
    print('Output File:', iColor(options.output_file, 'iYellow'))
    csvData = []
    for rs in res['Data']:

        # FSSO Special case
        if rs.get('GU_TYPE') == 'FUNCTIONAL':
            hasFSSO = True
            rs['GU_EMAIL_DISP'] = ', '.join([rs.get('GU_NAME', ''), rs.get('GU_LAST', '')])
            if rs['GU_EMAIL_DISP'] == ', ': rs['GU_EMAIL_DISP'] = ''

        rSet = {}
        for key in gMap.keys():
            rSet[gMap[key]] = rs.get(key)

        csvData.append(rSet)

    put_csv(options.output_file, csvData)

if isDebug() or options.debug or options.verbose:
    if options.output_file:
        printhh(f"{TITLE} › DB Data has ({len(res['Data'][0])}) Fileds")
        ppjson(res['Data'][0])
        printhh(f"{TITLE} › Translated Data has ({len(csvData[0])}) Fileds")
        ppjson(csvData[0])

    printhh(f"{TITLE} › Meta-Data")
    print_color_dict(res['Meta'])

# Nested Groups Tree - Join by DL_SEP
# Process Deep Nest
nested_level = 0
deep_nest = []
for dl_chk in groupTree:
    for dl in groupTree:
        dls = dl.split(DL_SEP)
        # if last split is the first of another then deep nested
        nested_level = max(nested_level, len(dls))
        i = len(deep_nest) + 1
        # Only if is not already last split
        if dls[-1] == dl_chk.split(DL_SEP)[0]:
            obj = DL_SEP.join([dl, dl_chk.split(DL_SEP)[-1]])
            if isDebug() or options.debug or options.verbose:
                print_color_dict({
                    f'{i}. Last Split': dls[-1],
                    f'     DL Check': dl_chk,
                    f'     DL to Process': dl,
                    f'     + Deep Nest': obj,
                })
            nested_level = max(nested_level, len(obj.split(DL_SEP)))
            deep_nest.append(obj)

for dl in deep_nest:
    groupTree.append(dl)

# Consolidate
if groupTree:
    deep_nest.sort()
    groupTree.sort()
    printhh(f"{TITLE} › Nested Groups Tree")
    for i, dl in enumerate(groupTree): 
        print(f"{str(i+1).rjust(5)}. {iColor(dl, 'iYellow')}")

    printhh(f"{TITLE} › Nested Groups Tree Summary")
    print_color_dict({
        'Nested Groups': len(groupTree),
        'Nesting Level': nested_level
    })


# Check for unprocessed Groups 
uGroups = []
notGroups = []
for gName in nestedGroups:
    if gName not in groupList and gName not in query:
        uGroups.append(gName)

    if gName not in groupList and gName in query:
        notGroups.append(gName)

if uGroups:
    uGroupsCount = len(uGroups)
    s = 's' if uGroupsCount > 1 else ''
    printhh(f"{TITLE} › Found ({uGroupsCount}) Unprocessed Nested Group")
    print(iColor(','.join(uGroups), 'iYellow'))
    if options.append_file:
        groupList = get_json(options.append_file)
        for group in uGroups:
            if group not in groupList:
                groupList.append(group)

        printhh(f"{TITLE} › {uGroupsCount} Unprocessed Nested Group{s} added to {options.append_file}")
        print(iColor(','.join(uGroups), 'iYellow'))        
        put_json(options.append_file, groupList)

if IS_USER:
    print()
    printhh(f"{TITLE} › If 'GU_TYPE = FUNCTIONAL' column names are following below translation for FSSO")
    fsso_note = {
        'GU_EMAIL_DISP': 'GU_EMAIL_DISP OR FSSO.LAST_NAME, FSSO.FIRST_NAME',
        'GU_EMAIL': 'FSSO Name',
        'GM_SSO': 'FSSO Manager',
    }
    print_color_dict(fsso_note)

## Query & Data count
print_color_dict({
    'Query Items': 1 if isinstance(query, str) else len(query),
    'Data Items': len(data),
    'Took': took_ts(ts),
})

if uGroups:
    iCritical(f"Rerun with updated '--query' value to process {uGroupsCount} Unprocessed Nested Group{s}")

if notGroups:
    notGroupsCount = len(notGroups)
    s = 's' if notGroupsCount > 1 else ''
    iWarning(f"Review {notGroupsCount} Missing Group{s} with no record in OneIDM!")
    print(iColor(','.join(notGroups), 'iYellow'))

    notGroup_detail = []
    for dl in notGroups:
        for rs in data:
            if rs.get('GU_EMAIL_DISP') == dl:
                notGroup_detail.append({
                    'GROUP_ID': rs.get('GROUP_ID'),
                    'GROUP_NAME': rs.get('GROUP_NAME'),
                    'GM_SSO': rs.get('GM_SSO'),
                    'GM_EMAIL_DISP': rs.get('GM_EMAIL_DISP'),
                    'GM_STATUS': rs.get('GM_STATUS'),
                    'GU_SSO': rs.get('GU_SSO'),
                    'GROUP_INVALID_MEMBER': dl,
                })

    dm = DataModel()
    ngd_color = {
        'GROUP_INVALID_MEMBER': {'@': 'iRed'}
    }
    dm.print_table(data=notGroup_detail, colors_map=ngd_color)

