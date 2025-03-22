#!/usr/bin/env python

# Description: export details of IAM roles in accounts hosting SoX applications
# GitHub: https://github.build.ge.com/503345432/Cloud-Quarterly-Access-Review
import argparse
import boto3
import botocore
import datetime
import json
import logging
import os
import platform
import sys
import textwrap
import xlsxwriter

from datetime import date, datetime, timezone, timedelta
from util import *
from DataModels import *

if platform.system() == 'Windows':
    from colorama import just_fix_windows_console
    just_fix_windows_console()

LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
BU_BRAND = os.environ.get('BU_BRAND', '# CoreTech / Compliance / ') # Branding for report Titles
BU_TRAIL = os.environ.get('BU_TRAIL', '-')  # Branding for report Titles trailing charater
BU_WIDTH = os.environ.get('BU_WIDTH', 120)  # Branding Titles width
DATAFOLDER = os.environ.get('DATAFOLDER', '')
INPUT_FILE = os.environ.get('INPUT_FILE', '')

bot_list = ["cs/pct-naapi-snaapi","cs/config-service-role","cs/p-readerbots","cs/p-actionbots","cs/dont-taze-me-role","cs/ge-cirt-analysis","cs/ge-cirt-auto","cs/p-mc-lawgiver","cs/p-cs-lawgiver","cs/p-lawmaker","ge-cirt-auto"]
exclustion_list = [] + bot_list


def parse_args():
    description = """\
    This program uses aws profiles to assume roles accross multiple accounts. 
    Use the bulk_login feature of gossamer3 (https://github.com/GESkunkworks/gossamer3) 
        to produce a correctly formatted aws credentials file.     
        In your gossamer3 roles config file, name profiles {acct_number}/role. 
    
    Output will be saved as CSV files for credentials in your working directory for each AWS Account.
    Output will be saved as xlsx files for SOX report in your working directory for bulk AWS Accounts.

    Important:   
        - In your gossamer3 roles config file, use: profiles: {acct_number}/role 
        - Output will be saved as individual ".csv" files for credentials per account.
        - Output will be saved as consolidate ".xlsx" files for SOX reports with one sheet per account.

    DL Extract:
        ACC=$(cat ~/gos3-qar1.yml | grep 'profile:' | grep -v '#' | tr '/' ' ' | awk '{print $2}');ACC=$(echo $ACC | tr ' ' ',')
        ../../qar_utility.py p-engineering $ACC -v
        ../../qar_utility.py p-engineering $ACC -lips


    Examples:
        # Alteryx format Credential, Local Users and IAM Roles report with progressbar and sorted AWS Accounts
        python ..\qar_utility.py bu-iam-admin '123456789012,001234567890' -aclips

        # Credential, Local Users and IAM Roles report with progressbar and sorted AWS Accounts
        python ..\qar_utility.py bu-iam-admin '123456789012,001234567890' -clips

        # Credential report with sorted AWS Accounts
        python ..\qar_utility.py bu-iam-admin '123456789012,001234567890' -cs

        # Local Users report with dot progressbar
        python ..\qar_utility.py bu-iam-admin '123456789012,001234567890' -lps

        # IAM Roles report wiht dot progressbar
        python ..\qar_utility.py bu-iam-admin '123456789012,001234567890' -ips

        # IAM Roles report
        python ..\qar_utility.py bu-iam-admin '123456789012,001234567890' -i
    """

    epilog = """\
    Important:
        - Always wrap your AWS Acoounts in single or double qoute. i.e. '123456789012,001234567890'
        - Always include all AWS accounts for all reports otherwise your .xlsx SOX reports will be 
          overwritten with the accounts list of last run and it would be incomplete.
        - Verify if you have "n" accounts then there are "n" ".csv' files for credential reports.
        - Verify if you have "n" accounts then there are "n" sheets on both ".xlsx" SOX files.
        - Take snapshots of execution and store it with other reports as proof of work.
        - If your reports is larger than one page copy it from console, paste it in an editor and
            print it as pdf in the same reporting folder:
            - Nmae the first run '1 Run Full QAR Report.pdf'
            - Name the 2nd run for verfication '2 Re-run Credential Report & Verification.pdf'

    GitHub: https://github.build.ge.com/503345432/Cloud-Quarterly-Access-Review
        """

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(description),
        epilog=textwrap.dedent(epilog)
    )

    parser.add_argument("role",     help="The role to assume with STS.", type=str, default='p-engineering', nargs='?')
    parser.add_argument("accounts", help="A comma delimeted list of AWS accounts wraped in qoutes.", type=str, nargs='?')
    parser.add_argument("-a", "--alteryx",      action="store_true", help="Supports Alteryx script to format the data to be CMT uploadable")
    parser.add_argument("-c", "--credentials",  action="store_true", help="Exports .csv Credential Report for each AWS account")
    parser.add_argument("-l", "--localusers",   action="store_true", help="Exports .xlsx SOX report of all local users and their inline and managed policies")
    parser.add_argument("-i", "--iamroles",     action="store_true", help="Exports .xlxs SOX report of all IAM roles and their trust principals")
    parser.add_argument("--datafolder", metavar='', help="Data Folder to store the output files")
    parser.add_argument("--input-file", metavar='', help="Accounts input file")
    parser.add_argument("-p", "--progressbar",  action="store_true", help="Shows dot [.] progress bar when used with -l or -i")
    parser.add_argument("-s", "--sortaccounts", action="store_true", help="Sorts AWS Accounts when used with -c, -l or -i")
    parser.add_argument("-v", "--verify",       action="store_true", help="Verify Access to target accounts")

    return parser.parse_args()

