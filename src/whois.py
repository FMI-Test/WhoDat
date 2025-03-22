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

    Requiremnt Always: 
        - export HRUS_KEY=$(cat ../../.HRUS_KEY)
                           
    Usage Examples:
        whois aws-p-jump-elevated-admin_432375862099@ge.com
        whois aws-p-jump-elevated-approver_432375862099@ge.com
        whois aws-p-jump-elevated-admin_589623221417@ge.com
        whois 503345432
        whois g03003109
    
    Batch:
        whois --input-file /tmp/oneidm/jump-roles.txt # see whois.sh
        time while read -r line; do whois "$line"; done < /tmp/oneidm/jump-roles.txt 

    GitHub: https://github.build.ge.com/GR2-0/Transitional-Master-Payer-Migration
    ''')
)

parser.add_argument('query', help="HR_US query to get User or Group data")
parser.add_argument('-b', '--brief',     metavar='', help="Brief output")
parser.add_argument('-c', '--cache-ttl', metavar='', type=int, default=604800, help="Cache TTL (Time-to-Leave) in seconds, default 604800 - 7 days")
parser.add_argument('-d', '--debug',    action='store_true', help='Disable multi threading for debug')
parser.add_argument('-u', '--user',     action='store_true', help="User report, default idm if email provided")
parser.add_argument('-n', '--no-cache', action='store_true', help="Live API call and no-cache")
parser.add_argument('-v', '--verbose',  action='store_true', help="Increase verbosity & show data file")
options = parser.parse_args()

BRIEF = options.brief 
CACHE_TTL = int(options.cache_ttl) if isInt(options.cache_ttl) else 604800
USE_CACHE = not options.no_cache

DATAFOLDER = os.environ.get('DATAFOLDER', '/tmp/oneidm')
INPUT = os.environ.get('INPUT', 'tst')

GRP_FILE = f"{DATAFOLDER}/{INPUT}-gid-data.json"
UID_FILE = f"{DATAFOLDER}/{INPUT}-uid-data.json"

TODAY = get_today()
ENV = {
    'GR2': f"### GR2-0 / {iColor('OneIDM Extract API', 'Orange')} on {TODAY}",
    'DATAFOLDER': DATAFOLDER,
    'Title': 'OneIDM Extract API',
    'Task': 'OneIDM Extract API' 
}
rWidth = 132

ppwide(ENV['GR2'], width=rWidth)

# Logs:
print('Args:', iColor(vars(options), 'iYellow'))

HRUS_KEY = os.environ.get('HRUS_KEY')

VAL = Validator(ENV['Task'])
UIDS = []

def get_hr_data(query):
    # printll(f"{ENV['GR2']} / Get OneIDM Data by API Call", width=rWidth)
    while query.startswith('/'): query = query[1:]

    url = f"https://hr-us.gecloud.io/{query}"
    headers = {
        'Connection': 'keep-alive', 
        'x-api-key': HRUS_KEY,
        'Content-Type': 'application/json',
        'Accept-Encoding': 'gzip, deflate', 
        # 'Cache-Control': 'no-cache', 
        # 'cache-control': 'no-cache', 
        'Host': 'hr-us.gecloud.io', 
        'Accept': '*/*'
    }

    response = {}

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
            'query': query,
            'took': took_ts(ts),
            'type': type,
            'url': url,
        })
    
    response['meta'] = {
        'uuid': cName,
        'query': query,
        'took': took_ts(ts),
        'type': type,
        'url': url,
    }

    return response

def get_ids(rs, only_gid=False, only_uid=False):
    """Returns list of Group & User ID
    
    Args:
        rs (dict): Dict of Group or User
        only_gid (bool): Only return Group ID, default False
        only_uid (bool): Only return User ID, default False

    only_gid    only_uid    Outcome
    ---------------------------------
    False       False       All
    False       True        Only User
    True        False       Only Group
    True        True        All - Invalid only this and only that hence skipped
    """
    sMap = [
        'primaryManager',
        'otherManagers',
        'members',
        'uid',
    ]

    kLen = 13
    res = []

    iTrace(rs)
    iDebug(data_view(rs))
    for k in sMap:
        ids = rs.get(k)
        if ids and isinstance(ids, str):
            ids = [ids]

        if ids and isinstance(ids, list):
            for id in ids:
                if not id.startswith('g') and id not in UIDS: UIDS.append(id)
                if id not in res: res.append(id)
                if id.startswith('g'):
                    iDebug(f'Nested Group {rspace(k, kLen)} :: {id}')

    if only_uid and not only_gid:
        rs = res
        res = []
        for rec in rs:
            if not rec.startswith('g'):
                res.append(rec)

    if only_gid and not only_uid:
        rs = res
        res = []
        for rec in rs:
            if rec.startswith('g'):
                res.append(rec)

    return res

def get_api_error(rs, silent=False):
    """Return List of API Errors - prints errors too if not silent"""
    eMap = [
        'message',
        'error'
    ]

    res = []
    for k in eMap:
        if rs.get(k):
            if not silent: iWarning(f"API Error :: {rs[k]}")
            res.append(rs[k])

    return res

# Process Query
def query_builder(q):
    """Returns dict of action & query"""
    res = {}
    action = ''
    query = None

    q = q.strip()
    # /user?sso=$sso # if 9 digits 
    if isInt(q):
        action = 'Get User by SSO'
        query = f'/user?sso={q}'

    # /user?email=$email # if endswith @ge.com
    if q.endswith('@ge.com') and options.user:
        action = 'Get User by Email'
        query =  f'/user?email={q}'

    # /user?firstName=$firstName&lastName=$lastName # if has ,
    if ',' in q:
        action = 'Get User by Name'
        name = q.split(',')
        query = f'user?firstName={name[1]}&lastName={name[0].strip()}'

    # /idm?groupId=$groupId # if 9 characters start with g
    if q.startswith('g') and isInt(str(q)[1:]):
        action = 'Get Group by ID'
        query = f'/idm?groupId={q}'

    # /idm/email=$email # if endswith @ge.com
    if q.endswith('@ge.com') and not options.user:
        action = 'Get Group by Email'
        query = f'/idm?email={q}'

    # /idm/name=$name # if starts swith @
    if q.startswith('@'):
        action = 'Get Group by Name'
        query = f'/idm?name={q}'

    res = {
        'action': action,
        'query': query,
    }
    iDebug(f"query_builder :: {res}")
    return res

def data_view(rs, brief=False):
    sMap = {
        # User
        'uid': 'SSO',
        'gessostatus': 'Status',
        'cn': 'Full Name',
        # 'employeeType': 'Type',
        # 'gessoeffectiveenddate': 'End Date',
        # 'gehrbusinesssegment': 'BU Segment', 

        # Group
        'groupId': 'GroupId',
        'groupName': 'GroupName',
        'groupType': 'GroupType',
        # 'primaryManager': 'PrimaryManager',
        # 'otherManagers': 'OtherManagers',
        # 'membershipType': 'GType',
        # 'members': 'Members',
        # Add Nested Groups Data
    }

    res = {}
    if rs.get('meta') and rs['meta'].get('uuid'):
        res['UUDI'] = str(rs['meta']['uuid'])

    for key in sMap.keys():
        if rs.get(key):
            newKey = sMap[key]
            res[newKey] = rs[key]

    return res

# Multi-thread
# Fix cyclic dependencies - a to b to a
global processedGroups
processedGroups = [] 
def process_id(id, i):
    """Process Group & User"""

    res = []
    rs = query_builder(id)
    action = rs.get('action')
    query = rs.get('query')
    
    rs = get_hr_data(query)
    res.append(rs)
    err = get_api_error(rs)
    rColor = 'Red' if err else ''

    dv = data_view(rs)
    print(f"  {lspace(i, 5)}. {iColor(action, rColor)} {query} :: {dv}")
    outcome = SUCCESS if rs else FAILURE
    VAL.put(task=action, outcome=outcome, note=dv)

    # Process Nested Groups
    groupdIds = get_ids(rs, only_gid=True)
    while True:
        nextIds = []
        for j, id in enumerate(groupdIds):
            j += 1
            if id not in processedGroups:
                processedGroups.append(id)
                iDebug(f"processedGroups :: {processedGroups}")

            rs = query_builder(id)
            action = rs.get('action')
            query = rs.get('query')

            rs = get_hr_data(query)
            res.append(rs)
            err = get_api_error(rs)
            rColor = 'Red' if err else ''

            dv = data_view(rs)
            print(f"  {lspace(i, 5)}.{j} {iColor(action, rColor)} {query} :: {dv}")
            outcome = SUCCESS if rs else FAILURE
            VAL.put(task=action, outcome=outcome, note=dv)
            
            # Deep Nested
            rs = get_ids(rs, only_gid=True)
            for rec in rs:
                if rec not in nextIds and rec not in processedGroups:
                    nextIds.append(rec)
        
        if nextIds:
            groupdIds = nextIds
        else:
            break

    return res


# Process Query
rs = {}
ts = get_ts()
action = ''
query = None
ids = []
if options.query:
    q = options.query
    rs = query_builder(options.query)

    action = rs.get('action')
    query = rs.get('query')

    if query:
        ppwide(f"{ENV['GR2']} / {action}", width=rWidth)
        print('Action:', iColor(action, 'iYellow'))
        print('Query :', iColor(query, 'iYellow'))
        rs = get_hr_data(query)
        iDebug(rs)
        get_api_error(rs)
        ids = get_ids(rs)

dv = data_view(rs)
outcome = SUCCESS if rs else SKIPPED
VAL.put(task=action, outcome=outcome, note=dv)

kMap = [
    'groupName',
    'Description',
    'uid',
    'cn',
]

count = len(ids) if not rs.get('uid') else 1
ppwide(f"{ENV['GR2']} / {count} {action}", width=rWidth)
for key in kMap:
    if rs.get(key):
        print(f'{key}:', iColor(rs[key], 'Blue'))

res = []
if options.debug:
    for i, id in enumerate(ids):
        i += 1
        iDebug(f"{len(ids)} ids :: {i}. :: {id} :: {processedGroups}")
        rs = process_id(id, i)
        res.append(rs)
    
if not options.debug:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for i, id in enumerate(ids):
            futures.append(
                executor.submit(
                    process_id,
                    id,
                    i
                ) 
            )

        for future in concurrent.futures.as_completed(futures):
            try:
                data = future.result()
                [res.append(rs) for rs in data]

            except Exception as err:
                iWarning(f'Process IDs has Error!', err)

# Verbose Output
if options.verbose:
    printll(f"{ENV['GR2']} / ResFile", width=rWidth)
    ppyamlc(res)

    printll(f"{ENV['GR2']} / Environment Info", width=rWidth)
    ppyamlc(ENV)

if VAL.get_outcome() == FAILURE:
    printll(f"{ENV['GR2']} / Outcome Faliures", width=rWidth)
    VAL.list_failures()

printll(f"{ENV['GR2']}  / Outcome: {VAL.get_outcome().upper()}", width=rWidth)
VAL.print_outcome()

# Unique users list # [{uid: {}}
ids_data = {}
if isFile(UID_FILE):
    data = get_json(UID_FILE)
    if isinstance(data, dict):
        ids_data = data

# unique groups list # {gid: {}, ...}
gid_data = {}
if isFile(GRP_FILE):
    data = get_json(GRP_FILE)
    if isinstance(data, dict):
        gid_data = data

# rs is dict of one group - if any 
if rs and 'groupId' in rs:
    gid = rs.get('groupId')
    if gid not in gid_data:
        gid_data[gid] = rs

for rs in res:
    if rs and 'groupId' in rs:
        gid = rs.get('groupId')
        if gid not in gid_data:
            gid_data[gid] = rs

# res is list of SSO - Users - if any
dm = DataModel()
data = []
for rs in res:
    # Group Report - Dict
    if isinstance(rs, dict):
        uids = get_ids(rs, only_uid=True)
        gids = get_ids(rs, only_gid=True)
        for id in uids:
            query = f'/user?sso={id}'
            rec = get_hr_data(query)
            data.append({
                'SSO': rec.get('uid'),
                'Status': rec.get('gessostatus'),
                'Full Name': rec.get('cn'),
                'Type': rec.get('employeeType'),
                'End Date': rec.get('gessoeffectiveenddate'),
                'BU Segment': rec.get('gehrbusinesssegment'),
            })
            uid = rec.get('uid')
            if uid not in ids_data:
                ids_data[uid] = rec
        continue

    # User Report - List
    for rec in rs:
        data.append({
            'SSO': rec.get('uid'),
            'Status': rec.get('gessostatus'),
            'Full Name': rec.get('cn'),
            'Type': rec.get('employeeType'),
            'End Date': rec.get('gessoeffectiveenddate'),
            'BU Segment': rec.get('gehrbusinesssegment'),
        })
        uid = rec.get('uid')
        if uid not in ids_data:
            ids_data[uid] = rec

# Print Outcome
if options.query:
    q = options.query
    rs = query_builder(options.query)

    action = rs.get('action')
    query = rs.get('query')

    if query:
        print()
        print('Action:', iColor(action, 'iYellow'))
        print('Query :', iColor(query, 'iYellow'))

cMap = OneIDM.get_user_color_map()
dm.print_table(data,colors_map=cMap)

grp_count = lspace(f'{len(gid_data):,}', 8)
print(f"{grp_count} Groups in {iColor(GRP_FILE, 'iYellow')}")
if gid_data:
    put_json(GRP_FILE, gid_data, sort_key=True)

ids_count = lspace(f'{len(ids_data):,}', 8)
print(f"{ids_count} Users  in {iColor(UID_FILE, 'iYellow')}")
if ids_data:
    put_json(UID_FILE, ids_data, sort_key=True)

cColor = 'iGreen' if USE_CACHE else 'iRed'
print(f"Cache     : {iColor(USE_CACHE, cColor)}")
if USE_CACHE:
    print(f"Cache TTL : {iColor(cache_ttl_fmt(CACHE_TTL), cColor)}")
print(f"Took      : {iColor(took_ts_hms(ts), cColor)}")
