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

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''\
    GET SSO & OneIDM data from HR_US 
    ------------------------------------------------------------------------------------------
    '''),
    epilog=textwrap.dedent('''\
    Requirement Once:
        - mkdir -p /tmp/oneidm'
        - mkdir -p __cache__

    Requirement Always:
        export HRUS_KEY=$( cat ./.HRUS_KEY )

    GitHub: https://github.build.ge.com/GR2-0/Transitional-Master-Payer-Migration
    ''')
)

parser.add_argument('-c', '--cache-ttl', metavar='', type=int, default=604800, help="Cache TTL (Time-to-Leave) in seconds, default 604800 - 7 days")
parser.add_argument('-d', '--debug',    action='store_true', help='Disable multi threading for debug')
parser.add_argument('-i', '--input-file', default='/tmp/oneidm/dls.json', help='Input File is a json file of groups.')
parser.add_argument('-n', '--no-cache', action='store_true', help="Live API call and no-cache")
parser.add_argument('-v', '--verbose',  action='store_true', help="Increase verbosity & show data file")
options = parser.parse_args()

CACHE_TTL = int(options.cache_ttl) if isInt(options.cache_ttl) else 604800
USE_CACHE = not options.no_cache

CMC_KEY = os.environ.get('CMC_KEY')
INPUT_FILE = options.input_file

dt = get_dt_local()[0:10]
DATAFOLDER = os.environ.get('DATAFOLDER', '/tmp/oneidm')
INPUT = os.environ.get('INPUT', 'tst')
OUTPUT_FILE = f"{DATAFOLDER}/{INPUT}-Groups-Report.csv"

GRP_FILE = f"{DATAFOLDER}/{INPUT}-gid-data.json"
UID_FILE = f"{DATAFOLDER}/{INPUT}-uid-data.json"

ENV = {
    'GR2': f"### GR2-0 / OneIDM Extract Groups Users",
    'DATAFOLDER': DATAFOLDER,
    'Title': 'OneIDM Extract Groups Users',
    'Task': 'OneIDM Extract Groups Users' 
}
rWidth = 132

print(ENV['GR2'])

# Logs
print('Args:', iColor(vars(options), 'iYellow'))

ts = get_ts()
MY_GROUPS = get_json(INPUT_FILE)
res = get_json(GRP_FILE)
USERS = get_json(UID_FILE)

def get_cmc_data(acc_id):
    url = f"https://cmc.gecloud.io/account/{acc_id}"
    iDebug(f"Get CMC Data by API Call to {url}")

    if not CMC_KEY:
        iWarning(f"Missing CMC KEY for API Call!")

    headers = {
        'Connection': 'keep-alive', 
        'x-api-key': CMC_KEY,
        'Accept-Encoding': 'gzip, deflate', 
        'Cache-Control': 'no-cache', 
        'cache-control': 'no-cache', 
        'Host': 'cmc.gecloud.io', 
        'Accept': '*/*'
    }

    ts = get_ts()
    cName = get_uuid_url(url)

    # get cache
    if USE_CACHE:
        response = get_cache(cName, meta=url)
        type = 'cache'

    # live call if no cache exist
    if not response:
        response = requests.request("GET", url, headers=headers, verify=True)    
        response = response.json()
        type = 'live'
        set_cache(cName, response, CACHE_TTL, meta={
            'uuid': cName,
            'took': took_ts(ts),
            'type': type,
            'url': url,
        })
    
    return response

def get_user(uid):
    res = {}
    
    if USERS.get(uid):
        rs = USERS[uid]
        res = {
            'UserSSO': rs.get('uid'),
            'UserStatus': rs.get('gessostatus'),
            'UserType': rs.get('employeeType'),
            'UserFullName': rs.get('cn'),
            'UserEndDate': rs.get('gessoeffectiveenddate'),
            'UserBUSegment': rs.get('gehrbusinesssegment'),
        }

    return res

uMap = {
    'PrimaryManager': 'primaryManager',
    'OtherManager': 'otherManagers',
    'Member': 'members',
}

# Get all DL accounts
accList = []
for i, key in enumerate(res.keys()):
    rec = res[key]
    acc = rec.get('groupName', '')
    if not acc:
        continue

    acc = acc[len(acc)-12:]
    if isInt(acc):
        if acc not in accList:
            iDebug(f"acc :: {acc}")
            accList.append(acc)

# Get all DL account info
cmcData = {}
if options.debug:
    for acc in accList:
        cmcRes = get_cmc_data(acc)
        cmcData[acc] = {
            'AccountId': cmcRes.get('account_id', ''),
            'AccountName': cmcRes.get('account_name', ''),
            'AccountBU': cmcRes.get('business_unit', ''),
        }
    
if not options.debug:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for acc in accList:
            futures.append(
                executor.submit(
                    get_cmc_data,
                    acc
                ) 
            )

        for future in concurrent.futures.as_completed(futures):
            try:
                cmcRes = future.result()
                acc = cmcRes.get('account_id')
                if acc:
                    cmcData[acc] = {
                        'AccountId': cmcRes.get('account_id', ''),
                        'AccountName': cmcRes.get('account_name', ''),
                        'AccountBU': cmcRes.get('business_unit', ''),
                    }

            except Exception as err:
                iWarning(f'Get CMC Data has Error!', err)


data = []
csvData = []
sumUser = {
    'Group': 0,
    'EmptyGroup': 0,
    'Users': 0,
    'Total': 0,
}
nestedGroups = []
nestedGroupsData = []
for i, key in enumerate(res.keys()):
    rec = res[key]

    if rec['groupName'] not in MY_GROUPS:
        continue

    i += 1

    accData = {}
    acc = rec.get('groupName')
    if acc:
        acc = acc[len(acc)-12:]
        iDebug(f"acc :: '{acc}' :: '{rec.get('groupName')}'")
        if isInt(acc):
            accData = cmcData.get(acc, {})

    csvRs = {
        'GroupId': rec.get('groupId'),
        'GroupName': rec.get('groupName'),
        'GroupEmail': rec.get('mail'),
        'GroupDescription': rec.get('description'),
        'GroupType': rec.get('groupType'),
        'Public': rec.get('membershipType'),
        'UserRole': '',
        'UserSSO': '',
        'UserBUSegment': '',
    }

    rs = {
        'GroupId': rec.get('groupId'),
        'GroupName': rec.get('groupName'),
        'GroupAccountBU': accData.get('AccountBU', ''),
        'GroupExp': rec.get('expirationDate'),
        'GroupType': rec.get('groupType'),
        'Public': rec.get('membershipType'),
    }

    for Role, rKey in uMap.items():
        uVal = rec.get(rKey)    # SSO or GroupId

        rs['UserRole'] = Role
        csvRs['UserRole'] = Role

        if uVal:
            if isinstance(uVal, str):
                uVal = [uVal]

            if isinstance(uVal, list):
                iDebug(iColor(f'{Role}: {uVal}', 'Gray'))
                for uid in uVal:
                    uData = get_user(uid)
                    rs['UserSSO'] = uid
                    rs['UserBUSegment'] = uData.get('UserBUSegment', '')
                    rSet = {}
                    for kk, vv in rs.items():
                        rSet[kk] = vv
                    data.append(rSet)

                    csvRs['UserSSO'] = uid
                    cSet = {}
                    for ck, cv in csvRs.items():
                        cSet[ck] = cv

                    # Only add User Detail to CSV
                    for ck, cv in uData.items():
                        cSet[ck] = cv
                    csvData.append(cSet)
    
                    if uid and isInt(uid):
                        sumUser['Users'] += 1

                    if uid and uid.startswith('g'):
                        sumUser['Group'] += 1
                        if uid not in nestedGroups:
                            nestedGroupsData.append(rSet)
                            nestedGroups.append(uid)
                        

    # Group without Neither Manager Nor User
    if not rs.get('UserSSO'):
        sumUser['EmptyGroup'] += 1
        rs['UserRole'] = ''
        csvRs['UserRole'] = ''
        csvRs['UserBUSegment'] = ''
        data.append(rs)
        csvData.append(csvRs)


# Print Outcome
print()
dm = DataModel()
cMap = OneIDM.get_group_color_map()
dm.print_table(data, colors_map=cMap)
put_csv(OUTPUT_FILE, csvData)

# Count all record Types UserSSO: User, Group, None
for key in sumUser.keys():
    if key != 'Total':
        sumUser['Total'] += sumUser[key]

# Verify all Nested Group are in report
missGroups = []
for gid in nestedGroups:
    isMissing = True
    for rs in data:
        if rs.get('GroupId') and rs.get('GroupId') == gid:
            isMissing = False
            continue

    if isMissing:
        missGroups.append(gid)

sumUser['MissingNestedGroups'] = len(missGroups)

# Files & Timing
fMap = {
    'Took': took_ts_hms(ts),
    'Data Folder': DATAFOLDER,
    'Input DL List': INPUT_FILE,
    'Input Groups Data': GRP_FILE,
    'Input User Data': UID_FILE,
    'Output Data Data': OUTPUT_FILE,
}
print()
blue_green_dict_print(fMap, ' : ',lcol='', rcol='iYellow')

blue_green_dict_print(sumUser, sep=' : ')
iDebug(f'accList ({len(accList)})')
iDebug(f'cmcData ({len(cmcData)})')

# MY_GROUPS = get_json(INPUT_FILE)

missGroups.sort()
if sumUser['MissingNestedGroups']:
    printhh(f"{ENV['GR2']} / Missing ({len(missGroups)}) Nested Groups")
    print(missGroups)

    printhh('Copy Below Code to Process Unprocessed DL to Extract Groups & Users Info')
    for gid in missGroups:
        print(f"{iColor('whois', 'iYellow')} {gid}")
    print()

    # add Missing Groups
    updatedGroup = []
    ugId = 0
    for gid in missGroups:
        groupData = res.get(gid) 
        if groupData:
            groupName = groupData.get('groupName')
            if groupName not in MY_GROUPS:
                ugId += 1
                iWarning(f"{ugId}. updatedGroup Append : {iColor(groupName, 'iYellow')}")
                updatedGroup.append(groupName)

    ugId = 0
    for groupName in updatedGroup:
        if groupName not in MY_GROUPS:
            ugId += 1
            iWarning(f"{ugId}. updatedGroup Appended {iColor(groupName, 'iYellow')}")
            MY_GROUPS.append(groupName)
    
    if updatedGroup:
        put_json(INPUT_FILE, MY_GROUPS)
        iWarning(f"{len(updatedGroup)} Groups added to {iColor(INPUT_FILE, 'iYellow')}")
        iWarning("Re-run to verify!")