def get_datetime():
    return datetime.now()

def get_datetimeutc():
    return datetime.now(timezone.utc).isoformat()

def progress_print(counter=7, indent=7, limit=BU_WIDTH, char='.'):
    if counter == indent:
        sys.stdout.write(' '*indent)

    counter += 1
    if counter > limit:
        print()
        counter = indent
    else:
        sys.stdout.write('.')

    sys.stdout.flush()
    return counter

def rspace(string, width=3):
    return str(string) + ' '*(width-len(str(string))) if len(str(string)) < width else string

def lspace(string, width=3):
    return ' '*(width-len(str(string))) + str(string) if len(str(string)) < width else string

def to_len(string=BU_TRAIL, delimeter=BU_TRAIL, width=BU_WIDTH):
    """Returns 'string' with following 'delimeter' up to given 'width' 
    
    Params:
        string    (str): Optional string. default -
        delimeter (str): Optional string. default -
        width     (int): Optional width. default 120
    """
    string = ' ' if len(string) == 0 else string
    delimeter = ' ' if len(delimeter) == 0 else delimeter
    spc = string if string == delimeter else ' '
    return string + spc + delimeter*int(width-len(string)/len(delimeter)) if len(string) < width else string

def to_space(string, width=3):  # Leading space to width i.e. to_space(1, 3) returns '  1'
    return ' '*(width-len(str(string))) + str(string) if len(str(string)) < width else string

def ppwide(string=BU_TRAIL, delimeter=BU_TRAIL, width=BU_WIDTH):
    """Prints 'string' with following 'delimeter' up to given 'width' 
    
    Params:
        string    (str): Optional string. default -
        delimeter (str): Optional string. default -
        width     (int): Optional width. default 120
    """
    if string != delimeter: string = BU_BRAND + string
    print(to_len(string, delimeter, width))

def get_dt_local():
    """Returns datetime in ISO format"""
    return datetime.now().isoformat()

def get_ts():
    return datetime.timestamp(datetime.now())

def fmt_ts(ts, digits=3):
    """Returns n digits decimal points - default microseconds - 6"""
    return float(format(ts, f'.{digits}f'))

def took_ts(ts):
    """Returns duration from input ts with 6 digit percision in seconds
    Parsms:

        ts (float): timestamp which was created earlier by calling get_ts()
    """
    return float(format(get_ts()-ts, '.3f'))

def pretty_json(jsonData=[]):
    return json.dumps(jsonData, indent=4, default=str)

def get_json(my_file:str):
    """Returns json file"""
    try:    
        with open(my_file, 'r') as json_file:
            res = json.load(json_file)
        return res
    except Exception as err:
        logging.error(f"get_json({my_file}) {str(err)}")

def put_json(my_file, my_data, minify=False):
    try:    
        with open(my_file, 'w') as json_file:
            if minify:
                json.dump(my_data, json_file, default=str)
            else:
                json.dump(my_data, json_file, indent=4, default=str)
        return False
    except Exception as err:
        logging.error(f"put_json({my_file}, my_data) {str(err)}")
    return True

def bash_color(string, color):
    """Adds shell color to given string ends with reset color

    Params:
        string (str): Input
        color  (str): Color name. Case insensitive.
    
    Color List:
        Black, Gray, Red, Green, Yellow, Blue, Magenta, Cyan, White
    """
    color = color.title() 

    if platform.system() == 'Darwin':
        rs = {
            'NC': '\e[0m',         # Text Reset
            'Black': '\e[0;30m',   # Black
            'Gray': '\e[0;90m',    # Gray
            'Red': '\e[0;91m',     # Red
            'Green': '\e[0;92m',   # Green
            'Yellow': '\e[0;93m',  # Yellow
            'Blue': '\e[0;94m',    # Blue
            'Magenta': '\e[0;95m', # Magenta
            'Cyan': '\e[0;96m',    # Cyan
            'White': '\e[0;97m',   # White
        }
    else:
        rs = {
            'NC': '\033[0m',         # Text Reset
            'Black': '\033[0;30m',   # Black
            'Gray': '\033[0;90m',    # Gray
            'Red': '\033[0;91m',     # Red
            'Green': '\033[0;92m',   # Green
            'Yellow': '\033[0;93m',  # Yellow
            'Blue': '\033[0;94m',    # Blue
            'Magenta': '\033[0;95m', # Magenta
            'Cyan': '\033[0;96m',    # Cyan
            'White': '\033[0;97m',   # White
        }

    if color in rs:
        return f"{rs[color]}{string}{rs['NC']}"
    else:
        return string

