#!/usr/bin/env python

import argparse
import concurrent.futures
import requests
import textwrap
import copy

from awsutil import *
from common import *
from copy import deepcopy
from util import *
from DataModels import *
from OneIDM import *
from validateutil import *

'''
# alias cmc="$HOME/whodat/src/cmc-api.py -a"

# Help
src/cmc-api.py -h

# Test
cmc 339713028896,931697245390,26277703191,853354396529,master-payer-av
cmc 339713028896,931697245390,26277703191,853354396529,master-payer-av -c  # --cider-block
cmc 339713028896,931697245390,26277703191,853354396529,master-payer-av -b  # --brief
cmc 339713028896,931697245390,26277703191,853354396529,master-payer-av -bc # --brief --cider-block
'''

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''\
    CMC API GET & PUT 
    ------------------------------------------------------------------------------------------
    '''),
    epilog=textwrap.dedent('''\
    Requiremnt: 
        - exported CMC_KEY as Env Var

    Read Usage Examples:
        cmc 'CSV of account_id or account_alias'

    Write Usage Examples:
        cmc account_id --update-bots GDBS-
        cmc account_id --eject-now
        cmc account_id --ejected-date 2024-02-07
        cmc account_id --reactivate
        cmc account_id --update-bu 'GE Vernova'
    
    GitHub: https://github.build.ge.com/GR2-0/Transitional-Master-Payer-Migration
    ''')
)

parser.add_argument('-a', '--account-id', metavar='', help="Csv of Account IDs and/or Aliases. Should be one AccountID for any CMC update!")
parser.add_argument('-b', '--update-bu', metavar='', help="Updated Business Uint")
parser.add_argument('-c', '--cider-block', action='store_true', help="Output PlanMan CIDR Block data")
parser.add_argument('-e', '--eject-now', action='store_true', help="Update CMC 'ejected_date' to now date!")
parser.add_argument('-f', '--brief', action='store_true', help="Output brief format. Requires OneIDM Access!")
parser.add_argument('-o', '--owner', action='store_true', help="Output Owner data. Requires OneIDM Access!")
parser.add_argument('-r', '--reactivate', action='store_true', help="Update CMC by removing 'ejected_date' & setting status to 'Active'!")
parser.add_argument('-d', '--ejected-date', metavar='', help="Update CMC 'ejected_date' to given date format of yyyy-mm-dd")
parser.add_argument('-s', '--serial', action='store_true', help="Output in the same order as input without parallell calls!")
parser.add_argument('-u', '--update-bots', metavar='', help="Csv list of BOT[+|-][, ...]")
parser.add_argument('-v', '--verbose', action='store_true', help="Increase verbosity & show data file")
options = parser.parse_args()
 

# Remove trailing comma
while options.account_id.endswith(','):
    options.account_id = options.account_id[0:-1]

ACCOUNTS = options.account_id.split(',')
MY_PATH = cur_dir()['Path']
PLANMAN_FILE = f'{MY_PATH}/../data/planman-blocks.json'
PLANMAN_MAP = f'{MY_PATH}/../data/planman-blocks.map.json'
PLANMAN_DATA = get_json(PLANMAN_FILE) if isFile(PLANMAN_FILE) else None

TODAY = get_today()

ENV = {
    'API': 'https://cmc.gecloud.io',
    'GR2': f"### GR2-0 / CMC Read API / {TODAY}",
    'DATAFOLDER': os.environ.get('DATAFOLDER', '/tmp/cmc'),
    'Title': f"CMC API / {TODAY}",
}

# Only Allow Single account CMC Update
UPDATE_ACTION = False
if options.update_bu or options.eject_now or options.reactivate or options.ejected_date or options.update_bots:
    UPDATE_ACTION = True
    if ',' in options.account_id:
        iSysExit(f"Invalid Usage! Only Single account CMC Update allowed!")

# Logs
iInfo('Args:', vars(options))

VAL = Validator()

CMC_KEY = os.environ.get('CMC_KEY')
try:
    db = DB(
        user=os.environ.get('USER'), 
        password=os.environ.get('PASS'), 
    )
except Exception as err:
    db = None
    iWarning('DB Connection Error!', err)

def activate_account(account_id:str):
    """Will remove ejected_date & sets status' to 'Active'"""
    CUR_DATA = get_cmc_data(account_id=account_id)
    data_update = {
        'status': 'Active',
        # 'ejected_date': '',
        # 'suspended_date': '',
    }

    NEW_DATA = CUR_DATA
    NEW_DATA.update(data_update)

    if isDebug():
        printll('CUR_DATA')
        ppjson(CUR_DATA)

        printll('NEW_DATA')
        ppjson(NEW_DATA)

    # Valid subset of changes
    res = put_cmc_data(account_id, data_update)

    return res

def update_bu(account_id:str, business_unit:str):
    """Update current account business_unit to given business_unit
    
    Args:
        business_unit (str): New Business Unit to update
    """
    CUR_DATA = get_cmc_data(account_id=account_id)
    data_update = {
        'business_unit':business_unit
    }

    NEW_DATA = CUR_DATA
    NEW_DATA.update(data_update)

    if isDebug():
        printll('CUR_DATA')
        ppjson(CUR_DATA)

        printll('NEW_DATA')
        ppjson(NEW_DATA)

    # Valid subset of changes
    res = put_cmc_data(account_id, data_update)

    return res

def eject_account(account_id:str, ejected_date:str):
    """Eject current account to given date
    
    Args:
        ejected_date (str): Excel format of date in days since 1900-01-01 in form of nnnnn
    """
    CUR_DATA = get_cmc_data(account_id=account_id)
    data_update = {
        'status': 'Ejected',
        'ejected_date': ejected_date
    }

    NEW_DATA = CUR_DATA
    NEW_DATA.update(data_update)

    if isDebug():
        printll('CUR_DATA')
        ppjson(CUR_DATA)

        printll('NEW_DATA')
        ppjson(NEW_DATA)

    # Valid subset of changes
    res = put_cmc_data(account_id, data_update)

    return res

def get_cmc_data(account_id:str):
    """Get CMC data for given account_id"""
    # Fix 12 digits AWS account_id
    if isInt(account_id) and len(account_id) < 12:
        account_id = account_id.rjust(12, '0')

    url = f"https://cmc.gecloud.io/account/{account_id}"
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
    
    if 'error' in response:
        response = {
            'account_id': account_id,
            'account_name': account_id,
            'connected_region': 'Unknown',
            'status': 'Unknown',
            'provision_date': 'Unknown',
            'migration_date': 'Unknown',
            'suspended_date': 'Unknown',
            'ejected_date': 'Unknown',
            'business_unit': 'Unknown',
            'owner': 'Unknown',
            'sku': 'External Account',
        }

    return response

def put_cmc_data(account_id, payload):
    """Update CMC with json payload data
    
    payload (dict): json

    """
    url = f"https://cmc.gecloud.io/account/{account_id}"
    headers = {
        'Connection': 'keep-alive', 
        'Content-Type': 'application/json',     # required
        'x-api-key': CMC_KEY,                   # required
        'Accept-Encoding': 'gzip, deflate', 
        # 'Cache-Control': 'no-cache', 
        # 'cache-control': 'no-cache', 
        'Host': 'cmc.gecloud.io', 
        'Accept': '*/*'
    }
    
    payload = json.dumps(payload)
    response = requests.request("PUT", url, headers=headers, data=payload, verify=True)
    response = response.json()

    if response.get('error'):
        iError(f"Unable to Update CMC :: {response.get('error')}")

    return response

def get_cider_block(account_id):
    """Get PlanMan CIDER Block Data for given AccountID or AccountName"""
    res = ''
    if not PLANMAN_DATA:
        iWarning(f"PlanMan data is empty! See if '{PLANMAN_FILE}' file exist and is a valid json!")
        return res
    
    # Try to filter for AccountID or AccountName
    for rs in PLANMAN_DATA['Items']:
        if rs.get('AccountId') == account_id or rs.get('AccountName') == account_id:
            res = rs.get('CidrBlock')

    return res
        

# Process CMC Data
iMap = {
    'account_id': 'AccountID',
    'account_name': 'AccountAlias',
    'connected_region': 'Region',
    'status': 'Status',
    'cider': 'PlanMan',
    'provision_date': 'Provision',
    'migration_date': 'Migration',
    'ejected_date': 'Ejection',
    'suspended_date': 'Suspension',
    'business_unit': 'BusinessUnit',
    'owner': 'Owner',
    'sku': 'SKU',
}

lenMap = {
    'provision_date': 10,
    'migration_date': 10,
    'suspended_date': 10,
    'ejected_date': 10,
}

cMap = {
    'Status': {
        'Active': 'iGreen',
        'Building': 'iYellow',
        'Decommissioning': 'iMagenta',
        'Ejected': 'iRed',
        'Suspended': 'iRed',
        'Unknown': 'iRed',
    },
    'Region': {'Unknown': 'iRed'},
    'SKU': {
        'External Account': 'iRed',
        'Standard': 'iBlue',
        'Limited': 'iGreen',
    },
    'BusinessUnit': {
        'Healthcare': 'iBlue',
        'GE Vernova': 'iGreen',
        'SMO': 'iYellow',
        'Unknown': 'iRed',
    },
    'Provision':    {'N/A': 'iGray', 'UNKNOWN': 'iGray', 'Unknown': 'iRed'},
    'Migration':    {'N/A': 'iGray', 'UNKNOWN': 'iGray', 'Unknown': 'iRed'},
    'Suspension':   {'N/A': 'iGray', 'UNKNOWN': 'iGray', 'Unknown': 'iRed'},
    'Ejection':     {'N/A': 'iGray', 'UNKNOWN': 'iGray', 'Unknown': 'iRed'},
    'Owner':        {'Unknown': 'iRed'},
}

def extract_cmc_data(ACCOUNTS):
    # Data Model
    res = []
    data = []

    for account_id in ACCOUNTS:
        res_data = get_cmc_data(account_id)
        res.append(res_data)

        if options.cider_block:
            res_data['cider'] = get_cider_block(res_data['account_id'])

        dataRset = {}
        owner_names = {}
        for key in iMap.keys():
            if res_data.get(key):
                if key in lenMap:
                    # Limit lenght if key is in lenght limit map
                    dataRset[iMap[key]] = res_data.get(key, '')[0:lenMap[key]]
                else:    
                    dataRset[iMap[key]] = res_data.get(key, '')

        # Extract Owner Name from OneIDM
        if options.owner or options.brief:
            if not db:
                iWarning('DB Connection is not available!')
                
            try:
                owner_names = []
                owner = res_data.get('owner', '').strip()
                if not owner.endswith(';'): owner += ';'
                query = owner.split(';')
                owners = db.get_users(query)

                for rs in owners['Data']:
                    iDebug(f"({dataRset.get('AccountID')}) [{dataRset.get('AccountAlias')}] Owner: {rs.get('GU_EMAIL_DISP')}")
                    owner_names.append(rs.get('GU_EMAIL_DISP'))

                dataRset['OwnerName'] = owner_names
            except Exception as err:
                iWarning(f'OneIDM Get Owner API has error!', err)

        data.append(dataRset)

    return res, data

# Data Model
res = []
data = []

# Get CMC Data
ts = get_ts()
if options.serial:
    res, data = extract_cmc_data(ACCOUNTS)

else:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for account_id in ACCOUNTS:
            futures.append(
                executor.submit(
                    get_cmc_data,
                    account_id
                ) 
            )

        for future in concurrent.futures.as_completed(futures):
            try:
                future_data = future.result()
                if future_data:
                    res.append(future_data)

                if options.cider_block:
                    future_data['cider'] = get_cider_block(future_data['account_id'])

                # Process Data
                dataRset = {}
                owner_names = {}
                for key in iMap.keys():
                    if future_data.get(key):
                        if key in lenMap:
                            # Limit lenght if key is in lenght limit map
                            dataRset[iMap[key]] = future_data.get(key, '')[0:lenMap[key]]
                        else:    
                            dataRset[iMap[key]] = future_data.get(key, '')

                # Extract Owner Name from OneIDM
                if options.owner or options.brief:
                    if not db:
                        iWarning('DB Connection is not available!')
                        
                    try:
                        owner_names = []
                        owner = future_data.get('owner', '').strip()
                        if not owner.endswith(';'): owner += ';'
                        query = owner.split(';')
                        owners = db.get_users(query)

                        for rs in owners['Data']:
                            iDebug(f"({dataRset.get('AccountID')}) [{dataRset.get('AccountAlias')}] Owner: {rs.get('GU_EMAIL_DISP')}")
                            owner_names.append(rs.get('GU_EMAIL_DISP'))

                        dataRset['OwnerName'] = owner_names
                    except Exception as err:
                        iWarning(f'OneIDM Get Owner API has error!', err)

                data.append(dataRset)
            except Exception as err:
                iWarning(f'CMC API has error!', err)

printll(f"{ENV['GR2']} ")

dm = DataModel()
dm.print_table(data=data, colors_map=cMap)

if options.brief:
    printll(f"{ENV['GR2']} / Brief Format")
    for rs in data:
        region = f", in {rs.get('Region')}" if rs.get('Region') else ''
        owners_sso = rs.get('Owner', '').split(';')
        owners_names =  rs.get('OwnerName')
        if len(owners_sso) != len(owners_names):
            iWarning(f"Owner SSO  ({len(owners_sso)}): {owners_sso}")
            iWarning(f"Owner Name ({len(owners_names)}): {owners_names}")

        owners_list = []
        for i, sso in enumerate(owners_names):
            owners_list.append(sso.replace(find_between(sso), owners_sso[i]))

        scolor = 'iRed'
        if rs.get('Status') == 'Active': scolor = 'iGreen'
        if rs.get('Status') == 'Building': scolor = 'iYellow'

        print(
            f"({rs.get('AccountID')}) [{rs.get('AccountAlias')}] is {iColor(rs.get('Status'), scolor)}{region},", 
            f"{iColor(rs.get('SKU'), 'iBlue')},",
            f"for {iColor(rs.get('BusinessUnit'), 'iYellow')},",
            f"Owned by {iColor(owners_list, 'iYellow')}"
        )

ENV['Took'] = took_ts(ts)
print()
print_color_dict(ENV)

# read is list and write is dict
# following is update & write logic hence res is a dict not a list anymore
if isinstance(res, list) and len(res) == 1:
    res = {'CMC': res[0]} 

if options.update_bu:
    update_bu(account_id=options.account_id, business_unit=options.update_bu)

if options.update_bots:
    res['Backup'] = get_cmc_data(account_id=options.account_id)
    OLD_DATA = res['Backup']

    OLD_BOTS = OLD_DATA['add_ons']['Bots']
    iInfo('OLD_BOTS', OLD_BOTS)
    NEW_BOTS = copy.deepcopy(OLD_BOTS)

    # Processing input
    bots = options.update_bots.split(',')
    iTrace('--update-bots Split:', bots)
    for bot in bots:
        iTrace('bot read :', bot)
        state = 'disabled' if bot[-1] == '-' else 'enabled'
        iInfo('desired state:', state)
        bot = bot[0:-1] if bot[-1]  in ['-', '+'] else bot
        iInfo('bot update:', bot)

        if OLD_BOTS[bot] != state:
            NEW_BOTS[bot] = state

            iTrace('OLD_BOTS', OLD_BOTS)
            iTrace('NEW_BOTS', NEW_BOTS)

            iWarning('Has a change - update')
            res['Update'] = put_cmc_data(
                account_id=options.account_id, 
                payload={
                'add_ons': {
                    'Bots': NEW_BOTS
                }
            })
            printll(f"{ENV['GR2']} / CMC Update")
            if isCodeBuild() or options.verbose or isDebug():
                ppjson(res['Backup'])

            res['Final'] = get_cmc_data(account_id=options.account_id)
            printll(f"{ENV['GR2']} / CMC Final")
            if isCodeBuild() or options.verbose or isDebug():
                ppjson(res['Final'])

if options.eject_now:
    EJECT_DTE = get_dt()[0:10]
    iWarning('Eject on ::', EJECT_DTE)

    res['Ejection'] = eject_account(account_id=options.account_id, ejected_date=EJECT_DTE)
    printll(f"{ENV['GR2']} / CMC Ejection on {EJECT_DTE}")
    if isCodeBuild() or options.verbose or isDebug():
        ppjson(res['Ejection'])

    res['Final'] = get_cmc_data(account_id=options.account_id)
    printll(f"{ENV['GR2']} / CMC Final")
    if isCodeBuild() or options.verbose or isDebug():
        ppjson(res['Final'])

if options.ejected_date:
    res['Backup'] = get_cmc_data(account_id=options.account_id)

    TODAY_DTE = get_dt()[0:10]
    EJECT_DTE = options.ejected_date

    iWarning('Today is ::', TODAY_DTE)
    iWarning('Eject on ::', EJECT_DTE)

    CUR_EJC_DATE = res['Backup'].get('ejected_date')
    NEW_EJC_DATE = date2excel(options.ejected_date)

    if EJECT_DTE > TODAY_DTE:
        iWarning('We shall not have ejected_date in the future!')
        iWarning('Today is ::', TODAY_DTE)
        iWarning('Eject on ::', EJECT_DTE)
    else:
        res['Ejection'] = eject_account(account_id=options.account_id, ejected_date=EJECT_DTE)
        printll(f"{ENV['GR2']} / CMC Ejection on {EJECT_DTE}")
        if isCodeBuild() or options.verbose or isDebug():
            ppjson(res['Ejection'])

        res['Final'] = get_cmc_data(account_id=options.account_id)
        printll(f"{ENV['GR2']} / CMC Final")
        if isCodeBuild() or options.verbose or isDebug():
            ppjson(res['Final'])

if options.reactivate:
    activate_account(account_id=options.account_id)

# Show Updated CMC Data 
if UPDATE_ACTION:
    res = []
    data = []
    res, data = extract_cmc_data(ACCOUNTS)

    ENV['GR2'] = f"### GR2-0 / {iColor('CMC Write API', 'iYellow')} / {TODAY}"
    printll(f"{ENV['GR2']} ")

    dm = DataModel()
    dm.print_table(data=data, colors_map=cMap)

# Verbose Output
if options.verbose or isDebug():
    printll(f"{ENV['GR2']} / ResFile")
    ppyamlc(res)

    printll(f"{ENV['GR2']} / Environment Info")
    ppyamlc(ENV)
    printll(f"{ENV['GR2']} / ResFile")
    ppyamlc(res)

    printll(f"{ENV['GR2']} / Environment Info")
    ppyamlc(ENV)
