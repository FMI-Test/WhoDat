#!/usr/bin/env python

import argparse
import concurrent.futures
import requests
import textwrap

from awsutil import *
from common import *
from util import *
from validateutil import *

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''\
    Describe AWS Account Organization
    ------------------------------------------------------------------------------------------
    '''),
    epilog=textwrap.dedent('''\
    Requiremnt Always: 
        - Active Orgs Profiles
                           
    Usage Examples:
        describe-account 716721748482[,...] [--output-file /tmp/output-accounts.[json|csv]]
    
    GitHub: https://github.build.ge.com/GR2-0/Transitional-Master-Payer-Migration
    ''')
)

parser.add_argument('accounts', type=str, help="A comma delimeted list of AWS accounts wraped in qoutes.")
parser.add_argument('-d', '--debug',    action='store_true', help='Disable multi threading for debug')
parser.add_argument('-o', '--output-file',  metavar='', help="Store output to a given csv or json file. Default csv")
parser.add_argument('-v', '--verbose',  action='store_true', help="Increase verbosity & show data file")
options = parser.parse_args()
 
CMC_KEY = os.environ.get('CMC_KEY')
DATAFOLDER = os.environ.get('DATAFOLDER')
OUT_FILE = options.output_file
TODAY = get_today()
ENV = {
    'GR2': f"### GR2-0 / Describe AWS Account Organizations on {TODAY}",
    'DATAFOLDER': DATAFOLDER,
    'Title': 'Describe AWS Account Organizations',
    'Task': 'Describe AWS Account Organizations' 
}
rWidth = 152

ppwide(ENV['GR2'], width=rWidth)

# Logs
print('Args:', iColor(vars(options), 'iYellow'))

ts = get_ts()

# Multi-thread
def describe_org(account_id, client, org):
    """Process account"""
    res = {}

    response = client.describe_account(account_id)

    if response:
        res = {
            'AccountId': response['Id'],
            'AccountAlias': response['Name'],
            'Status': response['Status'].title(),
            'JoinedMethod': response['JoinedMethod'],
            'JoinedDate': str(response['JoinedTimestamp'])[0:10],
            'Org': org,
        }

        if isDebug():
            print(
                'Current Org',
                iColor(org, 'Green'),
                '::',
                iColor(res['Status'], 'Yellow'),
                'State ::',
                f"({res['AccountId']}) [{res['AccountAlias']}]",
            )
    
    return res

def get_cmc_data(acc_id, org='Unknown'):
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

    response = requests.request("GET", url, headers=headers, verify=True)    
    response = response.json()
    iDebug(f"CMC API Call Res :: {response}") 

    response['LeaveDate'] = ''

    if response.get('migration_date'):
        response['JoinedMethod'] = 'MIGRATED'
        response['JoinedDate'] = response['migration_date'][0:10]

    if response.get('provision_date'):
        response['JoinedMethod'] = 'PROVISIONED'
        response['JoinedDate'] = response['provision_date'][0:10]

    if response.get('ejected_date'):
        response['LeaveDate'] = response['ejected_date'][0:10]

    if response.get('suspended_date') and not response.get('ejected_date'):
        response['LeaveDate'] = response['suspended_date'][0:10]

    # Cleanup invalid LeaveDate entry 
    if response['LeaveDate'] in ['UNKNOWN', 'N/A']:
        response['LeaveDate'] = ''

    response['Org'] = org

    return response
    
# Org Data
oMap = {
    'GECC': {
        'AccountId': '737859062117',
        'AccountAlias': 'gecc',
        'OrgId': '',
        'BU': 'Corporate CoreTech',
    },
    'GEAV': {
        'AccountId': '538763039462',
        'AccountAlias': 'master-payer-av',
        'OrgId': '',
        'BU': 'Aviation',
    },
    # 'GEHC': {
    #     'AccountId': '582019957860',
    #     'AccountAlias': 'master-payer-hc',
    #     'OrgId': '',
    #     'BU': 'Healthcare',
    # },
    # 'CC01': {
    #     'AccountId': '171844140004',
    #     'AccountAlias': 'cc-architecture-001',
    #     'OrgId': '',
    #     'BU': 'Corporate CoreTech',
    # },
}

# Clients
clients = {
    'GECC': Organization(profile_name='GECC', quite=not options.debug),
    'GEAV': Organization(profile_name='GEAV', quite=not options.debug),
    # 'CC01': Organization(profile_name='CC01', quite=not options.debug),
    # 'GEHC': Organization(profile_name='GEHC', quite=not options.debug),
}

# Verify profiles
try:
    sts = STS(profile_name='GECC')
    response = sts.get_caller_identity()
    if response.get('Account') != '737859062117':
        iAbort(f'Invalid GECC Profile! {response}')
except Exception as err:
    iAbort(f'Invalid GECC Profile! {err}')

# AWS Org Map
orgMap = {
    'AccountId': 'Id',
    'AccountAlias': 'Name',
    'Status': 'Status',
    'JoinedMethod': 'JoinedMethod',
    'JoinedDate': 'JoinedTimestamp',
    'Org': 'Org',
}

# CMC Map
cmcMap = {
    'AccountId': 'account_id',
    'AccountAlias':  'account_name',
    'BU': 'business_unit',
    'SKU': 'sku',
    'Status': 'status',
    'JoinedMethod': 'JoinedMethod',
    'JoinedDate': 'JoinedDate',
    'LeaveDate': 'LeaveDate',
    'Org': 'Org',
}

# Process Input
ACCOUNTS = []
accs = options.accounts.split(',')
for acc in accs:
    if acc:
        ACCOUNTS.append(ndigits(acc, 12))

count = len(ACCOUNTS)
s = 's' if count > 1 else ''
ppwide(f"{ENV['GR2']} / {count} Account{s}", width=rWidth)

res = []
if options.debug:
    for account_id in ACCOUNTS:
        for org in oMap.keys():
            rs = describe_org(account_id, clients[org], org)
            if rs:
                res.append(rs) 

if not options.debug:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for account_id in ACCOUNTS:
            for org in oMap.keys():
                futures.append(
                    executor.submit(
                        describe_org,
                        account_id,
                        clients[org],
                        org,
                    ) 
                )

        for future in concurrent.futures.as_completed(futures):
            try:
                rs = future.result()
                if rs:
                    res.append(rs)

            except Exception as err:
                iWarning(f'Process IDs has Error!', err)


# Store Results
# put_json(ENV['ResFile'], res)

# Verbose Output
if options.verbose:
    printll(f"{ENV['GR2']} / Environment Info", width=rWidth)
    ppyamlc(ENV)

# Process Output

# Outcome
print()
ppwide(f"{ENV['GR2']} / {count} Account{s}", width=rWidth)

data = []
processedIds = []
for account_id in ACCOUNTS:
    if account_id in processedIds:
        continue

    notFound = True
    org = 'Unknown'
    for rec in res:
        if notFound and rec['AccountId'] == account_id:
            notFound = False
            processedIds.append(account_id)
            org = rec.get('Org')
            # data.append(rec)

    cmcRes = get_cmc_data(account_id, org)
    rs = {}
    for key in cmcMap.keys():
        rs[key] = cmcRes.get(cmcMap[key])

    processedIds.append(account_id)

    if not rs['AccountId']: rs['AccountId'] = account_id
    data.append(rs)

dm = DataModel()
cMap = {
    'Status': {
        'None': 'Red',
        'Unknown': 'Red'
    },
    'BU': {
        'Corporate CoreTech': 'Green',
        'Corporate CoreTech': 'Green',
        'Aviation': 'Orange',
        'Healthcare': 'Blue',
        'TSA - HealthCare': 'Blue',
        'GE Vernova': 'Red',
        'Gas Power': 'Red',
        'Unknown': 'Red',
    },
    'JoinedMethod': {
        'CREATED': 'Green',
        'INVITED': 'Orange',
        'MIGRATED': 'Blue',
        'PROVISIONED': 'Green',
        'Unknown': 'Red',
    },
    'JoinedTimestamp': {'Unknown': 'Red'},
    'Org': {
        'CC01': 'Magenta',
        'GECC': 'Green',
        'GEAV': 'Orange',
        'GEHC': 'Blue',
        'GEEN': 'Red',
        'Unknown': 'Red',
    },
    'Status': {
        'Active': 'Green',
        'ACTIVE': 'Green',
        'Building': 'Yellow',
        'Decommissioning': 'Orange',
        'Ejected': 'Red',
        'Suspended': 'Red',
    }
}

dm.print_table(data, colors_map=cMap)

## Print outcome
outcome = {}
if OUT_FILE:
    if OUT_FILE.endswith('.json'):
        put_json(OUT_FILE, data)
    else:    
        put_csv(OUT_FILE, data)
    outcome['Output File'] = OUT_FILE

outcome['Took'] = took_ts_hms(ts)
print()
print_color_dict(outcome)