def sanity_check(accounts):
    ppwide(f'Sanity-Check / Accounts ({len(accounts)})')

    dt = get_dt_local()[0:24].replace(':', '-')
    file = f'0-access-report-{dt}.json'
    res = {
        'AccessDenied': [],
        'AccessGranted': []
    }

    #https://docs.aws.amazon.com/IAM/latest/UserGuide/example_iam_GenerateCredentialReport_section.html
    for rowNum, acc in enumerate(accounts):
        rowNum += 1
        accountAlias = ''

        # Print console log
        try:
            session = boto3.session.Session(profile_name=f"{acc}/"+args.role)
            iam = session.client('iam')
            try:
                accountAlias = iam.list_account_aliases()['AccountAliases']
                if len(accountAlias) > 0:
                    logging.info(f"QAR / Sanity-Check / IAM / Account Alias / ({acc}) {accountAlias}")
                else:
                    logging.warning(f"QAR / IAM / Account Alias / ({acc}) {accountAlias} Alias not Found!")
                msg = bash_color('AccessGranted', 'Green')
                res['AccessGranted'].append(acc)
            except Exception as err:
                res['AccessDenied'].append(acc)
                msg = bash_color('AccessDenied', 'Red')
            accountAlias = str(accountAlias)
        except Exception as err:
            msg = bash_color('AccessDenied', 'Red')
            res['AccessDenied'].append(acc)
            logging.warning(str(err))
    
        spc = rspace(msg, 15)
        myMsg = f'{to_space(rowNum,3)}. Access Verification {spc} ({acc}) {accountAlias}'
        print(f'  {myMsg}')

    put_json(file, res)

    return True if len(res['AccessDenied']) == 0 else False  

def get_out_files(datafolder, input):
    """Return auto-generated output files form DATAFOLDER & INPUT_FILE"""
    out_file = input.replace('.tab','').replace('inputs/', f'{datafolder}/') + '-LS-Credentials-Report'
    return {
        'csv': out_file + '.csv',
        'json': out_file + '.json',   
    }

