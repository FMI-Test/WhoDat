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
    GET IAM Roles & Their Trust Relashionships for Given Input File
    ------------------------------------------------------------------------------------------
    '''),
    epilog=textwrap.dedent('''\
    Requirement Once:
        - mkdir -p /tmp/oneidm'
        - mkdir -p __cache__

    Usage Examples:
    
    Batch:
        --input-file /tmp/oneidm/jump-roles.txt --output-path

    GitHub: https://github.build.ge.com/GR2-0/Transitional-Master-Payer-Migration
    ''')
)

parser.add_argument('-d', '--debug', action='store_true', help='Disable multi threading for debug ')
parser.add_argument('-i', '--input-file', required=True, help='Accounts File is list of AWS accounts one account id per line. Lines starting with # will be excluded')
parser.add_argument('-o', '--output-path', metavar='', default='/tmp/oneidm', help='Output Path')
parser.add_argument('-v', '--verbose',  action='store_true', help="Increase verbosity & show data file")
options = parser.parse_args()

INPUT_FILE = options.input_file
accounts = file_read_input_file(INPUT_FILE)

DATAFOLDER = os.environ.get('DATAFOLDER', options.output_path)
ENV = {
    'GR2': f"### GR2-0 / IAM Roles & Trust Extract",
    'DATAFOLDER': DATAFOLDER,
    'Title': 'Extract IAM Roles & Trust',
    'Task': 'Extract IAM Roles & Trust' 
}

rWidth = 132

ppwide(ENV['GR2'], width=rWidth)

# Logs
print('Args:', iColor(vars(options), 'iYellow'))
print('Input File:', iColor(INPUT_FILE, 'iYellow'))

VAL = Validator(ENV['Task'])

ts = get_ts()

# Accounts
accounts_count = len(accounts)
included_accounts = []
excluded_accounts = []

for account in accounts:
    if not account:
        continue
    if account.get('Comment'):
        excluded_accounts.append(account.get('Comment'))
    else:
        included_accounts.append(account)

ppwide(f"{ENV['GR2']} ({len(included_accounts)}/{accounts_count}) Accounts. Comments ({len(excluded_accounts)}/{accounts_count})", width=rWidth)

print()
ppwide(f"{ENV['GR2']} / Commented Lines ({len(excluded_accounts)})", width=rWidth)
for i, comment in enumerate(excluded_accounts):
    i += 1
    row = lspace(i,4)
    print(f"{row}.{len(excluded_accounts)}. {iColor(comment,'iGreen')}")

print()
ppwide(f"{ENV['GR2']} / Included Accounts ({len(included_accounts)})", width=rWidth)
dm = DataModel()
dm.print_table(included_accounts)

# Multi-thread
def process_role(account_dict, role, counter):
    """Process role
    
    Params:
        account_dict (dict): dict of account info
        role (str): role to process
        i (int): current account index
        count (int): count of all ccounts
        j (int): current role index
    """
    res = {}
    for key in account_dict.keys():
        res[key] = account_dict[key]

    res['Errors'] = []
    res['RolesTrusts'] = []
    account = res['AccountId']

    role['DL'] = []
    ACC_FMT = f"({res['AccountId']}) [{res['AccountName']}]"
    action  = 'Get IAM Role Trust Relashionships'
    iTrace(f"  {counter}. {ACC_FMT} DL {iColor(action, 'Yellow')}")
    
    outcome = SUCCESS if role else FAILURE
    VAL.put(task=action, outcome=outcome, note=f"Get IAM Role Trust Data")

    dl_List = []
    trustRs = {}
    dl_prefix = "@GE GOVAWS_" if isGovSts() else "@GE AWS_"
    for trustPolicies in role['AssumeRolePolicyDocument']['Statement']:
        trustPolicies = trustPolicies['Principal']

        for key in trustPolicies.keys():
            if key not in trustRs:
                trustRs[key] = []

            if isinstance(trustPolicies[key], str):
                if trustPolicies[key] not in trustRs[key]:
                    trustRs[key].append(trustPolicies[key])

            if isinstance(trustPolicies[key], list):
                for item in trustPolicies[key]:
                    if item not in trustRs[key]:
                        trustRs[key].append(item)

            roleName = role['RoleName']
            pathName = role['Path'][1:] if len(role['Path'] ) > 1 else ""
            console_access = "Yes"
            dl_name = ''
            notes = ''
            principal = key
            entity = trustPolicies[key]

            # For each role:principal:entity, we add a row to the workbook.
            # But first we categorize it, and attempt to fill in info for the variables above

            if principal == "Service":
                console_access = "No"

            if principal == "Federated":

                if entity == "cognito-identity.amazonaws.com":
                    console_access = "No"

                if "oidc-provider/oidc.eks" in str(entity):
                    console_access = "No"

                if "saml-provider" in str(entity):
                    dl_name = dl_prefix + pathName + roleName + "_" + account

                notes += "DL listed. IAM account extract in scope of the AWS script, please check trust policy showing federated access/ SAML integration. "

            if principal == "AWS":

                if entity == "*":
                    notes += "Wildcard * in Trust Policy: Needs Review. "
                    
                # https://docs.aws.amazon.com/govcloud-us/latest/UserGuide/using-govcloud-arns.html
                if "arn:aws:iam:" in entity or "arn:aws-us-gov:iam:" in entity: # Update for GovCloud
                    trusted_acct = entity.split(':')[4]
                    trusted_role = entity.split(':')[5]

                    if trusted_acct == account and trusted_role == 'root':
                        notes += "IAM extract & credentials report of the account included in the AWS script. "
                    elif trusted_acct in accounts and trusted_role == 'root':
                        notes += "IAM extract & credentials report of the account included in the AWS script. See sheet: " + str(trusted_acct) + ". "
                    elif trusted_acct != account and trusted_acct in accounts:
                        notes += "IAM extract & credentials report of the account included in the AWS script. See sheet: " + str(trusted_acct) + ". "
                    elif trusted_acct != account:
                        notes += "Trusted entity is in another account. See account: " + str(trusted_acct) + ". "

                    if "role/" in trusted_role:

                        trusted_role = trusted_role.replace("root/","")
                        dl_name = dl_prefix + trusted_role + "_" + trusted_acct

                        # Update
                        trusted_role = trusted_role.replace("role/","")
                        dl_name = dl_prefix + trusted_role + "_" + trusted_acct

            ## Debug
            if options.debug or isDebug() or options.verbose:
                debugData = {
                    'Counter': counter,
                    'Role': role['Path'] + role['RoleName'],
                    'ConsoleAccess': console_access,
                    'principal': principal,
                    'entity': entity,
                }
                ppwide(f"Debug {role['Path']}{role['RoleName']}", delimeter='-')
                print_color_dict(debugData)
                wline()

            # Store DLs
            role['DL'] = dl_name
            role['ConsoleAccess'] = console_access
            if dl_name:
                print(f"  {counter}. {ACC_FMT} DL {iColor(dl_name, 'Yellow')}")
                if dl_name not in dl_List:
                    dl_List.append(dl_name)

    iDebug(f"{account}: {trustRs}")
    role['DL'] = dl_List
    role['TrustRelashipships'] = trustRs

    res['RolesTrusts'].append(role)

    return res

res = []

incl_count = len(included_accounts)
print()
ppwide(f"{ENV['GR2']} / {incl_count}/{accounts_count}", width=rWidth)

'''
{
    "AccountId": "556003251088",
    "AccountName": "gecirt",
    "Region": "us-east-1",
    "SKU": "GR-Standard-AWS",
    "BU": "Corporate-Cyber",
}
'''
accLen = 12
roleLen = 12
for i, acc_data in enumerate(included_accounts):
    i += 1
    account = acc_data['AccountId']
    sess = get_session(account, dont_quit=True, role='cs/p-support')
    roles = []

    Marker = None
    MaxItems = 1000
    # iam:ListRoles
    client = sess.client('iam')
    while True:
        try:
            if Marker is None:
                response = client.list_roles(
                    MaxItems=MaxItems
                )
            else:
                response = client.list_roles(
                    Marker=Marker,
                    MaxItems=MaxItems
                )
            # Consolidated Result
            roles.extend(response['Roles'])

        except Exception as err:
            iWarning(f"Access Error! ({acc_data['AccountId']}) [{acc_data['AccountName']}]", err)
            if 'ExpiredToken' in str(err):
                iSysExit(f'Credential Error! ExpiredToken!')
    
            continue

        Marker = response.get('Marker')

        if Marker is None:
            break

    # Count Account & Roles
    accCount = len(included_accounts)
    roleCount = len(roles)

    if options.debug:
        for j, role in enumerate(roles):
            j += 1
            counter = 'Account ' + lspace(f"{i:,}/{accCount:,}", accLen) + '  :: Role ' + lspace(f"{j:,}/{roleCount:,}", roleLen)
            rs = process_role(acc_data, role, counter)
            res.append(rs)

    if not options.debug:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for j, role in enumerate(roles):
                j += 1
                counter = 'Account ' + lspace(f"{i:,}/{accCount:,}", accLen) + '  :: Role ' + lspace(f"{j:,}/{roleCount:,}", roleLen)
                futures.append(
                    executor.submit(
                        process_role,
                        acc_data,
                        role,
                        counter
                    ) 
                )

            for future in concurrent.futures.as_completed(futures):
                try:
                    data = future.result()
                    res.append(data)

                except Exception as err:
                    iWarning(f'Process Role has Error!', err)

TAB_FILE = options.input_file.replace('/', ' ').split(' ')[-1].replace('.tab', '')
dl_list = []
dl_data = []
for rs in res:
    if not isinstance(rs, dict) or not rs.get('RolesTrusts'):
        continue

    for trust_entitiese in rs['RolesTrusts']:
        dls = trust_entitiese.get('DL', [])
        iDebug('DL:', dls)
        for dl in dls:
            if dl:
                if dl not in dl_list:
                    dl_list.append(dl)

                dl_data.append({
                    'AccountId': rs['AccountId'],
                    'AccountName': rs['AccountName'],
                    'Region': rs['Region'],
                    'SKU': rs['SKU'],
                    'BU': rs['BU'],
                    'DL': dl,
                })

# Store Results
TODAY = get_today()
OUT_FILE = f"{DATAFOLDER}/{TAB_FILE}-roles-trusts.json"
DL_LIST_FILE = f"{DATAFOLDER}/{TAB_FILE}-dl-list.json"
JSON_FILE = f"{DATAFOLDER}/{TAB_FILE}-gid-data.json"
CSV_FILE = f"{DATAFOLDER}/{TAB_FILE}-gid-data.csv"

put_json(OUT_FILE, res) 
put_json(DL_LIST_FILE, dl_list) 
put_json(JSON_FILE, dl_data) 
put_csv(CSV_FILE, dl_data) 

# Verbose Output
if options.verbose:
    printll(f"{ENV['GR2']} / ResFile", width=rWidth)
    ppyamlc(res)

    printll(f"{ENV['GR2']} / Environment Info", width=rWidth)
    ppyamlc(ENV)
    printll(f"{ENV['GR2']} / ResFile", width=rWidth)
    ppyamlc(res)

if VAL.get_outcome() == FAILURE:
    printll(f"{ENV['GR2']} / Outcome Faliures", width=rWidth)
    VAL.list_failures()

printll(f"{ENV['GR2']}  / Outcome: {VAL.get_outcome().upper()}", width=rWidth)
# VAL.print_outcome()

# List DL
dm = DataModel()
# Colors Map
cMap = {
    'BU': {
        'Corporate-CoreTech': 'Blue',
        'Corporate-Cyber': 'Green',
    },
    'DL': {
        '@': 'Yellow',
    }
}
dm.print_table(dl_data, colors_map=cMap)

took = took_ts_hms(ts)
print()
print('Took           :', iColor(took, 'iYellow'))
print('Input File     :', iColor(INPUT_FILE, 'iYellow'))
print('Data Output    :', iColor(OUT_FILE, 'iYellow'))
print('DL List JSON   :', iColor(DL_LIST_FILE, 'iYellow'))
print('DL Output JSON :', iColor(JSON_FILE, 'iYellow'))
print('DL Output CSV  :', iColor(CSV_FILE, 'iYellow'))

# printhh('Copy Below Code to Bulk Process Above DL List to Extract Groups & Users Info', width=rWidth)
# lines = [
#     '''# Process Groups & Build User Cache Data''',
#     '''time while read -r line; do whois "$line"; done < <(cat DL_LIST_FILE | jq -r . | tr -d '[],"' | awk '{print $1, $2}')''',
#     '''''',
#     '''# Process DL Groups & Users Data''',
#     '''src/oneidm-groups-report.py --input-file DL_LIST_FILE''',
#     '''''',
# ]
# for line in lines:
#     line = line.replace('DL_LIST_FILE', DL_LIST_FILE)
#     color = 'iGreen' if line.startswith('#') else 'iYellow'
#     print(iColor(line, color))