def export_iam_roles(accounts, progressBar=False, alteryxSupport=False):

    # list & store all trusted_acct to catch suspended accounts
    trusted_accounts_list = []
    trusted_accounts_file = 'trusted_accounts_list.json'
    if DATAFOLDER: trusted_accounts_file = f'{DATAFOLDER}/{trusted_accounts_file}'

    # create xlsx file
    dt = get_dt_local()[0:24].replace(':', '-')
    dl_file = f'sox_iam_roles_dls-{dt}.json'
    if DATAFOLDER: dl_file = f'{DATAFOLDER}/{dl_file}'

    dl_data = []
    filename = 'sox_iam_roles_export.xlsx'
    if DATAFOLDER: filename = f'{DATAFOLDER}/{filename}'

    workbook = xlsxwriter.Workbook(filename)
    rolesCountTotal = 0
    rowTotal = 0

    # Add a bold with gray background format for header cells
    header_format = workbook.add_format()
    header_format.set_bold(True)
    header_format.set_bg_color('#D9D9D9')

    highlight_format = workbook.add_format()
    highlight_format.set_bg_color('#FFFF00')

    # Iterate through each AWS Account
    for rowNum,acc in enumerate(accounts):
        rowNum += 1
        row = 1 # iterate per row to insert data
        worksheet = workbook.add_worksheet(acc)

        # Columns width
        if alteryxSupport:
            col_width = {
                'A:A': 12,
                'B:B': 20,
                'C:C': 57,
                'E:E': 20,
                'F:F': 11,
                'G:G': 38
            }
        else:       
            col_width = {
                'A:A': 12,
                'B:B': 12,
                'D:D': 57,
                'F:F': 20,
                'G:G': 11
            }
        for col in col_width:
            worksheet.set_column(col, col_width[col])

        if alteryxSupport:
            worksheet.autofilter('A1:K1')   # Set the autofilter
        else:
            worksheet.autofilter('A1:O1')   # Set the autofilter

        worksheet.freeze_panes(1, 0)    # Freeze pane on top row

        # Add header to the xlsx file
        if alteryxSupport:
            header = ['VPC','Path','Role Name','Role ARN','Console Access','Trust Principal','Trusted Entity','Attached Policies','Inline Policy', 'DL Name','Notes']
        else:
            header = ['AWS Account','Account Alias','Path','Role Name','Role ARN','Role Last Used Date','Region','Instance Profiles','Console Access','Trust Principal','Trusted Entity','Attached Policies','Inline Policy', 'DL Name','Notes']
        
        for col_num, data in enumerate(header):
            worksheet.write(0,col_num,data,header_format)

        # Try to auth, get a iam client, and get the roles
        try:
            session = boto3.session.Session(profile_name=f"{acc}/"+args.role)
            sts = session.client('sts')
            isGovSts = True if sts.get_caller_identity()['Arn'].split(':')[1] == 'aws-us-gov' else False
            iam = session.client('iam')
            roles = iam.list_roles(MaxItems=1000)
        except Exception as e:
            myMsg = f"Profile {acc}/{args.role} not found!"
            logging.error(myMsg)
            print(myMsg)
            print(str(e))
            continue

        accountAlias = []
        try:
            accountAlias = iam.list_account_aliases()['AccountAliases']
            if len(accountAlias) > 0:
                logging.info(f"QAR / IAM / Roles / ({acc}) {accountAlias}")
            else:
                logging.warning(f"QAR / IAM / Roles / ({acc}) {accountAlias} Alias not Found!")
        except botocore.exceptions.ClientError:
            pass
        accountAlias = str(accountAlias)

        rolesCount = 0
        for role in roles['Roles']:
            if role['RoleName'] not in exclustion_list:
                rolesCount += 1

        roleStr = 'Role' if rolesCount < 2 else 'Roles'

        # Print console log
        spc = (4-len(str(rolesCount)))*' '
        spc2 = ' ' if rolesCount <= 1 else ''

        myMsg = f'{to_space(rowNum,3)}. Exporting {spc}({str(rolesCount)}) IAM {roleStr}{spc2} for ({acc}) {accountAlias}'
        print(f'  {myMsg}')
        logging.info(myMsg)
        rolesCountTotal += rolesCount

        # GovCloud DLs Prefixed by GOV -  "@GE GOVAWS_" vs. "@GE AWS_"
        dl_prefix = "@GE GOVAWS_" if isGovSts else "@GE AWS_"
        myCounter = 7
        for role in roles['Roles']:

            roleName = role['RoleName']
            logging.info(f"QAR / ({acc}) {accountAlias} / IAM / Role / {roleName}")

            # Discard roles in exclusion list
            if roleName in exclustion_list:
                logging.info("Excluding role. " + roleName + " is on the exclusion list.")
            else:
                if progressBar:
                    myCounter = progress_print(counter=myCounter)

                pathName = role['Path'][1:] if len(role['Path'] ) > 1 else ""

                # Get iam role last used date and region
                roleDetail = iam.get_role(RoleName = role['RoleName'])

                # Update for lastUsedDate error handling
                lastUsedDate = ''
                lastRegion = ''
                try:
                    res = roleDetail['Role']['RoleLastUsed']
                    lastUsedDate = str(res['LastUsedDate']) if 'LastUsedDate' in res else ''
                    lastRegion = res['Region'] if 'Region' in res else ''
                except Exception as e:
                    logging.error('Failed! to get lastUsedDate & lastRegion')
                    
                instanceProfiles = []

                # Check for instance_profiles
                logging.debug("List Instance Profiles for Role: " + str(role['RoleName']))
                paginator = iam.get_paginator('list_instance_profiles_for_role')
                rs = paginator.paginate(
                    RoleName = role['RoleName'], 
                    PaginationConfig = {'MaxItems': 1000}
                )
                for instance in rs:
                    if len(instance['InstanceProfiles']) > 0:
                        if len(instanceProfiles) > 0:
                            instanceProfiles.append(instance['InstanceProfiles'])
                        else:
                            instanceProfiles = instance['InstanceProfiles']

                # Pull list of attached policies for role
                try:
                    attached_policies = iam.list_attached_role_policies(RoleName=roleName)['AttachedPolicies']
                    logging.debug("Attached Policies: " + str(attached_policies))
                except botocore.exceptions.ClientError:
                    pass

                # Pull list of inline policy for role
                try:
                    inline_policy = iam.list_role_policies(RoleName=roleName)['PolicyNames']
                    logging.debug("Inline Policies: " + str(inline_policy))
                except botocore.exceptions.ClientError:
                    pass

                # A role can have multiple policy statementents.
                for statement in role['AssumeRolePolicyDocument']['Statement']:

                    trust_entity_principals = statement['Principal']
                    logging.debug("Trust Entity Principls:" + str(trust_entity_principals))

                    # The principal the type of entity trusted, such as Service, AWS, or Federated
                    for principal in trust_entity_principals:

                        # A principal might have a value of a string, or a value of a list.
                        # To simplify the handling, i check if the principal value is a string
                        # and if so, i put it in a list
                        trust_entities = trust_entity_principals[principal]
                        if isinstance(trust_entity_principals[principal], str):
                            trust_entities = [trust_entities]

                        for entity in trust_entities:
                            logging.debug("Ready to categorize Role: " + roleName + ", Principal: " + principal + ", Trust Entity: " + entity)

                            # Default value for valus written to excel later
                            console_access = "Yes"
                            dl_name = ""
                            notes = ""

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

                                    dl_name = dl_prefix + pathName + roleName + "_" + acc  ##V3 - Added for Arcoe accounts 002420537650
                                    logging.debug("Generating DL: " + dl_name + " from Path Name: " + str(pathName) + " Role Name: " + str(roleName) + " and Account:  " + acc)

                                notes += "DL listed. IAM account extract in scope of the AWS script, please check trust policy showing federated access/ SAML integration. "

                            if principal == "AWS":

                                if entity == "*":
                                    notes += "Wildcard * in Trust Policy: Needs Review. "
                                    
                                # https://docs.aws.amazon.com/govcloud-us/latest/UserGuide/using-govcloud-arns.html
                                if "arn:aws:iam:" in entity or "arn:aws-us-gov:iam:" in entity: # Update for GovCloud
                                    trusted_acct = entity.split(':')[4]
                                    if trusted_acct not in trusted_accounts_list:
                                        trusted_accounts_list.append(trusted_acct)

                                    trusted_role = entity.split(':')[5]

                                    if trusted_acct == acc and trusted_role == 'root':
                                        notes += "IAM extract & credentials report of the account included in the AWS script. "
                                    elif trusted_acct in accounts and trusted_role == 'root':
                                        notes += "IAM extract & credentials report of the account included in the AWS script. See sheet: " + str(trusted_acct) + ". "
                                    elif trusted_acct != acc and trusted_acct in accounts:
                                        notes += "IAM extract & credentials report of the account included in the AWS script. See sheet: " + str(trusted_acct) + ". "
                                    elif trusted_acct != acc:
                                        notes += "Trusted entity is in another account. See account: " + str(trusted_acct) + ". "

                                    if "role/" in trusted_role:

                                        trusted_role = trusted_role.replace("root/","")
                                        dl_name = dl_prefix + trusted_role + "_" + trusted_acct

                                        # Update
                                        trusted_role = trusted_role.replace("role/","")
                                        dl_name = dl_prefix + trusted_role + "_" + trusted_acct
                                        logging.debug("Generating DL: " + dl_name + " from Trusted Role: " + str(trusted_role) + " and Trusted Account:  " + trusted_acct)

                            # Store DLs
                            if dl_name and dl_name not in dl_data:
                                dl_data.append(dl_name)


                            # Write row data to xlsx
                            if alteryxSupport:
                                entry = [acc,str(role['Path']),str(roleName),str(role['Arn']),str(console_access),principal,entity,str(attached_policies),str(inline_policy), str(dl_name), str(notes)]
                            else:
                                entry = [acc,accountAlias,str(role['Path']),str(roleName),str(role['Arn']),str(lastUsedDate),str(lastRegion),str(pretty_json(instanceProfiles)),str(console_access),principal,entity,str(pretty_json(attached_policies)),str(inline_policy), str(dl_name), str(notes)]
                            for col_num, data in enumerate(entry):
                                worksheet.write_string(row,col_num,data)
                                # Highlight Notes if mentions review
                                if col_num == 14 and 'review' in notes.lower():
                                    worksheet.write_string(row,col_num,notes,highlight_format)
                            row = row + 1
                            logging.debug("Writing entry to worksheet: " + str(entry))
        if progressBar:
            print()

        rowTotal += row - 1 # Exclude header

    put_json(dl_file, dl_data)
    workbook.close()

    # store trusted_accounts_list to trusted_accounts_file
    put_json(trusted_accounts_file, trusted_accounts_list)

    return rolesCountTotal, rowTotal

def export_credential_reports(accounts):
    res = {
        'AccessDenied': [],
        'STARTED': [],
        'INPROGRESS': [],
        'COMPLETE': []
    }

    # Consolidate if input_file given
    cred_data = []
    out_files = get_out_files(DATAFOLDER, INPUT_FILE)
    cred_file_csv = out_files['csv']
    cred_file_json = out_files['json']

    #https://docs.aws.amazon.com/IAM/latest/UserGuide/example_iam_GenerateCredentialReport_section.html
    for rowNum, acc in enumerate(accounts):
        rowNum += 1
        accountAlias = ''

        filename = acc + "_credential_report.csv"
        if DATAFOLDER: filename = f'{DATAFOLDER}/{filename}'

        # Print console log
        try:
            session = boto3.session.Session(profile_name=f"{acc}/"+args.role)
            iam = session.client('iam')
            response = iam.generate_credential_report()
            logging.debug("Generating credentials report for account " + acc + "Current state is %s.", response['State'])
            try:
                accountAlias = iam.list_account_aliases()['AccountAliases']
                if len(accountAlias) > 0:
                    accountAlias = accountAlias[0]
                    logging.info(f"QAR / IAM / User Credentail Report / ({acc}) {accountAlias}")
                else:
                    logging.warning(f"QAR / IAM / User Credentail Report / ({acc}) {accountAlias} Alias not Found!")
            except botocore.exceptions.ClientError:
                pass
            accountAlias = str(accountAlias)
                
            res[response['State']].append(acc)
            logging.info(f"Get credential for {str(acc)} {response['State']}")
        except Exception as err:
            response = {'State': 'AccessDenied'}
            res['AccessDenied'].append(acc)
            logging.warning(str(err))
        else:
            try:
                report = iam.get_credential_report()
            except Exception as err:
                pass
            
        print(f"  {to_space(rowNum,3)}. Generating Credential Report {to_space(response['State'],12)} for ({acc}) {accountAlias}")

        try:
            textfile = open(filename, "w")
            a = textfile.write(report['Content'].decode())
            textfile.close()

            # Debug get_credential_report csv data
            iDebug(f"WR: ({acc}) {accountAlias}")
            iDebug(report['Content'].decode())

        except Exception as e:
            logging.warning("Credential report for " + acc + " is not ready. Try again in a few minutes.")

        # Consolidate credentials
        if isFile(filename):
            iDebug(f"Found {filename}!")
            cred_csv = get_csv(filename)

            # Debug get_credential_report csv data
            iDebug(f"RO: ({acc}) {accountAlias}")
            iDebug(cred_csv)

            for rs in cred_csv:                
                # insert account, alias to top of dict of rs
                rs = {'account': acc, 'alias': accountAlias, **rs}  
                user = rs.get('user')
                if user and user != '<root_account>':
                    cred_data.append(rs)

    # Generate Consolidate credentials files
    if cred_data:
        iDebug(f"{len(cred_data)} Records to Export ")
        put_json(cred_file_json, cred_data)
        put_csv(cred_file_csv, cred_data)
                
    return res

def export_local_users_and_policies(accounts, progressBar=False, alteryxSupport=False):
    logging.info(f"QAR / IAM / Local Users Policies / Accounts ({len(accounts)})")

    dt = get_dt_local()[0:24].replace(':', '-')
    user_file = f'sox_local_users-{dt}.json'
    if DATAFOLDER: user_file = f'{DATAFOLDER}/{user_file}'
    user_data = []

    filename = 'sox_local_users_attached_policies.xlsx'
    if DATAFOLDER: filename = f'{DATAFOLDER}/{filename}'

    workbook = xlsxwriter.Workbook(filename)
    usersCountTotal = 0
    rowTotal = 0

    # Add a bold with gray background format for header cells
    header_format = workbook.add_format()
    header_format.set_bold(True)
    header_format.set_bg_color('#D9D9D9')

    highlight_format = workbook.add_format()
    highlight_format.set_bg_color('#FFFF00')

    totalRow = 0
    for rowNum, acc in enumerate(accounts):
        rowNum += 1
        worksheet = workbook.add_worksheet(acc)
        row = 1

        # Columns width
        if alteryxSupport:
            col_width = {
                'A:A': 50,
                'B:B': 14,
                'C:E': 25,
            }
        else:
            col_width = {
                'A:A': 50,
                'B:B': 14,
                'C:F': 25
            }
        for col in col_width:
            worksheet.set_column(col, col_width[col])

        if alteryxSupport:
            worksheet.autofilter('A1:E1')   # Set the autofilter
        else:    
            worksheet.autofilter('A1:F1')   # Set the autofilter

        worksheet.freeze_panes(1, 0)    # Freeze pane on top row

        if alteryxSupport:
            header = ['Policy Name','Account','Local User','Policy Type','Statement']
        else:
            header = ['Policy Name','AWS Account','Account Alias','Local User','Policy Type','Statement']

        for col_num, data in enumerate(header):
            worksheet.write(0,col_num,data,header_format)

        try:
            session = boto3.session.Session(profile_name=f"{acc}/"+args.role)
        except Exception as e:
            myMsg = f"Profile {acc}/{args.role} not found. Did you log in using gossamer3 bulk_login? Refer to: https://github.com/GESkunkworks/gossamer3"
            logging.error(myMsg)
            print(myMsg)
            print(str(e))
            quit()

        iam = session.client('iam')

        logging.info("Working on acc: " + acc)

        accountAlias = []
        try:
            accountAlias = iam.list_account_aliases()['AccountAliases']
            if len(accountAlias) > 0:
                logging.info(f"QAR / IAM / Roles / ({acc}) {accountAlias}")
            else:
                logging.warning(f"QAR / IAM / Roles / ({acc}) {accountAlias} Alias not Found!")
        except botocore.exceptions.ClientError:
            pass
        accountAlias = str(accountAlias)
        
        users = iam.list_users()['Users']
        logging.info(f"({acc}) {accountAlias} / Users ({len(users)}) / {str(users)}")

        usersCount = len(users)
        usersCountTotal += usersCount
        # Print console log
        spc = (4-len(str(usersCount)))*' '
        print(f"  {to_space(rowNum,3)}. Exporting {spc}({str(usersCount)}) Local Users' Managed and Inline Policies for ({acc}) {accountAlias}")

        myCounter = 7        
        for user in users:
            if progressBar:
                myCounter = progress_print(counter=myCounter)
            logging.debug("User: " + str(user))

            user_groups = iam.list_groups_for_user(UserName=user['UserName'])['Groups']
            inline_user_policies = iam.list_user_policies(UserName=user['UserName'])['PolicyNames']
            managed_user_policies = iam.list_attached_user_policies(UserName=user['UserName'])['AttachedPolicies']

            logging.debug("Inline User Policies: " + str(inline_user_policies))
            logging.debug("Managed User Policies: " + str(managed_user_policies))

            # Testing users with no inline, managed or group policies
            if len(user_groups) == 0 and len(inline_user_policies) == 0 and len(managed_user_policies) == 0:
                if alteryxSupport:
                    entry = ['n/a',acc,user['UserName'],'n/a','']
                else:
                    entry = ['n/a',acc,accountAlias,user['UserName'],'n/a','']

                for col_num, data in enumerate(entry):
                    worksheet.write_string(row, col_num, data)
                row += 1

            for inline_user_policy in inline_user_policies:

                logging.info(f'({acc}) {accountAlias} /IAM / Inline User Policie: {inline_user_policy}')
                policy = iam.get_user_policy(UserName=user['UserName'], PolicyName=inline_user_policy)
                policy_statement = policy['PolicyDocument']['Statement']
                logging.debug("Inline Policy: " + str(policy_statement))
                if alteryxSupport:
                    entry = [inline_user_policy,acc,user['UserName'],'Inline User Policy',str(pretty_json(policy_statement))]
                else:
                    entry = [inline_user_policy,acc,accountAlias,user['UserName'],'Inline User Policy',str(pretty_json(policy_statement))]
                for col_num, data in enumerate(entry):
                    worksheet.write_string(row, col_num, data)
                    logging.info(f"wrote Inline Policy: {inline_user_policy}")
                row += 1

            for managed_user_policy in managed_user_policies:

                policy = iam.get_policy(PolicyArn=managed_user_policy['PolicyArn'])
                policy_version = iam.get_policy_version(PolicyArn=managed_user_policy['PolicyArn'],VersionId=policy['Policy']['DefaultVersionId'])
                policy_statement = policy_version['PolicyVersion']['Document']['Statement']
                logging.info(f'({acc}) {accountAlias} /IAM / Managed User Policie: {managed_user_policy}')

                if alteryxSupport:
                    entry = [managed_user_policy['PolicyName'],acc,user['UserName'],'Managed User Policy',str(policy_statement)]
                else:
                    entry = [managed_user_policy['PolicyName'],acc,accountAlias,user['UserName'],'Managed User Policy',str(pretty_json(policy_statement))]

                for col_num, data in enumerate(entry):
                    worksheet.write_string(row,col_num,data)
                    logging.info(f"wrote Managed Policy: {managed_user_policy['PolicyName']}")
                row += 1

            '''
            'Path': 'string',
            'GroupName': 'string',
            'GroupId': 'string',
            'Arn': 'string',
            'CreateDate': datetime(2015, 1, 1)
            '''
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam/client/get_group_policy.html
            # print(bash_color('Groups : ','Red'),user_groups)
            if len(user_groups) == 0:
                continue
            for group in user_groups:
                # print(bash_color('Group : ','Green'),group)
                group_policies = iam.list_group_policies(GroupName=group['GroupName'])['PolicyNames']
                # iterate policies get default version
                for policy in group_policies:
                    group_policy = iam.get_group_policy(GroupName=group['GroupName'], PolicyName=policy)
                    '''
                    'GroupName': 'string',
                    'PolicyName': 'string',
                    'PolicyDocument': 'string'
                    '''
                    policy_statement = group_policy['PolicyDocument']

                    # store Users
                    if user['UserName'] and user['UserName'] not in user_data:
                        user_data.append(user['UserName'])

                    if alteryxSupport:
                        entry = [policy,acc,user['UserName'],'User Group Policy',str(pretty_json(policy_statement))]
                    else:
                        entry = [policy,acc,accountAlias,user['UserName'],'User Group Policy',str(pretty_json(policy_statement))]

                    for col_num, data in enumerate(entry):
                        worksheet.write_string(row,col_num,data)
                        logging.info(f"wrote User Group Policy: {policy}")
                    row += 1

            attached_group_policies = iam.list_attached_group_policies(GroupName=group['GroupName'])['AttachedPolicies']
            '''
            'PolicyName': 'string',
            'PolicyArn': 'string'
            '''
            for group_policy in attached_group_policies:
                policy = iam.get_policy(PolicyArn=group_policy['PolicyArn'])
                policy_version = iam.get_policy_version(PolicyArn=group_policy['PolicyArn'],VersionId=policy['Policy']['DefaultVersionId'])
                policy_statement = policy_version['PolicyVersion']['Document']['Statement']
                logging.info(f"({acc}) {accountAlias} /IAM / Attached Group Policie: {group_policy['PolicyName']}")

                if alteryxSupport:
                    entry = [group_policy['PolicyName'],acc,user['UserName'],'Attached Group Policy',str(policy_statement)]
                else:
                    entry = [group_policy['PolicyName'],acc,accountAlias,user['UserName'],'Attached Group Policy',str(pretty_json(policy_statement))]

                for col_num, data in enumerate(entry):
                    worksheet.write_string(row,col_num,data)
                    logging.info(f"wrote Attached Group Policy: {group_policy['PolicyName']}")
                row += 1

        if progressBar and usersCount > 0:
            print()
        
        rowTotal += row - 1 # Exclude header

    put_json(user_file, user_data)

    workbook.close()
    return usersCountTotal, rowTotal


################################################################################

args = parse_args()
ts = get_ts()

## Error collections
WARNINIG = []

# add DATAFOLDER logic
if args.datafolder: DATAFOLDER = args.datafolder
INPUT_FILE = args.input_file if args.input_file else None

if DATAFOLDER:
    logging.basicConfig(filename=f'{DATAFOLDER}/qar_utility.log',format='%(asctime)s %(levelname)s:%(message)s', encoding='utf-8', level=LOGLEVEL)
else:
    logging.basicConfig(filename='qar_utility.log',format='%(asctime)s %(levelname)s:%(message)s', encoding='utf-8', level=LOGLEVEL)

progressBarShow = True if args.progressbar else False 
alteryxSupport =  True if args.alteryx else False 

if alteryxSupport:
    ppwide(f'Quarterly Access Review / Alteryx Support')
else:
    ppwide(f'Quarterly Access Review')

print('Start:', get_datetime(), 'UTC:', get_datetimeutc())

# Logs
print('Args:', iColor(vars(args), 'iYellow'))


# add --input-file logic
if args.sortaccounts:
    if not args.input_file:
        awsAccounts = args.accounts.split(',')
        awsAccounts.sort()
        args.accounts = ','.join(awsAccounts)
    else:
        # --input-file logic
        rSet = file_read_input_file(args.input_file)
        awsAccounts = []
        for rs in rSet:
            if rs.get('AccountId') and rs.get('AccountId') not in awsAccounts:
                awsAccounts.append(rs.get('AccountId'))
        awsAccounts.sort()
        args.accounts = ','.join(awsAccounts)

if not args.input_file:
    awsAccounts = args.accounts.split(',')
else:
    # --input-file logic
    rSet = file_read_input_file(args.input_file)
    awsAccounts = []
    for rs in rSet:
        if rs.get('AccountId') and rs.get('AccountId') not in awsAccounts:
            awsAccounts.append(rs.get('AccountId'))

awsAccountsCount = len(awsAccounts)

ppwide(f'AWS Accounts ({str(awsAccountsCount)})')
print(awsAccounts)

print()
exclusionsCount = len(exclustion_list)
ppwide(f'IAM Roles / Exclustion List ({str(exclusionsCount)})')
print(exclustion_list)

ts = get_ts()
if args.verify:
    tss = get_ts()
    ppwide("Sanity Check / Verify Account Access")
    res = sanity_check(awsAccounts)
    print(f'Took: {took_ts(tss)} seconds')
    if not res:
        logging.error(f"AccessDenied Error! See '0-access-report.json'")
        sys.exit()

if args.credentials:
    print()
    ppwide("Export / IAM Credential Reports ")
    tss = get_ts()
    res = export_credential_reports(awsAccounts)
    if len(res['COMPLETE']) == len(awsAccounts):
        print(f"[.] In { took_ts(tss)} Seconds COMPLETED Generating Credential Reports")
    elif len(res['AccessDenied']) == len(awsAccounts):
        print(ppwide('#', delimeter='#'))
        print('#   1. Check the role in gossamer3 file and in script \n'
              '#   2. Check your gossamer3 file! \n'
              '#   3. Check gossamer3 bulk_login command and run it with --force \n'
              '#   4. You should have IAM Access to run the QAR report!')
        print(ppwide('#', delimeter='#'))
    else:
        print(f"[.] In {took_ts(tss)} seconds Credential Reports didn't complete!")
        for rs in res:
            count = len(res[rs]) 
            if count > 0:

                WARNINIG.append(f"Credential Reports didn't complete! Please re-run to Complete Credential Reports!")
                print(f"    -. {rs} ({str(count)}): {str(res[rs])}")

if args.localusers:
    print()
    tss = get_ts()
    ppwide("Export / IAM Local Users' Managed and Inline Policies")
    usersCountTotal, rowTotal = export_local_users_and_policies(awsAccounts, progressBarShow, alteryxSupport)
    print(f"[.] In {took_ts(tss)} Seconds COMPLETED Exporting ({usersCountTotal}) Local Users' Managed and Inline Policies in ({rowTotal}) Rows")

if args.iamroles:
    print()
    ppwide("Export / IAM Roles")
    tss = get_ts()
    rolesCountTotal, rowTotal = export_iam_roles(awsAccounts, progressBarShow, alteryxSupport)
    print(f"[.] In {took_ts(tss)} Seconds COMPLETED Exporting ({rolesCountTotal}) IAM Roles in ({rowTotal}) Rows")
if not (args.credentials or args.localusers or args.iamroles):
    print()
    print(ppwide('#', delimeter='#'))
    print('#   1. WARNING: Dry run. \n'
          '#   2. You MUST use all or at least one of the switches of: \n'
          '#       -c -l -i')
    print(ppwide('#', delimeter='#'))

print('End:', get_datetime(), 'UTC:', get_datetimeutc())
print(f"Overall Execution Took: { took_ts(ts)} seconds")
print()

# Outcome Files Summary
out_sum = {}
out_sum['Data Folder'] = DATAFOLDER if DATAFOLDER else '.'

# User report
uMap = {
    'account': 'AWS Account',
    'alias': 'Account Alias',
    'user': 'User',
    'arn': 'ARN',
    'user_creation_time': 'User Creation Time',
    'password_enabled': 'Password',
    'mfa_active': 'MFA',
    'password_last_used': 'Pass Last Used',
    'password_last_changed': 'Pass Last Changed',
    'password_next_rotation': 'Pass Next Rotation',
    # 'access_key_1_active': 'Key1',
    # 'access_key_1_last_rotated': 'Key1 Rotated',
    # 'access_key_1_last_used_date': 'Key1 Last Used',
    # 'access_key_2_active': 'Key2',
    # 'access_key_2_last_rotated': 'Key2 Rotated',
    # 'access_key_2_last_used_date': 'Key2 Last Used',
}

if INPUT_FILE:
    out_files = get_out_files(DATAFOLDER, INPUT_FILE)
    cred_file_csv = out_files['csv']
    cred_file_json = out_files['json']

    out_sum['Credential CSV'] = cred_file_csv
    out_sum['Credential JSON'] = cred_file_json

    acc_users = {}
    users = []
    rSet = get_json(cred_file_json)
    
    print_color_dict(out_files)
    if not rSet: 
        rSet = []

    if iDebug(): 
        ppjson(rSet)
    
    data = []
    for rs in rSet:
        acc = rs.get('account')
        user = rs.get('user')
        if user:
            # create and map data
            rec = {}
            for key, val in uMap.items():
                rec[val] = rs.get(key)

            # append to datamodel
            if rec:
                data.append(rec)

            if not acc_users.get(acc):
                acc_users[acc] = []

            # add user to account's user
            acc_users[acc].append(user)
            iDebug(f"acc_users[{acc}]:", acc_users[acc])

            # add user to consolidated users
            if user not in users:
                users.append(user)

    # Report User data
    cMap =  {
        'ARN': {
            'user': 'iYellow',
        },
        'Password': {
            'true': 'iYellow',
        },
        'MFA': {
            'true': 'iYellow',
        },
    }
    dm = DataModel()
    dm.print_table(data, cMap)

    print()
    print_color_dict(acc_users)
    print('users:', iColor(users, 'iYellow'))
    print('--user', "'" + iColor(','.join(users), 'iYellow') + "'")


print()
print_color_dict(out_sum)

if len(WARNINIG) > 0:
    print()
    for warn in WARNINIG:
        iWarning(warn)
