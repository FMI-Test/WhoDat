#!/usr/bin/env python

# To 'Extract Required Permissions' run:
#   exec/extract-awsutil-permissions.sh

'''
AWS Utility for Boto3
------------------------------------------------------------------------------------------
### Extract Required Permissions for bin/awsutil.py on Fri 22-Nov-2024  10:28:28 #########

### 1. Class Account #####################################################################
        account:GetAlternateContact
        account:GetContactInformation
        account:PutAlternateContact

### 2. Class CloudFormation ##############################################################
        cloudformation:DescribeStacks
        cloudformation:DescribeStackEvents

### 3. Class CloudTrail ##################################################################
        cloudtrail:DescribeTrails
        cloudtrail:DeleteTrail
        cloudtrail:CreateTrail
        cloudtrail:GetEventDataStore
        cloudtrail:GetEventSelectors
        cloudtrail:GetChannel
        cloudtrail:GetTrailStatus
        cloudtrail:ListChannels
        cloudtrail:ListTrails
        cloudtrail:StartLogging
        cloudtrail:LookupEvents
        cloudtrail:UpdateTrail

### 4. Class ConfigService ###############################################################
        configservice:DescribeConfigRules
        configservice:DescribeConfigurationRecorders
        configservice:DescribeConfigurationRecorderStatus
        configservice:DescribeDeliveryChannels
        configservice:DescribeDeliveryChannelStatus
        configservice:DeleteConfigurationRecorder
        configservice:DeleteDeliveryChannel
        configservice:PutConfigurationRecorder
        configservice:PutDeliveryChannel
        configservice:StartConfigurationRecorder
        configservice:StopConfigurationRecorder

### 5. Class DirectConnect ###############################################################
        directconnect:DescribeDirectConnectGateways
        directconnect:DescribeVirtualGateways
        directconnect:DescribeVirtualInterfaces
        directconnect:DescribeDirectConnectGatewayAssociations
        directconnect:DescribeDirectConnectGatewayAttachments

### 6. Class EC2 #########################################################################
        ec2:AllocateAddress
        ec2:CreateNatGateway
        ec2:DeleteTransitGatewayVpcAttachment
        ec2:DescribeFlowLogs
        ec2:DescribeInstances
        ec2:DescribeNatGateways
        ec2:DescribeRegions
        ec2:DescribeRouteTables
        ec2:DescribeTransitGatewayVpcAttachments
        ec2:DescribeVpcs
        ec2:DescribeVpcEndpoints
        ec2:DescribeVpcEndpointConnections
        ec2:DisassociateRouteTable
        ec2:TerminateInstances

### 7. Class ELBV2 #######################################################################
        elbv2:DescribeLoadBalancers
        elbv2:DescribeLoadBalancerAttributes

### 8. Class Firewall ####################################################################
        firewall:ListFirewalls
        firewall:DescribeFirewall

### 9. Class IAM #########################################################################
        iam:ListAccountAliases
        iam:GetAccountPasswordPolicy
        iam:GetSamlProvider
        iam:DeleteSamlProvider
        iam:GetAccountSummary
        iam:ListRoles
        iam:ListRolesPolicies
        iam:ListPolicies
        iam:ListSamlProviders

### 10. Class IamRolesCleanup ############################################################
         iam:DeleteInstanceProfile
         iam:DeletePolicy
         iam:DeleteRole
         iam:DeleteRolePolicy
         iam:DeleteSamlProvider
         iam:DetachPolicy
         iam:DetachRole
         iam:GetAccountPasswordPolicy
         iam:GetPaginator
         iam:GetPolicy
         iam:GetPolicyVersion
         iam:GetRole
         iam:GetSamlProvider
         iam:ListAccountAliases
         iam:ListAttachedRolePolicies
         iam:ListEntitiesForPolicy
         iam:ListPolicyVersions
         iam:ListRolePolicies
         iam:ListRoles
         iam:ListSamlProviders
         iam:RemoveRoleFromInstanceProfile

### 11. Class GuardDuty ##################################################################
        guardduty:AcceptAdministratorInvitation
        guardduty:CreateDetector
        guardduty:CreateMembers
        guardduty:CreatePublishingDestination
        guardduty:CreateSampleFindings
        guardduty:DeclineInvitations
        guardduty:DeleteDetector
        guardduty:DeleteInvitations
        guardduty:DeleteMembers
        guardduty:DescribeMalwareScans
        guardduty:DescribeOrganizationConfiguration
        guardduty:DescribePublishingDestination
        guardduty:DisassociateFromAdministratorAccount
        guardduty:DisassociateMembers
        guardduty:GetAdministratorAccount
        guardduty:GetDetector
        guardduty:GetInvitationsCount
        guardduty:GetMalwareScanSettings
        guardduty:GetMemberDetectors
        guardduty:GetMembers
        guardduty:InviteMembers
        guardduty:ListCoverage
        guardduty:ListDetectors
        guardduty:ListInvitations
        guardduty:ListMembers
        guardduty:ListOrganizationAdminAccounts
        guardduty:ListPublishingDestinations

### 12. Class RAM ########################################################################
        ram:ListResourceTypes
        ram:ListResources
        ram:GetResourceShareAssociations
        ram:GetResourceShares
        ram:ListPrincipals

### 13. Class Route53Resolver ############################################################
        route53resolver:DeleteResolverEndpoint
        route53resolver:DeleteResolverRule
        route53resolver:ListResolverEndpoints
        route53resolver:ListResolverRules

### 14. Class SecurityHub ################################################################
        securityhub:AcceptAdministratorInvitation
        securityhub:CreateMembers
        securityhub:DeclineInvitations
        securityhub:DeleteInvitations
        securityhub:DeleteMembers
        securityhub:DescribeActionTargets
        securityhub:DescribeHub
        securityhub:DescribeOrganizationConfiguration
        securityhub:DescribeStandards
        securityhub:DisassociateFromAdministratorAccount
        securityhub:DisassociateMembers
        securityhub:EnableSecurityHub
        securityhub:GetAdministratorAccount
        securityhub:GetEnabledStandards
        securityhub:GetInsights
        securityhub:GetInvitationsCount
        securityhub:GetMembers
        securityhub:InviteMembers
        securityhub:ListInvitations
        securityhub:ListMembers
        securityhub:ListOrganizationAdminAccounts
        securityhub:ListSecurityControlDefinitions

### 15. Class STS ########################################################################
        sts:GetCallerIdentity

### 16. Class Organization ###############################################################
        organization:DescribeAccount
        organization:DescribePolicy
        organization:ListAccounts
        organization:ListPolicies
        '''

import boto3
import botocore

from botocore.exceptions import ClientError
from common import *
from util import *


def callerid():
    """When called from a class returns class:ClassMethodName"""
    stack = inspect.stack()
    the_class = stack[1][0].f_locals["self"].__class__.__name__
    the_method = stack[1][0].f_code.co_name
    the_method = the_method.replace('_', ' ').title().replace(' ','')
    return f"{the_class.lower()}:{the_method}"


def filter_dict(records: dict|list=[], key_map=[]):
    """Filters [list of] dictionaty based on list of key map to filter
    
    Args:
        records (dict|list): A dictionary or list of dictionaries
        key_map (list): List of dictionary key to filter

    Returns dict|list if records is dict|list respectively 
    """
    if not key_map:
        return records

    if isinstance(records, dict):
        res = {}
        for key in key_map:
            res[key] = records.get(key)
        
        return res

    res = []
    for rs in records:
        rss = {}
        for key in key_map:
            rss[key] = rs.get(key)

        res.append(rss)

    return res


def get_aws_partition():
    """Returns AWS partition .e.g. 'aws' or 'aws-us-gov'"""
    sts = boto3.client('sts')
    return sts.get_caller_identity()['Arn'].split(':')[1]


def get_env_info(file_date: bool=False):
    """Returns Account info from Env Vars or current STS & IAM
    
    Args: 
        file_date (bool): if True will add date of yyyy-mm-dd at the end of csv & json data files

    Note: env vars will overwites, if not gives then all extracted

    Returns dictionary of: 
        PROJECT:        Config SecOps
        ACCOUNT_ID:     012345678912
        ACCOUNT_ALIAS:  account-alias
        ACC_FMT:        (012345678912) [account-alias]
        ACC_DASH:       (0123-4567-8912) [account-alias]

        GOV_CLOUD:      False
        PARTITION:      aws
        PREFIX:         Pre             # first three character for ResFile prefix

        REGION:         us-east-1
        REG_LOC:        US East (N. Virginia) 
        REG_FMT:        US East us-east-1 (N. Virginia)

        SOURCE:         GECC
        TARGET:         GEAV

        Title:          Config Contacts
        GR2:            ### GR2-0 / Config Contacts / (012345678912) [account-alias]

        CWD:            .../src
        DATAFOLDER:     /tmp/secops/{ACCOUNT_ALIAS}
        Path:           {CWD}/src/bin
        File:           {CWD}/src/bin/config-contacts.py
        NAME:           config-contacts
        Task:           Pre-Config-Contacts

        CsvFile:        {DATAFOLDER}/pre-{NAME}.csv
        OutFile:        {DATAFOLDER}/out-{NAME}.json
        ResFile:        {DATAFOLDER}/pre-{NAME}.json

    """
    # https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-env-vars.html
    caller_frame = inspect.stack()[1]
    file = caller_frame.filename.replace('//', '/')
    fullPath = os.path.realpath(file)
    path, filename = os.path.split(fullPath)
    name = os.path.splitext(filename)[0]
    title = file_title( name )

    PREFIX = os.environ.get('PREFIX', '')

    res = {}
    try:
        sts = STS()
        caller_info = sts.get_caller_identity()
        if isTrace():
            iTrace('caller_info:')
            ppjson(caller_info)
        account = caller_info['Account']
        iTrace(f'account: {account}')
        ACCOUNT_ID = os.environ.get('ACCOUNT_ID', account)

        PARTITION = caller_info['Arn'].split(':')[1]
        iTrace(f'PARTITION: {PARTITION}')
        GOV_CLOUD = True if PARTITION == 'aws-us-gov' else False

        ACCOUNT_ALIAS = os.environ.get('ACCOUNT_ALIAS')
        if not os.environ.get('ACCOUNT_ALIAS'):
            iam = IAM()
            alias = iam.list_account_aliases()
            iTrace(f'alias: {alias}')
            ACCOUNT_ALIAS = alias

        PROJECT = os.environ.get('PROJECT')
        DATAFOLDER = os.environ.get('DATAFOLDER', '/tmp')
        if not isCodeBuild():
            if isinstance(PROJECT, str):
                DATAFOLDER += f'/{PROJECT.lower()}'
            DATAFOLDER += f'/{ACCOUNT_ALIAS}'
        DATAFOLDER = DATAFOLDER.replace(' ', '-')
        iTrace(f'DATAFOLDER: {DATAFOLDER}')
        mk_folder(DATAFOLDER)

        ACC12 =  ndigits(ACCOUNT_ID, 12)
        iTrace(f'ACC12: {ACC12}')
        ACC_DASH = f'{ACC12[0:4]}-{ACC12[4:8]}-{ACC12[8:12]}'
        iTrace(f'ACC_DASH: {ACC_DASH}')

        PREFIX = os.environ.get('PREFIX', 'Backup').replace('-',' ').title().replace(' ','-')
        Prefix = PREFIX[0:3].lower()
        file_name = name.replace('_', '-').replace('--','-').strip()
        file_dt = '-' + get_dt().replace(':', '-')[0:10]  + '-utc' if file_date else ''
        CSV_FILE = f'{DATAFOLDER}/{Prefix}-{file_name}{file_dt}.csv'
        OUT_FILE = f'{DATAFOLDER}/out-{file_name}{file_dt}.json'
        RES_FILE = f'{DATAFOLDER}/{Prefix}-{file_name}{file_dt}.json'
        Task = f"{PREFIX} {title}".strip()

        REGION = os.environ.get('REGION', 'us-gov-east-1' if GOV_CLOUD else 'us-east-1')
        iTrace(f'REGION: {REGION}')
        REG_LOC =  get_region_location(REGION)
        iTrace(f'REG_LOC: {REG_LOC}')
        REG_FMT =  get_region_fmt(REGION)
        iTrace(f'REG_FMT: {REG_FMT}')

        ACC_FMT =  f'({ACC12}) [{ACCOUNT_ALIAS}]'
        iTrace(f'ACC_FMT: {ACC_FMT}')
        ACC_DASH = f'({ACC_DASH}) [{ACCOUNT_ALIAS}]'
        iTrace(f'ACC_DASH: {ACC_DASH}')

        DIRECTION = '-'.join([ os.environ.get('SOURCE', ''), os.environ.get('TARGET','')])

        res = {
            'PROJECT': PROJECT,
            'ACCOUNT_ID': ACC12,
            'ACCOUNT_ALIAS': ACCOUNT_ALIAS,
            'ACC_FMT': ACC_FMT,
            'ACC_DASH': ACC_DASH,

            'GOV_CLOUD': GOV_CLOUD,
            'PARTITION': PARTITION,
            'PREFIX': PREFIX,

            'REGION': REGION,
            'REG_LOC': REG_LOC,
            'REG_FMT': REG_FMT,

            'SOURCE': os.environ.get('SOURCE'),
            'TARGET': os.environ.get('TARGET'),

            'Title': title,
            'GR2': f'### GR2-0 / {DIRECTION} / {title} / {ACC_FMT}' if DIRECTION != '-' else f'### GR2-0 / {title} / {ACC_FMT}',

            'CWD': os.getcwd(),
            'DATAFOLDER': DATAFOLDER,
            'Path': path,
            'File': file,
            'NAME': file_name,
            'Prefix': Prefix,
            'Task': Task,
            'CsvFile': CSV_FILE,
            'OutFile': OUT_FILE,
            'ResFile': RES_FILE,
        }

    except Exception as err:
        iWarning('Unable to extract Account, Alias, Partition from current STS & IAM', err)

    return res


def get_regions():
    """Returns list of active regions"""
    res = []
    ec2 = boto3.client('ec2')

    try:
        response = ec2.describe_regions()
        
        [res.append(rs['RegionName']) for rs in response['Regions']]

    except Exception as err:
        iAbort('Error getting regions ', err)

    return res


def get_process_result(response: list, default: str=''):
    """Return UnprocessedAccounts Result/ProcessingResult for GuardDuty & SecuriyHub
    
    Args:
        response (dict): Boto3 response for GD & SH calls

    Returns dict:
        Account (dict): if acc_data given
        Outcome (str): one of failed, passeed, skipped
        Tasks (list): TBD 

    """
    # Failed
    aMap = [
        # 
        'already an associated member of another master account',
        'invalid or out-of-range value is specified as an input parameter',
        'is still associated to it',
    ]

    # Skipped
    sMap = [
        'already invited or is already the GuardDuty master of the given member account',
        'already a member or associated member of the current account',
        'already the SecurityHub master of the given member account',
        'is not yet associated to it',
    ]

    res = []
    for rs in response:
        rss = rs.get('ProcessingResult', rs.get('Result'))
        if rss:
            for needle in aMap:
                if needle in rss:
                    rss = f"{iColor(FAILURE.upper(), 'Red')} because {needle}"

            for needle in sMap:
                if needle in rss:
                    rss = f"{iColor(SKIPPED.upper(), 'Green')} because {needle}"

            res.append(rss)
        else:
          rss = iColor(SUCCESS.upper(), 'Green')
          res.append(rss)  


    return res[0] if len(res) == 1 else res  


def get_response(response: dict):
    """Extracts ResponseMetadata if exist and append it to response"""
    res = {
        'HTTPStatusCode': 'Unknown',
        'RetryAttempts': 'Unknown'
    }

    if 'ResponseMetadata' in response:
        rs = response['ResponseMetadata']
        res['HTTPStatusCode'] = rs.get('HTTPStatusCode')
        res['RetryAttempts'] = rs.get('RetryAttempts')

    return res


def pop_meta(response):
    """Removes ResponseMetadata if exist from response"""
    res = response
    if not isinstance(res, dict):
        return res
    
    if 'ResponseMetadata' in res and res['ResponseMetadata'].get('HTTPStatusCode'):
        http_code = res['ResponseMetadata'].get('HTTPStatusCode', 555)
        if http_code != 200 and isTrace():
            iTrace('HTTPStatusCode:', http_code)
            
    res.pop('ResponseMetadata', None)
    res.pop('RequestId', None)
    res.pop('HTTPHeaders', None)

    return res


def region_index(region, regions):
    """Returns index of given region from 1 in list of regions
    
    Args:
        region (str): AWS region
        regions (list): list of regions 
    """

    for i, r in enumerate(regions):
        if region == r:
            return i + 1
        
    iWarning(f'Unable to find {region} in {regions}')

    return 0


class Account:
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/account.html

    def __init__(self, profile_name=None) -> None:
        sess = boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()
        self.client = sess.client('account')

    def get_alternate_contact(self, AlternateContactType: str) -> dict:
        """Retrieves the specified alternate contact attached to an account.

        Args:
            AlternateContactType (str): one of BILLING, OPERATIONS, SECURITY

        Returns dict of alternate contact info
        """
        client = self.client
        res = {}

        try:
            response = client.get_alternate_contact(AlternateContactType=AlternateContactType)

            iDebug('Account / GetAlternateContact', pop_meta(response))

            # Consolidated Result
            res = response['AlternateContact']

        except Exception as err:
            iWarning(f'Unable to GetAlternateContact', err)

        return res

    def get_contact_information(self) -> dict:
        """Retrieves the primary contact information of an account"""
        client = self.client
        res = {}

        try:
            response = client.get_contact_information()

            iDebug('Account / GetContactInformation', pop_meta(response))

            # Consolidated Result
            res = response['ContactInformation']

        except Exception as err:
            iWarning(f'Unable to GetContactInformation', err)

        return res

    def put_alternate_contact(self, 
            AlternateContactType: str,
            EmailAddress: str,
            Name: str,
            PhoneNumber: str,
            Title: str
        ) -> dict:
        """Modifies the specified alternate contact of BILLING, OPERATIONS, SECURITY

        Args:
        
            AlternateContactType (str): one of BILLING, OPERATIONS, SECURITY
            EmailAddress (str): email address for the alternate contact
            Name (str): name for the alternate contact.
            PhoneNumber (str): phone number for the alternate contact
            TitleTitle (str):  title for the alternate contact.

        Returns True or False
        """
        client = self.client
        res = {}

        try:
            response = client.put_alternate_contact(
                    AlternateContactType=AlternateContactType,
                    EmailAddress=EmailAddress,
                    Name=Name,
                    PhoneNumber=PhoneNumber,
                    Title=Title
                )

            iDebug(f'Account / PutAlternateContact {AlternateContactType}', pop_meta(response))

            return True

        except Exception as err:
            iWarning(f'Unable to PutAlternateContact {AlternateContactType}', err)

        return False


class CloudFormation:

    def __init__(self, region_name='us-east-1', profile_name=None, maxResults=100) -> None:
        sess  = boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()
        self.client = sess.client('cloudformation', region_name=region_name) if region_name else sess.client('cloudformation')
        self.region = region_name
        self.maxResults = maxResults

    def describe_stacks(self, stack=None, key_map=[]):
        """Returns list of CF Stack Events"""
        client = self.client

        res = {'Stacks': [], 'Region': self.region}
        response = {}
        nextToken = None
        while True:
            try:
                if not nextToken:
                    if stack is not None:
                        response = client.describe_stacks(
                            StackName=stack
                        )
                    else:
                        response = client.describe_stacks()
                else:
                    iDebug('nextToken', nextToken)
                    if stack is not None:
                        response = client.describes(
                            StackName=stack,
                            NextToken=nextToken,
                        )
                    else:
                        response = client.describes(
                            NextToken=nextToken,
                        )

                iTrace(f'{callerid()} / Stack {stack}')
                if isTrace():
                    ppjson(response)

                stacks = response.get('Stacks', [])

                # Filter Result
                if len(key_map) > 0:
                    stacks = filter_dict(stacks, key_map)

                for iStack in stacks:
                    res['Stacks'].append(iStack)
            except Exception as err:
                if 'does not exist' in str(err):
                    iInfo(f'{callerid()} Stack "{stack}" does not exist in "{self.region}"')
                    return res
                iWarning(f'API call faied for {callerid()} / Stack {stack}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res

    def describe_stack_events(self, stack=None, key_map=[]):
        """Returns list of CF Stack Events"""
        client = self.client

        res = {'StackEvents': [], 'Region': self.region}
        response = {}
        nextToken = None
        while True:
            try:
                if not nextToken:
                    response = client.describe_stack_events(
                        StackName=stack,
                    )
                else:
                    iDebug('nextToken', nextToken)
                    response = client.describe_stack_events(
                        StackName=stack,
                        NextToken=nextToken,
                    )

                iTrace(f'{callerid()} / Stack {stack}', pop_meta(response))
                if isTrace():
                    ppjson(response)

                events = response.get('StackEvents', [])

                # Filter Result
                if len(key_map) > 0:
                    filter_events = []
                    events = filter_dict(events, key_map)
                    for event in events:
                        res['StackEvents'].append(event)
                else:
                    res['StackEvents'].append(events)

            except Exception as err:
                if 'does not exist' in str(err):
                    iInfo(f'{callerid()} Stack "{stack}" does not exist in "{self.region}"')
                    return res
                iAbort(f'API call faied for {callerid()} / Stack "{stack}" in "{self.region}"', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        self.stackEvents = res
        return res

    def stacks_brief_map(self):
        return [
            'StackId',
            'StackName',
            'CreationTime',
            'LastUpdatedTime',
            'StackStatus',
            'Capabilities'
        ]

    def events_brief_map(self):
        return [
            'StackName',
            'LogicalResourceId',
            'ResourceType',
            'Timestamp',
            'ResourceStatus',
            'ResourceStatusReason',
        ]


class CloudTrail:
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html

    def __init__(self, region_name=None, profile_name=None) -> None:
        sess  = boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()
        self.client = sess.client('cloudtrail', region_name=region_name) if region_name else sess.client('cloudtrail')
        self.region = region_name

    def describe_trails(self, trails_arns: list = [], shadow_trails: bool = True):
        """Retrieves settings for one or more trails associated with the current Region for your account

        Args:
            trails_arns (list): if empty returns trail in the current Region
            shadow_trails (bool): shadow trail is the replication in a Region of a trail that 
                was created in a different Region

        Returns list of trails
        """
        client = self.client
        res = []

        try:
            response = client.describe_trails(
                trailNameList=trails_arns,
                includeShadowTrails=shadow_trails
            )

            iDebug(callerid(), pop_meta(response))

            # Consolidated Result
            [res.append(rs) for rs in response['trailList']]

        except Exception as err:
            iWarning(f'API call faied for {callerid()} {self.region} {get_region_location(self.region)}', err)

        return res

    def delete_trail(self, name:str):
        """Deletes a trail. This operation must be called from the Region in which the trail was created

        Args:
            name (str): Specifies the name or the CloudTrail ARN of the trail to be deleted

            Return dict
        """
        client = self.client
        res = {}

        try:
            res = client.delete_trail( Name=name )

            iDebug(callerid(), res)

        except Exception as err:
            iWarning(f'Unable to DeleteTrail {self.region} {get_region_location(self.region)}', err)

        return res

    def create_trail(self, 
            Name: str,
            S3BucketName: str,
            S3KeyPrefix: str,
            SnsTopicName: str,
            IncludeGlobalServiceEvents: bool = True,
            IsMultiRegionTrail: bool = True,
            EnableLogFileValidation: bool = True,
        ):
        """Creates a trail that specifies the settings for delivery of log data to an Amazon S3 bucket.

        Args:
            name (str): Specifies the name or the CloudTrail ARN of the trail to be deleted

            Return dict
        """
        client = self.client
        res = {}

        try:
            response = client.create_trail(
                Name=Name,
                S3BucketName=S3BucketName,
                S3KeyPrefix=S3KeyPrefix,
                SnsTopicName=SnsTopicName,
                IncludeGlobalServiceEvents=True,
                IsMultiRegionTrail=True,
                EnableLogFileValidation=True
            )

            iDebug(callerid(), response)

            res = pop_meta(response)

        except Exception as err:
            iWarning(f'API call faied for {callerid()} {self.region} {get_region_location(self.region)}', err)

        return res

    def get_event_data_store(self, arn):
        """Returns get event data store

        Args:
            arn (str): ARN or the ID portion of the ARN

            Return dict
        """
        client = self.client
        res = {}

        try:
            res = client.get_event_data_store( EventDataStore=arn )
            res.pop('ResponseMetadata')

            iDebug(callerid(), res)

        except Exception as err:
            iWarning(f'API call faied for {callerid()} {self.region} {get_region_location(self.region)}', err)

        return res

    def get_event_selectors(self, arn):
        """Returns get trail event selector

        Args:
            arn (str): arn of trail

            Return dict
        """
        client = self.client
        res = {}

        try:
            response = client.get_event_selectors( TrailName=arn)

            iDebug(callerid(), pop_meta(response))

            res = pop_meta(response)

        except Exception as err:
            iWarning(f'API call faied for {callerid()} {self.region} {get_region_location(self.region)}', err)

        return res

    def get_channel(self, arn):
        """Returns get trail channels

        Args:
            arn (str): arn or UUID of channel

            Return dict
        """
        client = self.client
        res = {}

        try:
            response = client.get_get_channel( Channel=arn)

            iDebug(callerid(), pop_meta(response))

            res = pop_meta(response)

        except Exception as err:
            iWarning(f'API call faied for {callerid()} {self.region} {get_region_location(self.region)}', err)

        return res

    def get_trail_status(self, arn):
        """Returns get trail status

        Args:
            arn (str): arn of name of trail

            Return dict
        """
        client = self.client
        res = {}

        try:
            res = client.get_trail_status(Name=arn)
            res['TrailARN'] = arn
            res.pop('ResponseMetadata')

            iDebug(callerid(), res)

        except Exception as err:
            iWarning(f'Unable to GetTrailStatus {self.region} {get_region_location(self.region)}', err)

        return res

    def list_channels(self) -> list:
        """Returns list of Trail Cahnnels"""
        client = self.client
        response = {}
        nextToken = None
        maxResults = 100
        res = []

        while True:
            try:
                if not nextToken:
                    response = client.list_channels(
                        MaxResults=maxResults,
                    )
                else:
                    response = client.list_channels(
                        NextToken=nextToken,
                        MaxResults=maxResults,
                    )

                iDebug(callerid(), pop_meta(response))

                # Consolidated Result
                res =  response['Channels']

            except Exception as err:
                iWarning(f'API call faied for {callerid()} {self.region} {get_region_location(self.region)}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res

    def list_trails(self):
        """Returns list of cloud trails"""
        client = self.client
        res = []

        try:
            response = client.list_trails()

            iDebug(callerid(), pop_meta(response))

            # Consolidated Result
            res = response['Trails']

        except Exception as err:
            iWarning(f'API call faied for {callerid()} {self.region} {get_region_location(self.region)}', err)

        return res

    def start_logging(self, Name):
        """
        Starts the recording of Amazon Web Services API calls and log file delivery for a trail. 
        For a trail that is enabled in all Regions, this operation must be called from the Region 
        in which the trail was created.

        Args:
            name (str): Specifies the name or the CloudTrail ARN of the trail to be started

        """
        client = self.client
        res = []

        try:
            response = client.start_logging(Name=Name)

            iDebug(callerid(), pop_meta(response))

            # Consolidated Result
            return True

        except Exception as err:
            iWarning(f'API call faied for {callerid()} {self.region} {get_region_location(self.region)}', err)

        return False

    def lookup_events(self, 
                      start_time: datetime, 
                      end_time: datetime,
                      filter: list=[{'EventName': 'ConsoleLogin'}, {'EventName': 'GetRole'}], 
                      ) -> list:
        """Returns list of given lookup_events. Default EventName of ConsoleLogin or GetRole
        
        Args:
            start_time (datetime):      Datetime of look start time
            end_time (datetime):        Datetime of look  time
            filter (list):              List of dictionaries of [{AttributeKey: AttributeValue}]. Default [{'EventName': 'ConsoleLogin'}, {'EventName': 'GetRole'}]
            
            AttributeKey (str):         EventId | EventName | ReadOnly | Username | ResourceType | ResourceName | EventSource | AccessKeyId
            AttributeValue (str):       String value
        """
        iInfo(f"start_time: {start_time}")
        iInfo(f"end_time  : {end_time}")
        iInfo(f"filter    : {filter}")

        client = self.client
        response = {}
        res = []
        nextToken = None
        maxResults = 50
        res = []

        for rs in filter:
            for k, v in rs.items():
                lookup_attributes = [{
                    'AttributeKey': k,
                    'AttributeValue': v
                }]
                iInfo(f"lookup_attributes: {lookup_attributes}")

                # Process each Lookup separately and consolidate
                while True:
                    try:
                        if not nextToken:
                            response = client.lookup_events(
                                LookupAttributes=lookup_attributes,
                                StartTime=start_time,
                                EndTime=end_time,
                                MaxResults=maxResults
                            )
                        else:
                            response = client.lookup_events(
                                LookupAttributes=lookup_attributes,
                                StartTime=start_time,
                                EndTime=end_time,
                                MaxResults=maxResults,
                                NextToken=nextToken
                            )

                        iDebug(callerid(), pop_meta(response))

                        # Consolidated Result
                        iInfo(f"{len(response['Events'])} Events Exported for {rs} ")
                        res.extend(response['Events'])

                    except Exception as err:
                        iWarning(f'API call faied for {callerid()} {self.region} {get_region_location(self.region)}', err)

                    nextToken = response.get('NextToken')

                    if not nextToken:
                        break

        return res

    def update_trail(self, 
            Name: str,
            S3BucketName: str,
            S3KeyPrefix: str,
            SnsTopicName: str,
            IncludeGlobalServiceEvents: bool = True,
            IsMultiRegionTrail: bool = True,
            EnableLogFileValidation: bool = True,
        ):
        """Updates trail settings that control what events you are logging, and how to handle log files

        Args:
            name (str): Specifies the name or the CloudTrail ARN of the trail to be deleted

            Return dict
        """
        client = self.client
        res = {}

        try:
            response = client.update_trail(
                Name=Name,
                S3BucketName=S3BucketName,
                S3KeyPrefix=S3KeyPrefix,
                SnsTopicName=SnsTopicName,
                IncludeGlobalServiceEvents=True,
                IsMultiRegionTrail=True,
                EnableLogFileValidation=True
            )

            iDebug(callerid(), pop_meta(response))

            res = pop_meta(response)


        except Exception as err:
            iWarning(f'API call faied for {callerid()} {self.region} {get_region_location(self.region)}', err)

        return res
        pass


class ConfigService:
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/config.html

    def __init__(self, region_name=None, profile_name=None) -> None:
        sess  = boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()
        self.client = sess.client('config', region_name=region_name) if region_name else sess.client('config')
        self.region = region_name

    def describe_config_rules(self):
        client = self.client
        response = {}
        nextToken = None
        res = []

        while True:
            try:
                if not nextToken:
                    response = client.describe_config_rules()
                else:
                    response = client.describe_config_rules(NextToken=nextToken)

                iDebug('ConfigService / DescribeConfigRules', pop_meta(response))

                # Consolidated Result
                for rs in response['ConfigRules']:
                    rs['region'] = self.region
                    res.append(rs) 
            except Exception as err:
                iWarning(f'API call faied for {callerid()} {self.region} {get_region_location(self.region)}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res

    def describe_configuration_recorders(self):
        """Returns list of Configuration Recorders"""
        client = self.client
        response = {}
        res = {}

        try:
            response = client.describe_configuration_recorders()

            iDebug('ConfigService / DescribeConfigurationRecorders', pop_meta(response))

            # Consolidated Result
            res = response['ConfigurationRecorders'][0]

        except Exception as err:
            iWarning(f'API call faied for {callerid()} {self.region} {get_region_location(self.region)}', err)

        return res

    def describe_configuration_recorder_status(self, ConfigurationRecorderNames: list = []):
        """Returns the current status of the specified configuration recorder 
        as well as the status of the last recording event for the recorder
        
        Args:
            ConfigurationRecorderNames (list): The name(s) of the configuration recorder. 
            If the name is not specified, the action returns the current status of all the 
            configuration recorders associated with the account
        """
        client = self.client

        res = {}

        try:
            response = client.describe_configuration_recorder_status(
                ConfigurationRecorderNames=ConfigurationRecorderNames
            )

            iDebug(f'ConfigService / DescribeConfigurationRecorderStatus', pop_meta(response))

            # Consolidated Result
            res = response['ConfigurationRecordersStatus'][0]

        except Exception as err:
            iWarning(f'API call faied for {callerid()} {self.region} {get_region_location(self.region)}', err)

        return res


    def describe_delivery_channels(self):
        """Returns List of DescribeDeliveryChannels"""
        client = self.client
        response = {}
        res = {}

        try:
            response = client.describe_delivery_channels()

            iDebug(f'ConfigService / DescribeDeliveryChannels', pop_meta(response))

            # Consolidated Result
            res = response['DeliveryChannels'][0]

        except Exception as err:
            iWarning(f'API call faied for {callerid()} {self.region} {get_region_location(self.region)}', err)

        return res

    def describe_delivery_channel_status(self, delivery_channel_names):
        """Returns List of DescribeDeliveryChannels"""
        client = self.client

        res = {}

        try:
            response = client.describe_delivery_channel_status(DeliveryChannelNames=delivery_channel_names)

            iDebug(f'ConfigService / DescribeDeliveryChannelStatus', pop_meta(response))

            # Consolidated Result
            res = response['DeliveryChannelsStatus']

        except Exception as err:
            iWarning(f'API call faied for {callerid()} {self.region} {get_region_location(self.region)}', err)

        return res

    def delete_configuration_recorder(self, recorder: str) -> bool:
        """DeleteconfigurationRecorder

        Args:
            recorder (str): Configuration recorder name

        Returns True or False
        """
        client = self.client

        try:
            response = client.delete_configuration_recorder(ConfigurationRecorderName=recorder)
            iDebug(f'ConfigService / DeleteConfigurationRecorder', pop_meta(response))
            return True
        except Exception as err:
            iWarning(f'API call faied for {callerid()} {self.region} {get_region_location(self.region)}', err)
            return False

    def delete_delivery_channel(self, channel: str) -> bool:
        """DeleteDeliveryChannel

        Args:
            channel (str): delivery channel name

        Returns True or False
        """
        client = self.client

        try:
            response = client.delete_delivery_channel(DeliveryChannelName=channel)
            iDebug(f'ConfigService / DeleteDeliveryChannel', pop_meta(response))
            return True
        except Exception as err:
            iWarning(f'API call faied for {callerid()} {self.region} {get_region_location(self.region)}', err)
            return False

    def put_configuration_recorder(self, name: str, role_arn: str) -> bool:
        """Creates a new configuration recorder to record configuration changes

        Args:
            name (str): The name of the configuration recorder.
            role_arn (str): ARN of the IAM role assumed & used by Config recorder

        Returns True or False
        """
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/config/client/put_configuration_recorder.html
        client = self.client

        try:
            response = client.put_configuration_recorder(
                    ConfigurationRecorder={
                        'name': name,
                        'roleARN': role_arn,
                    })

            iDebug(f'ConfigService / PutConfigurationRecorder', pop_meta(response))
            return True
        except Exception as err:
            iWarning(f'API call faied for {callerid()} {self.region} {get_region_location(self.region)}', err)
            return False

    def put_delivery_channel(self, 
            name: str,
            s3BucketName: str,
            s3KeyPrefix: str) -> bool:
        """Creates a delivery channel deliver config & compliance info to S3 bucket

        Args:
            name (str): The name of the delivery channel
            s3BucketName (str): S3 bucket for Config snapshots & history files
            s3KeyPrefix (str): The prefix for Config S3 bucket

        Returns True or False
        """
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/config/client/put_delivery_channel.html
        client = self.client

        try:
            response = client.put_delivery_channel(
                DeliveryChannel={
                    'name': name,
                    's3BucketName': s3BucketName,
                    's3KeyPrefix': s3KeyPrefix
                }
            )

            iDebug(f'ConfigService / PutDeliveryChannel', pop_meta(response))
            return True
        except Exception as err:
            iWarning(f'API call faied for {callerid()} {self.region} {get_region_location(self.region)}', err)
            return False

    def start_configuration_recorder(self, ConfigurationRecorderName: str) -> bool:
        """Starts recording configuration

        Args:
            ConfigurationRecorderName (str): The name of the recorder

        Returns True or False
        """
        client = self.client

        try:
            response = client.start_configuration_recorder(ConfigurationRecorderName=ConfigurationRecorderName)

            iDebug(f'ConfigService / StartConfigurationRecorder', pop_meta(response))
            return True
        except Exception as err:
            iWarning(f'API call faied for {callerid()} {self.region} {get_region_location(self.region)}', err)
            return False

    def stop_configuration_recorder(self, ConfigurationRecorderName: str) -> bool:
        """Stops recording configurations

        Args:
            ConfigurationRecorderName (str): The name of the recorder

        Returns True or False
        """
        client = self.client

        try:
            response = client.stop_configuration_recorder(ConfigurationRecorderName=ConfigurationRecorderName)

            iDebug(f'ConfigService / StopConfigurationRecorder', pop_meta(response))
            return True
        except Exception as err:
            iWarning(f'API call faied for {callerid()} {self.region} {get_region_location(self.region)}', err)
            return False


class DirectConnect:

    def __init__(self, region_name=None, profile_name=None) -> None:
        sess  = boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()
        self.client = sess.client('directconnect', region_name=region_name) if region_name else sess.client('directconnect')
        self.region = region_name

    def describe_direct_connect_gateways(self, directConnectGatewayId: str | None = None):
        """Returns list of Direct Connect Gateways

        Args:
            directConnectGatewayId (str | None): list of all resource if None else list requested resource 
        """
        client = self.client
        response = {}
        nextToken = None
        maxResults = 100
        res = []

        while True:
            try:
                if not nextToken:
                    if directConnectGatewayId is None:
                        response = client.describe_direct_connect_gateways(
                            maxResults=maxResults
                        )
                    else:
                        response = client.describe_direct_connect_gateways(
                            directConnectGatewayId=directConnectGatewayId,
                            maxResults=maxResults
                        )
                else:
                    if directConnectGatewayId is None:
                        response = client.describe_direct_connect_gateways(
                            nextToken=nextToken,
                            maxResults=maxResults
                        )
                    else:
                        response = client.describe_direct_connect_gateways(
                            nextToken=nextToken,
                            maxResults=maxResults
                        )

                iDebug('DirectConnect / DescribeDirectConnectGateways', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['directConnectGateways']]

            except Exception as err:
                iWarning(f'API call faied for {callerid()}', err)

            nextToken = response.get('nextToken')

            if not nextToken:
                break

        return res

    def describe_virtual_gateways(self):
        """Returns list of Direct Connect Gateways"""
        client = self.client
        res = []

        try:
            response = client.describe_virtual_gateways( )

            iDebug('DirectConnect / DescribeVirtualGateways', pop_meta(response))

            # Consolidated Result
            [res.append(rs) for rs in response['virtualGateways']]

        except Exception as err:
            iWarning(f'API call faied for {callerid()}', err)

        return res

    def describe_virtual_interfaces(self):
        """Returns list of Direct Connect Virtual Interfaces"""
        client = self.client
        res = []

        try:
            response = client.describe_virtual_interfaces()

            iDebug('DirectConnect / DescribeVirtualInterfaces', pop_meta(response))

            # Consolidated Result
            [res.append(rs) for rs in response['virtualInterfaces']]

        except Exception as err:
            iWarning(f'API call faied for {callerid()}', err)

        return res

    def describe_direct_connect_gateway_associations(self, directConnectGatewayId: str | None = None):
        """Returns list of Direct Connect Gateway Associations

        Args:
            directConnectGatewayId (str | None): list of all resource if None else list requested resource 
        """
        client = self.client
        response = {}
        nextToken = None
        maxResults = 100
        res = []

        while True:
            try:
                if not nextToken:
                    if directConnectGatewayId is None:
                        response = client.describe_direct_connect_gateway_associations(
                            maxResults=maxResults
                        )
                    else:
                        response = client.describe_direct_connect_gateway_associations(
                            directConnectGatewayId=directConnectGatewayId,
                            maxResults=maxResults
                        )
                else:
                    if directConnectGatewayId is None:
                        response = client.describe_direct_connect_gateway_associations(
                            nextToken=nextToken,
                            maxResults=maxResults
                        )
                    else:
                        response = client.describe_direct_connect_gateway_associations(
                            directConnectGatewayId=directConnectGatewayId,
                            nextToken=nextToken,
                            maxResults=maxResults
                        )

                iDebug('DirectConnect / DescribeDirectConnectGatewayAssociations', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['directConnectGatewayAssociations']]

            except Exception as err:
                iWarning(f'API call faied for {callerid()}', err)

            nextToken = response.get('nextToken')

            if not nextToken:
                break

        return res

    def describe_direct_connect_gateway_attachments(self, directConnectGatewayId: str | None = None):
        """Returns list of Direct Connect Gateway Attachements

        Args:
            directConnectGatewayId (str | None): list of all resource if None else list requested resource 
        """
        client = self.client
        response = {}
        nextToken = None
        maxResults = 100
        res = []

        while True:
            try:
                if not nextToken:
                    if directConnectGatewayId is None:
                        response = client.describe_direct_connect_gateway_attachments(
                            maxResults=maxResults
                        )
                    else:
                        response = client.describe_direct_connect_gateway_attachments(
                            directConnectGatewayId=directConnectGatewayId,
                            maxResults=maxResults
                        )
                else:
                    if directConnectGatewayId is None:
                        response = client.describe_direct_connect_gateway_attachments(
                            nextToken=nextToken,
                            maxResults=maxResults
                        )
                    else:
                        response = client.describe_direct_connect_gateway_attachments(
                            directConnectGatewayId=directConnectGatewayId,
                            nextToken=nextToken,
                            maxResults=maxResults
                        )

                iDebug('DirectConnect / DescribeDirectConnectGatewayAttachments', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['directConnectGatewayAttachments']]

            except Exception as err:
                iWarning(f'API call faied for {callerid()}', err)

            nextToken = response.get('nextToken')

            if not nextToken:
                break

        return res


class EC2:
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html

    def __init__(self, 
                 region_name=None,
                 profile_name=None,
                 account='', 
                 dont_quit=True, 
                 role='cs/p-support',
                 ) -> None:
        if account:
            sess = get_session(account, dont_quit=True, role=role, region_name=region_name) if region_name else get_session(account, dont_quit=True, role=role)
        else:
            sess  = boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()
            
        self.client = sess.client('ec2', region_name=region_name) if region_name else sess.client('ec2')
        self.region = region_name

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_images.html
    def describe_images(self, 
                        ExecutableUsers:list=['self'], 
                        Filters:list=[{'Name': 'creation-date', 'Values':['*']}], # multiple filters are joined with an 'AND'
                        Owners:list=['self', '144538309574'], # (1445-3830-9574) [gesos]
                        IncludeDeprecated=True,
                        IncludeDisabled=True,
                        DryRun=False

        ):
        """Return list of AMI images
        
        Args:
            ExecutableUsers (list):     List of launch permissions of ['ACCOUNT_ID', 'self', 'all']. Default ['Self']
            Filters (list):             List of filters. Multiple filters  are joined with an 'AND'
            Owners (list):              List of AMI Owners. Default ['self', '144538309574'], # (1445-3830-9574) [gesos]
                                        List of AWS Account IDs, self, amazon, and aws-marketplac
            IncludeDeprecated (bool):   Specifies whether to include deprecated AMIs. Default False
            IncludeDisabled (bool):     Specifies whether to include disabled AMIs. Default False
            DryRun (bool):              Checks required permissions for the action with reponse message. Default False

        """
        client = self.client
        paginator = client.get_paginator('describe_images')

        response = {}
        nextToken = None
        maxResults = 100
        res = []

        while True:
            try:
                if not nextToken:
                    PaginationConfig = {
                        'MaxItems': maxResults,
                        'PageSize': maxResults,
                    }
                else:
                    PaginationConfig = {
                        'MaxItems': maxResults,
                        'PageSize': maxResults,
                        'StartingToken': nextToken
                    }

                iterator = paginator.paginate(
                    ExecutableUsers=ExecutableUsers,
                    Filters=Filters,
                    Owners=Owners,
                    IncludeDeprecated=IncludeDeprecated,
                    IncludeDisabled=IncludeDisabled,
                    DryRun=DryRun,
                    PaginationConfig=PaginationConfig
                )

                for i, page in enumerate(iterator):
                    for rs in page['Images']:
                        region_data = {
                            'Region': self.region,
                            'RegionLocation': get_region_location(self.region)
                        }
                        rSet = {**region_data, **rs}
                        iDebug('EC2 / Describe Images', pop_meta(rSet))
                        region_fmt = get_region_fmt(region=self.region)
                        iInfo(f'EC2 / Describe Images :: Page {i+1} :: {region_fmt} {len(rSet)}')

                        # Consolidated Result
                        res.append(rSet)

                iInfo(f'EC2 / Describe Images :: {i+1} Pages :: {region_fmt} {len(res)}')

            except Exception as err:
                iWarning(f'API call faied for {callerid()}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res

    def describe_image_attribute(self, ImageId:str, Attribute='launchPermission', DryRun:bool=False):
        """Describe Image Attribute
        
        Args:
            Attribute (str):    Default launchPermission. One of description, kernel, ramdisk, launchPermission, productCodes, blockDeviceMapping, sriovNetSupport, bootMode, tpmSupport, uefiData, lastLaunchedTime, imdsSupport, deregistrationProtection
            ImageId (str):      Image ID
            DryRun (bool):      Dry-Run, default False
        """
        res = {}
        client = self.client

        try:
            response = client.describe_image_attribute(
                Attribute=Attribute,
                ImageId=ImageId,
                DryRun=DryRun
            )
            res = pop_meta(response)
        except Exception as err:
            iWarning(f'API call faied for create EIP', err)

        return res

    def allocate_address(self):
        """Allocates an Elastic IP address to an account"""
        res = {}
        client = self.client

        try:
            response = client.allocate_address(Domain='vpc',)
            res = pop_meta(response)
        except Exception as err:
            iWarning(f'API call faied for create EIP', err)

        return res

    def create_nat_gateway(self, AllocationId: str, SubnetId: str, ConnectivityType: str):
        """Creates a NAT gateway in the specified subnet

        Args:
             AllocationId (str):
             SubnetId (str):
             connectivitytype (str): 
        """
        res = {}
        client = self.client

        if ConnectivityType not in [ 'private', 'public' ]:
            iAbort(f"Invalid ConnectivityType! Valid value is one of 'private', 'public'")

        try:
            if ConnectivityType == 'public':
                response = client.create_nat_gateway(
                    AllocationId=AllocationId,
                    SubnetId=SubnetId,
                    ConnectivityType=ConnectivityType
                )
            else:
                # You cannot specify an Elastic IP address with a private NAT gateway.
                response = client.create_nat_gateway(
                    SubnetId=SubnetId,
                    ConnectivityType=ConnectivityType
                )

            # response['NatGateway']['NatGatewayId']
            res = pop_meta(response)

        except Exception as err:
            iWarning(f'API call faied for {callerid()}', err)

        return res

    def delete_transit_gateway_vpc_attachment(self, TransitGatewayAttachmentId: str):
        client = self.client

        res = {}
        try:
            response = client.delete_transit_gateway_vpc_attachment(
                TransitGatewayAttachmentId=TransitGatewayAttachmentId
            )
            # res = response['TransitGatewayVpcAttachment']
            res = pop_meta(response)
        except Exception as err:
            iWarning(f'API call faied for {callerid()}', err)

        return res

    def describe_flow_logs(self):
        """Returns flow logs in current client region"""
        client = self.client

        res = []
        try:
            response = client.describe_flow_logs()

            if 'FlowLogs' in response:
                for rs in response['FlowLogs']:
                    rs['Region'] = self.region
                    res.append(rs)

        except Exception as err:
            iWarning(f'API call faied for {callerid()}', err)

        return res

    def describe_instances(self, filters=[{'Name': 'Name', 'Values': ['ISS-GR-NAT']}]) -> list:
        client = self.client
        res = []
        try:
            response = client.describe_instances(Filters=filters)
            if bool(response):
                for reservation in (response["Reservations"]):
                    for instance in reservation["Instances"]:
                        res.append(instance["InstanceId"])

        except Exception as err:
            iWarning(f'API call faied for {callerid()}! Filter {filters} Error:', err)

        return res

    def describe_nat_gateways(self):
        client = self.client
        response = {}
        nextToken = None
        maxResults = 100
        res = []

        while True:
            try:
                if not nextToken:
                    response = client.describe_nat_gateways(
                        MaxResults=maxResults,
                    )
                else:
                    response = client.describe_nat_gateways(
                        NextToken=nextToken,
                        MaxResults=maxResults,
                    )

                iDebug('EC2 / Describe NAT Gateways', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['NatGateways']]
            except Exception as err:
                iWarning(f'API call faied for {callerid()}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res

    def describe_regions(self):
        """Returns list of active regions"""
        client = self.client

        res = []
        response = {}
        try:
            response = client.describe_regions()
            [res.append(rs) for rs in response['Regions']]

        except Exception as err:
            iAbort(f'API call faied for {callerid()}', err)

        return res

    def describe_route_tables(self):
        """Returns route tables for all active regions"""
        client = self.client

        res = []
        try:
            response = client.describe_route_tables()

            [res.append(rs) for rs in response['RouteTables']]

        except Exception as err:
            iWarning(f'API call faied for {callerid()}', err)

        return res

    def describe_transit_gateway_vpc_attachments(self):
        """Describes transit gateway vpc attachemnts"""
        client = self.client
        response = {}
        nextToken = None
        maxResults = 100
        res = []

        while True:
            try:
                if not nextToken:
                    response = client.describe_transit_gateway_vpc_attachments(
                        MaxResults=maxResults,
                    )
                else:
                    response = client.describe_transit_gateway_vpc_attachments(
                        NextToken=nextToken,
                        MaxResults=maxResults,
                    )

                iDebug('EC2 / Describe TGW Attachements', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['TransitGatewayVpcAttachments']]
            except Exception as err:
                iWarning(f'Unable to Describe TGW Attachements', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res

    def describe_vpcs(self):
        """Returns VPCs in current client region
        
        Args:
            region_filter (str): region to filter and return result for one region
        """
        client = self.client
        nextToken = None
        res = []

        while True:
            try:
                if not nextToken:
                    response = client.describe_vpcs()
                else:
                    response = client.describe_vpcs(
                        NextToken=nextToken,
                    )

                iDebug('EC2 / DescribeVpcs', pop_meta(response))

                # Consolidated Result
                if 'Vpcs' in response:
                    for rs in response['Vpcs']:
                        rs['Region'] = self.region
                        res.append(rs)

            except Exception as err:
                iWarning(f'API call faied for {callerid()}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res

    def describe_vpc_endpoints(self):
        """Returns VPC Endpoints in current client region
        """
        client = self.client
        nextToken = None
        res = []

        while True:
            try:
                if not nextToken:
                    response = client.describe_vpc_endpoints()
                else:
                    response = client.describe_vpc_endpoints(
                        NextToken=nextToken,
                    )

                iDebug(callerid(), pop_meta(response))

                # Consolidated Result
                for rs in response['VpcEndpoints']:
                    rs['Region'] = self.region
                    res.append(rs)

            except Exception as err:
                iWarning(f'API call faied for {callerid()}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res

    def describe_vpc_endpoint_connections(self):
        """Returns VPC Endpoints Connections in current client region

        Describes the VPC endpoint connections to your VPC endpoint services, including any endpoints that are pending your acceptance.
        """
        client = self.client
        nextToken = None
        res = []

        while True:
            try:
                if not nextToken:
                    response = client.describe_vpc_endpoint_connections()
                else:
                    response = client.describe_vpc_endpoint_connections(
                        NextToken=nextToken,
                    )

                iDebug(callerid(), pop_meta(response))

                # Consolidated Result
                for rs in response['VpcEndpointConnections']:
                    rs['Region'] = self.region
                    res.append(rs)

            except Exception as err:
                iWarning(f'API call faied for {callerid()}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res

    def disassociate_route_table(self, AssociationId: str):
        """Dissassociates given route table"""
        client = self.client

        try:
            client.disassociate_route_table(AssociationId=AssociationId)
            return True

        except Exception as err:
            iWarning(f'API call faied for {callerid()}', err)
        
        return None

    def terminate_instances(self, instance_ids: list = []):
        client = self.client
        try:
            response = client.terminate_instances(InstanceIds=instance_ids)
            return True

        except Exception as err:
            iWarning(f'API call faied for {callerid()}', err)

        return None


class ELBV2:
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html

    def __init__(self, 
                 region_name=None,
                 profile_name=None,
                 account='', 
                 dont_quit=True, 
                 role='cs/p-support',
                 ) -> None:
        if account:
            sess = get_session(account, dont_quit=True, role=role, region_name=region_name) if region_name else get_session(account, dont_quit=True, role=role)
        else:
            sess  = boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()
            
        self.client = sess.client('elbv2', region_name=region_name) if region_name else sess.client('elbv2')
        self.region = region_name

    def describe_load_balancers(self):
        """Describe Load Balancers"""
        client = self.client
        response = {}
        Marker = None
        PageSize = 100
        res = []

        while True:
            try:
                if not Marker:
                    response = client.describe_load_balancers(
                        PageSize=PageSize,
                    )
                else:
                    response = client.describe_load_balancers(
                        Marker=Marker,
                        PageSize=PageSize,
                    )

                iDebug('ELBV2 / Describe Load Balancers', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['LoadBalancers']]

            except Exception as err:
                iWarning(f'API call faied for {callerid()}', err)

            Marker = response.get('Marker')

            if not Marker:
                break

        return res

    def describe_load_balancer_attributes(self, LoadBalancerArn: str):
        """Describes the attributes for the specified Application Load Balancer, Network Load Balancer, or Gateway Load Balancer.

        Args:
             LoadBalancerArn (str): Load Balancer ARN
        """
        client = self.client
        response = {}
        res = []

        try:
            response = client.describe_load_balancer_attributes(
                LoadBalancerArn=LoadBalancerArn,
            )

            iDebug('ELBV2 / Describe Load Balancer Attributes', pop_meta(response))

            # Consolidated Result
            res = response['Attributes']

        except Exception as err:
            iWarning(f'API call faied for {callerid()}', err)

        return res


# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/network-firewall.html
class Firewall:

    def __init__(self, region_name=None, profile_name=None) -> None:
        sess  = boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()
        self.client = sess.client('network-firewall', region_name=region_name) if region_name else sess.client('network-firewall')
        self.region = region_name

    def list_firewalls(self) -> list:
        """Returns list of Network Firewalls"""
        client = self.client
        response = {}
        nextToken = None
        maxResults = 100
        res = []

        while True:
            try:
                if not nextToken:
                    response = client.list_firewalls(
                        MaxResults=maxResults,
                    )
                else:
                    response = client.list_firewalls(
                        NextToken=nextToken,
                        MaxResults=maxResults,
                    )

                iDebug('Network Firewall / List Firewalls', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['Firewalls']]

            except Exception as err:
                iWarning(f'API call faied for {callerid()}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res

    def describe_firewall(self, firewallName, firewallArn=None):
        """Returns Desribe Firewall Result

        Args:
            firewallName (str): Name of Firewall. Required if firewallArn not given.
            firewallArn  (str): Firewall ARN. Required if firewallName not given.

        Usage:
            describe_firewall( firewallName )
            describe_firewall( firewallArn )
            describe_firewall( firewallName, firewallArn )

        """
        client = self.client

        response = {}
        res = {}
        try:
            # Both params are given
            if firewallArn:
                response = client.describe_firewall(
                    FirewallName=firewallName,
                    FirewallArn=firewallArn
                )
            # Single param with arn: -
            elif 'arn:' in firewallName and firewallArn is None:
                response = client.describe_firewall(
                    FirewallArn=firewallArn
                )
            else:
                response = client.describe_firewall(
                    FirewallName=firewallName
                )

            iDebug(f'Network Firewall / Describe Firewall / {firewallName}', pop_meta(response))

            res = pop_meta(response)

        except Exception as err:
            iWarning(f'API call faied for {callerid()}', err)

        return res


class IAM:

    def __init__(self, region_name=None, profile_name=None) -> None:
        sess  = boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()
        self.client = sess.client('iam', region_name=region_name) if region_name else sess.client('iam')
        self.region = region_name

    def list_account_aliases(self):
        """Returns Account Alias"""
        client = self.client

        res = ''
        try:
            response = client.list_account_aliases()['AccountAliases'][0]
        
            iDebug('IAM / ListAccountAliases', pop_meta(response))

            res = pop_meta(response)
        except Exception as err:
            iWarning(f'API call faied for {callerid()}', err)

        return res

    def get_account_password_policy(self):
        """Returns Account Password Policy"""
        client = self.client

        res = {}
        try:
            response = client.get_account_password_policy()

            iDebug('IAM / GetAccountPasswordPolicy', pop_meta(response))

            res = pop_meta(response)
        except Exception as err:
            iWarning(f'API call faied for {callerid()}', err)

        return res

    def get_saml_provider(self, arn: str):
        """Returns the SAML provider metadocument that was uploaded when 
        the IAM SAML provider resource object was created or updated"""
        client = self.client

        res = {}
        try:
            response = client.get_saml_provider(SAMLProviderArn=arn)

            iDebug('IAM / GetSamlProvider', pop_meta(response))

            res = pop_meta(response)
        except Exception as err:
            iWarning(f'API call faied for {callerid()}', err)

        return res

    def delete_saml_provider(self, arn: str):
        """Deletes a SAML provider resource in IAM"""
        client = self.client

        res = {}
        try:
            response = client.delete_saml_provider(SAMLProviderArn=arn)

            iDebug('IAM / DeleteSAMLProvider', pop_meta(response))

            return True
        except Exception as err:
            iWarning(f'API call faied for {callerid()}', err)

        return False

    def get_account_summary(self):
        """Returns Dict of IAM Account Summary"""
        client = self.client

        res = {}
        try:
            response = client.get_account_summary()

            iDebug(callerid(), pop_meta(response))

            res = pop_meta(response)

            return True
        except Exception as err:
            iWarning(f'API call faied for {callerid()}', err)

        return res

    def list_roles(self):
        """List IAM roles

        Returns list of Roles
        """
        client = self.client

        res = []

        Marker = None
        MaxItems = 1000
        # iam:ListRoles
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

                iDebug(callerid(), pop_meta(response))

                # Consolidated Result
                res = response['Roles']

            except Exception as err:
                iWarning(f'API call faied for {callerid()}', err)

            Marker = response.get('Marker')

            if Marker is None:
                break
        
        return res

    def list_roles_policies(self, roles):
        """List Roles Policies"""
        client = self.client

        res = []
        MaxItems = 1000

        for role in roles:
            roleName = role['RoleName']

            # Init vars for roles
            lastUsedDate = ''
            lastRegion = ''
            instanceProfiles = []

            # Get iam role last used date and region
            roleDetail = client.get_role(RoleName=role['RoleName'])
            rss = roleDetail['Role']['RoleLastUsed']

            lastUsedDate = str(rss['LastUsedDate']) if 'LastUsedDate' in rss else ''
            lastRegion = rss['Region'] if 'Region' in rss else ''

            # Check for instance_profiles
            iTrace(f"List Instance Profiles for Role: {str(role['RoleName'])}")
            paginator = client.get_paginator('list_instance_profiles_for_role')
            rs = paginator.paginate(
                RoleName=role['RoleName'],
                PaginationConfig={'MaxItems': MaxItems}
            )

            for instance in rs:
                if len(instance['InstanceProfiles']) > 0:
                    if len(instanceProfiles) > 0:
                        instanceProfiles.append(instance['InstanceProfiles'])
                    else:
                        instanceProfiles = instance['InstanceProfiles']

            # Pull list of attached policies for role
            attached_policies = []
            try:
                attached_policies = client.list_attached_role_policies(RoleName=roleName)['AttachedPolicies']
                iTrace("Attached Policies: ", attached_policies)
            except Exception as err:
                iWarning(f'List attached role policy failed for {roleName}!', err)

            # Pull list of inline policy for role
            role_policies = []
            try:
                role_policies = client.list_role_policies(RoleName=roleName)['PolicyNames']
                iTrace("Inline Policies:", role_policies)
            except Exception as err:
                iWarning(f'List role policies failed for {roleName}!', err)

            # A role can have multiple policy statementents
            for statement in role['AssumeRolePolicyDocument']['Statement']:

                trust_entity_principals = statement['Principal']
                iTrace('Trust Entity Principls:', trust_entity_principals)

                # Principal the type of entity trusted, such as Service, AWS, or Federated
                for principal in trust_entity_principals:

                    # A principal might have a value of a string, or a value of a list.
                    # to simplify the handling, i check if the principal value is a string
                    # and if so, i put it in a list
                    trust_entities = trust_entity_principals[principal]
                    if isinstance(trust_entity_principals[principal], str):
                        trust_entities = [trust_entities]

        # Add attached & inline policies to role for backup
        role['lastUsedDate'] = lastUsedDate
        role['lastRegion'] = lastRegion
        role['AttachedPolicy'] = attached_policies
        role['RolePolicies'] = role_policies
        role['InstanceProfiles'] = instanceProfiles

        # append in-scope roles to result
        res['Roles'].append(role)

        # List & append IAM Roles Policies
        policies_unique = []  # unique list of policies arn
        for role in roles:
            for policy in role['AttachedPolicy']:
                # Aws managed policy - no need to backup
                if policy['PolicyArn'].split(':')[4] != 'aws':
                    if not (policy['PolicyArn'] in policies_unique):
                        policies_unique.append(policy['PolicyArn'])
                        path = ''
                        splitPolicy = policy['PolicyArn'].split('/')

                        if len(splitPolicy) > 1:
                            path = '/'
                        if len(splitPolicy) > 2:
                            path = f'/' + splitPolicy[1] + '/'

                        policy = {**{'Path': path}, **policy}
                        res['PoliciesList'].append(policy)

        self.roles = res['Roles']
        self.policies_list = res['PoliciesList']

        return res

    def list_policies(self, policies):
        """List IAM Policies

        Returns policies
        """
        client = self.client

        res = []
        policies_list = self.policies_list
        myPath = ''

        for policy in policies_list:
            if not myPath and 'IamPolicies' in policy and len(policy['IamPolicies']) > 0:
                myPath = policy['IamPolicies'][0]['Path'].replace('/', '')

        # IAM Policies
        for rs in policies:
            policyName = rs['PolicyName']
            policyArn = rs['PolicyArn']
            try:
                myPolicy = client.get_policy(PolicyArn=policyArn)['Policy']
                versions = client.list_policy_versions(
                    PolicyArn=policyArn, MaxItems=1000)['Versions']

                # Get Policy by Version ID
                for id, version in enumerate(versions):
                    policyDocument = client.get_policy_version(
                        PolicyArn=policyArn,
                        VersionId=version['VersionId'])['PolicyVersion']['Document']
                    versions[id]['Document'] = policyDocument

                myPolicy['Versions'] = versions

                # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/client.html#IAM.Client.list_entities_for_policy
                # PolicyGroups - Skip if any
                # PolicyUsers - Skip if any
                # PolicyRoles
                response = client.list_entities_for_policy(
                    PolicyArn=policyArn,
                    MaxItems=1000
                )
                myPolicy['PolicyGroups'] = response['PolicyGroups']
                myPolicy['PolicyUsers'] = response['PolicyUsers']
                myPolicy['PolicyRoles'] = response['PolicyRoles']
                myPolicy['IsTruncated'] = response['IsTruncated']

                res.append(myPolicy)
            except Exception as err:
                iWarning(f'IAM Policy data extraction error!', err)

        return res

    def list_saml_providers(self):
        """Lists the SAML provider resource objects defined in IAM in the account"""
        client = self.client

        res = []
        try:
            response = client.list_saml_providers()

            iDebug('IAM / ListSamlProviders', pop_meta(response))

            [res.append(rs) for rs in response['SAMLProviderList']]

        except Exception as err:
            iWarning(f'API call faied for {callerid()}', err)

        return res


class IamRolesCleanup:
    """Backup & Cleanup IAM Roles & their Policies if Policies not is-use by any User nor Group

    Args:
        account (str): AWS account id - will be converted to leading zeros 12 chars
        alias (str): AWS account alias
        datafolder (str): Stores results to {datafolder}/[backup|delete]-{alias}-iam-roles.json
        PathPrefix (str): Roles PathPrefix in format of '/PathPrefix/'
        exclusion_roles (list): List of roles which should be excluded from deletion, default is []
        InScope (bool): Only backup in-scope iam roles otherwise backup all roles for given path

    Permissions:
        iam:DeleteInstanceProfile
        iam:DeletePolicy
        iam:DeleteRole
        iam:DeleteRolePolicy
        iam:DetachPolicy
        iam:DetachRole
        iam:GetPaginator
        iam:GetPolicy
        iam:GetPolicyVersion
        iam:GetRole
        iam:ListAttachedRolePolicies
        iam:ListEntitiesForPolicy
        iam:ListPolicyVersions
        iam:ListPolicyVersions
        iam:ListRolePolicies
        iam:ListRoles
        iam:RemoveRoleFromInstanceProfile
    """

    def __init__(self,
                 account: str,          # required
                 alias: str,            # required
                 datafolder: str,       # required
                 PathPrefix: str,       # required
                 exclusion_roles: list = [],
                 InScope: bool = True,
                 region=None,
                 profile_name=None
                 ) -> None:
        # validation
        if not ( account and alias and datafolder and PathPrefix ):
            iAbort(f"Missing one or more required arguments of: account, alias, datafolder, PathPrefix")

        # TODO: Rmove to enable deletion
        self.dryrun = True

        self.account = ndigits(account, 12)
        self.alias = alias
        self.backup_file = f'{datafolder}/backup-{alias}-iam-roles.josn'
        self.delete_file = f'{datafolder}/delete-{alias}-iam-roles.josn'
        self.PathPrefix = PathPrefix
        self.PathPrefixStr = PathPrefix.replace('/', '-')
        self.exclusion_roles = exclusion_roles
        self.InScope = InScope

        self.roles = []
        self.policies = []
        self.policies_list = []

        self.deleted_roles = []
        self.deleted_policies = []

        self.excludedPolicyGroups = []
        self.excludedPolicyUsers = []

        # session & client
        sess  = boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()
        self.client = sess.client('iam', region_name=region) if region else sess.client('iam')
        self.region = region

    def backup(self):
        """Backups IAM roles & their policies for given PathPrefix"""
        res = {}
        res['BackupRoles'] = self.backup_roles()
        res['BackupPoliciesList'] = self.get_policies_list()
        res['BackupPolicies'] = self.backup_policies()

        return res

    def backup_roles(self):
        """Backups IAM roles & their policies list for given PathPrefix

        Returns { res['Roles]: [], res['PoliciesList'] and updates self.roles & self.policies_list
        """
        iInfo("Backup IAM Roles")

        # read data
        PathPrefix = self.PathPrefix
        exclusion_roles = self.exclusion_roles
        InScope = self.InScope
        myCounter = 8

        client = self.client

        res = {
            'Roles': [],
            'PoliciesList': [],
        }

        roles = []
        Marker = None
        MaxItems = 1000
        # iam:ListRoles
        while True:
            try:
                if Marker is None:
                    response = client.list_roles(
                        PathPrefix=PathPrefix,
                        MaxItems=MaxItems
                    )
                else:
                    response = client.list_roles(
                        PathPrefix=PathPrefix,
                        Marker=Marker,
                        MaxItems=MaxItems
                    )

                iDebug('IAM / List Roles', pop_meta(response))

                # Consolidated Result
                [roles.append(rs) for rs in response['Roles']]

            except Exception as err:
                iWarning(f'API call faied for List Roles', err)

            Marker = response.get('Marker')

            if Marker is None:
                break

        for role in roles:
            roleName = role['RoleName']

            # Init vars for roles
            lastUsedDate = ''
            lastRegion = ''
            instanceProfiles = []

            # If in-scope filter roles otherwise don't filter roles
            if InScope:
                InScopeFilter = roleName not in exclusion_roles and role['Path'] == PathPrefix
            else:
                InScopeFilter = True

            if InScopeFilter:
                iInfo("Role: " + str(role))

                myCounter = progress_print(counter=myCounter)

                # Get iam role last used date and region
                roleDetail = client.get_role(RoleName=role['RoleName'])
                rss = roleDetail['Role']['RoleLastUsed']

                lastUsedDate = str(rss['LastUsedDate']) if 'LastUsedDate' in rss else ''
                lastRegion = rss['Region'] if 'Region' in rss else ''

                # Check for instance_profiles
                iInfo(f"List Instance Profiles for Role: {str(role['RoleName'])}")
                paginator = client.get_paginator('list_instance_profiles_for_role')
                rs = paginator.paginate(
                    RoleName=role['RoleName'],
                    PaginationConfig={'MaxItems': MaxItems}
                )

                for instance in rs:
                    if len(instance['InstanceProfiles']) > 0:
                        if len(instanceProfiles) > 0:
                            instanceProfiles.append(instance['InstanceProfiles'])
                        else:
                            instanceProfiles = instance['InstanceProfiles']

                # Pull list of attached policies for role
                attached_policies = []
                try:
                    attached_policies = client.list_attached_role_policies(RoleName=roleName)['AttachedPolicies']
                    iInfo("Attached Policies: ", attached_policies)
                except Exception as err:
                    iWarning(f'List attached role policy failed for {roleName}!', err)

                # Pull list of inline policy for role
                role_policies = []
                try:
                    role_policies = client.list_role_policies(RoleName=roleName)['PolicyNames']
                    iInfo("Inline Policies:", role_policies)
                except Exception as err:
                    iWarning(f'List role policies failed for {roleName}!', err)

                # A role can have multiple policy statementents
                for statement in role['AssumeRolePolicyDocument']['Statement']:

                    trust_entity_principals = statement['Principal']
                    iInfo('Trust Entity Principls:', trust_entity_principals)

                    # Principal the type of entity trusted, such as Service, AWS, or Federated
                    for principal in trust_entity_principals:

                        # A principal might have a value of a string, or a value of a list.
                        # to simplify the handling, i check if the principal value is a string
                        # and if so, i put it in a list
                        trust_entities = trust_entity_principals[principal]
                        if isinstance(trust_entity_principals[principal], str):
                            trust_entities = [trust_entities]

            # Exclude Roles based on exclusion_roles for backup
            if roleName in exclusion_roles:
                iInfo(f'Excluding role! Role {roleName} is on the exclusion list.')
            elif role['Path'] == PathPrefix:
                # Append data if its in scope
                # Add attached & inline policies to role for backup
                role['lastUsedDate'] = lastUsedDate
                role['lastRegion'] = lastRegion
                role['AttachedPolicy'] = attached_policies
                role['RolePolicies'] = role_policies
                role['InstanceProfiles'] = instanceProfiles

                # append in-scope roles to result
                res['Roles'].append(role)

        # List & append IAM Roles Policies
        policies_unique = []  # unique list of policies arn
        for role in roles:
            for policy in role['AttachedPolicy']:
                # Aws managed policy - no need to backup
                if policy['PolicyArn'].split(':')[4] != 'aws':
                    if not (policy['PolicyArn'] in policies_unique):
                        policies_unique.append(policy['PolicyArn'])
                        path = ''
                        splitPolicy = policy['PolicyArn'].split('/')

                        if len(splitPolicy) > 1:
                            path = '/'
                        if len(splitPolicy) > 2:
                            path = f'/' + splitPolicy[1] + '/'

                        # Only same PathPrefix policies
                        if path == PathPrefix:
                            policy = {**{'Path': path}, **policy}
                            res['PoliciesList'].append(policy)

        # update class data
        self.roles = res['Roles']
        self.policies_list = res['PoliciesList']

        return res

    def backup_policies(self):
        """Backups IAM Policies

        Returns policies & updates self.policies

        Reads self.policies and update it with policies data
        Backups roles & policies list first if self.roles is empty
        """
        if not self.roles:
            self.backup_iam_roles()

        client = self.client
        myCounter = 8

        policies = []
        policies_list = self.policies_list
        myPath = ''

        for policy in policies_list:
            if not myPath and 'IamPolicies' in policy and len(policy['IamPolicies']) > 0:
                myPath = policy['IamPolicies'][0]['Path'].replace('/', '')

        # IAM Policies
        for rs in policies_list:
            policyName = rs['PolicyName']
            policyArn = rs['PolicyArn']
            try:
                myPolicy = client.get_policy(PolicyArn=policyArn)['Policy']
                versions = client.list_policy_versions(
                    PolicyArn=policyArn, MaxItems=1000)['Versions']

                # Get Policy by Version ID
                for id, version in enumerate(versions):
                    policyDocument = client.get_policy_version(
                        PolicyArn=policyArn,
                        VersionId=version['VersionId'])['PolicyVersion']['Document']
                    versions[id]['Document'] = policyDocument
                    # print(f"{l1} {policyArn} {version['VersionId']}")
                    myCounter = progress_print(counter=myCounter)

                myPolicy['Versions'] = versions

                # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/client.html#IAM.Client.list_entities_for_policy
                # PolicyGroups - Skip if any
                # PolicyUsers - Skip if any
                # PolicyRoles
                response = client.list_entities_for_policy(
                    PolicyArn=policyArn,
                    MaxItems=1000
                )
                myPolicy['PolicyGroups'] = response['PolicyGroups']
                myPolicy['PolicyUsers'] = response['PolicyUsers']
                myPolicy['PolicyRoles'] = response['PolicyRoles']
                myPolicy['IsTruncated'] = response['IsTruncated']

                policies.append(myPolicy)
            except Exception as err:
                iWarning(f'IAM Policy data extraction error!', err)

        # update class data
        self.policies = policies
        self.set_inuse_policies(policies)

        return policies

    def delete(self):
        """Deletes IAM roles & their policies for given PathPrefix"""
        res = {}
        res['DeletedRoles'] = self.delete_roles()
        res['DeletedPoliciesList'] = self.get_policies_list()
        res['DeletedPolicies'] = self.delete_policies()

        return res

    def delete_roles(self):
        """Deletes IAM Roles from self.roles

        Returns deleted roles list and updates self.deleted_roles
        """
        if not self.roles:
            iWarning(f'Found no IAM Role to delete!')
            return

        if self.dryrun:
            return

        roles = self.roles
        client = self.client
        iam = client.resource('iam')
        myCounter = 8
        res = []

        for rs in roles:
            roleName = rs['RoleName']
            role = iam.Role(roleName)

            rsReport = {
                'RoleName': roleName,
                'DeleteRolePolicy': [],
                'DetachPolicy': [],
                'RemoveRoleFromInstanceProfile': [],
                'DeleteInstanceProfile': [],
                'DeleteRole': []
            }

            # Inline policies ( DeleteRolePolicy )
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/client.html#IAM.Client.delete_role_policy

            for policyName in rs['RolePolicies']:
                myMsg = f"Delete inline policy {policyName} from role {roleName}"
                try:
                    response = client.delete_role_policy(
                        RoleName=roleName,
                        PolicyName=policyName
                    )
                    iInfo(myMsg)
                    myCounter = progress_print(counter=myCounter)
                    rsReport['DeleteRolePolicy'].append({
                        'RoleName': roleName,
                        'PolicyName': policyName,
                        'Response': response
                    })
                except Exception as err:
                    myMsg = f"Couldn't delete inline policy {policyName} from role {roleName}"
                    if err.response['Error']['Code'] == 'NoSuchEntity':
                        iWarning(f"{err.response['Error']['Code']}. {myMsg}")
                    else:
                        myCounter = progress_print(counter=myCounter, char='-')
                        errMsg = err.response['Error']['Code']
                        rsReport['DeleteRolePolicy'].append({
                            'RoleName': roleName,
                            'PolicyName': policyName,
                            'Error': errMsg
                        })
                        iWarning(f'{errMsg}. {myMsg}')

            # Attached managed policies ( DetachPolicy )
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/client.html#IAM.Group.detach_policy

            for attachedPolicy in rs['AttachedPolicy']:
                policyArn = attachedPolicy['PolicyArn']

                myMsg = f"Detach policy {policyArn} from role {roleName}"
                try:
                    response = role.detach_policy(PolicyArn=policyArn)
                    iInfo(myMsg)
                    myCounter = progress_print(counter=myCounter)
                    rsReport['DetachPolicy'].append({
                        'RoleName': roleName,
                        'PolicyArn': policyArn,
                        'Response': response
                    })
                except Exception as err:
                    myMsg = f"Couldn't detach policy {policyArn} from role {roleName}"
                    if err.response['Error']['Code'] == 'NoSuchEntity':
                        iWarning(f"{err.response['Error']['Code']}. {myMsg}")
                    else:
                        myCounter = progress_print(counter=myCounter, char='-')
                        errMsg = err.response['Error']['Code']
                        rsReport['DetachPolicy'].append({
                            'RoleName': roleName,
                            'PolicyArn': policyArn,
                            'Error': errMsg
                        })
                        iWarning(f'{errMsg}. {myMsg}')

            # Instance profile ( RemoveRoleFromInstanceProfile )
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/client.html#IAM.Client.remove_role_from_instance_profile

            for instanceProfile in rs['InstanceProfiles']:
                instanceProfileName = instanceProfile['InstanceProfileName']

                myMsg = f"Remove role {roleName} from instance profile {instanceProfileName}"
                try:
                    response = client.remove_role_from_instance_profile(
                        InstanceProfileName=instanceProfileName,
                        RoleName=roleName
                    )
                    iInfo(myMsg)
                    myCounter = progress_print(counter=myCounter)
                    rsReport['RemoveRoleFromInstanceProfile'].append({
                        'RoleName': roleName,
                        'InstanceProfileName': instanceProfileName,
                        'Response': response
                    })
                except Exception as err:
                    myMsg = f"Couldn't remove role from instance profile {instanceProfileName} from role {roleName}"
                    if err.response['Error']['Code'] == 'NoSuchEntity':
                        iWarning(f"{err.response['Error']['Code']}. {myMsg}")
                    else:
                        myCounter = progress_print(counter=myCounter, char='-')
                        errMsg = err.response['Error']['Code']
                        rsReport['RemoveRoleFromInstanceProfile'].append({
                            'RoleName': roleName,
                            'InstanceProfileName': instanceProfileName,
                            'Error': errMsg
                        })
                        iWarning(f'{errMsg}. {myMsg}')

            # Optional – Delete instance profile ( DeleteInstanceProfile )
            for instanceProfile in rs['InstanceProfiles']:
                instanceProfileName = instanceProfile['InstanceProfileName']

                myMsg = f"Delete instance profile {instanceProfileName}"
                try:
                    response = client.delete_instance_profile(InstanceProfileName=instanceProfileName)
                    iInfo(myMsg)
                    myCounter = progress_print(counter=myCounter)
                    rsReport['DeleteInstanceProfile'].append({
                        'InstanceProfileName': instanceProfileName,
                        'Response': response
                    })
                except Exception as err:
                    myMsg = f"Couldn't delete instance profile {instanceProfileName}"
                    if err.response['Error']['Code'] == 'NoSuchEntity':
                        iWarning(f"{err.response['Error']['Code']}. {myMsg}")
                    else:
                        myCounter = progress_print(counter=myCounter, char='-')
                        errMsg = err.response['Error']['Code']
                        rsReport['DeleteInstanceProfile'].append({
                            'InstanceProfileName': instanceProfileName,
                            'Error': errMsg
                        })
                        iWarning(f'{errMsg}. {myMsg}')

            # Delete Role (delete)
            myMsg = f"Delete role {roleName}"
            try:
                response = client.delete_role(RoleName=roleName)
                iInfo(myMsg)
                myCounter = progress_print(counter=myCounter)
                rsReport['DeleteRole'].append({
                    'RoleName': roleName,
                    'Response': response
                })
            except Exception as err:
                myMsg = f"Couldn't delete role {roleName}"
                if err.response['Error']['Code'] == 'NoSuchEntity':
                    iWarning(f"{err.response['Error']['Code']}. {myMsg}")
                else:
                    iWarning(err.response)
                    myCounter = progress_print(counter=myCounter, char='-')
                    errMsg = err.response['Error']['Code']
                    rsReport['DeleteRole'].append({
                        'RoleName': roleName,
                        'Error': errMsg
                    })
                    iWarning(f'{errMsg}. {myMsg}')

            # Append role deletion processes to the final report
            res.append(rsReport)

        # update class
        self.deleted_roles = res

        return res

    def delete_policies(self):
        """Deletes IAM Roles' Policies if not in-use by any Group or User

        Returns deleted policies list and updates self.delete_policies
        """

        if self.dryrun:
            return

        policies = self.policies
        PathPrefix = self.PathPrefix
        client = self.client
        iam = client.resource('iam')
        myCounter = 8

        res = []

        # read in-use policies by Groups & Users generated by backup
        excludedPolicyGroups = self.get_inuse_policies(policies)['excludedPolicyGroups']
        excludedPolicyUsers = self.get_inuse_policies(policies)['excludedPolicyUsers']

        # Remove policy from deletion if it has PolicyGroups or PolicyUsers
        for rs in policies:
            if len(rs['PolicyGroups']) > 0:
                if rs['Arn'] not in excludedPolicyGroups:
                    excludedPolicyGroups.append({
                        'PolicyName': rs['PolicyName'],
                        'PolicyId': rs['PolicyId'],
                        'Arn': rs['Arn'],
                        'Description': rs.get('Description', ''),
                        'Path': rs['Path'],
                        'PolicyGroups': rs['PolicyGroups']
                    })
            if len(rs['PolicyUsers']) > 0:
                if rs['Arn'] not in excludedPolicyUsers:
                    excludedPolicyUsers.append({
                        'PolicyName': rs['PolicyName'],
                        'PolicyId': rs['PolicyId'],
                        'Arn': rs['Arn'],
                        'Description': rs['Description'] if 'Description' in rs else '',
                        'Path': rs['Path'],
                        'UserGroups': rs['UserGroups']
                    })

        print()
        policyGroupsCount = len(excludedPolicyGroups)
        print(to_len(f'Excluded Policies with PolicyGroups ({str(policyGroupsCount)})'))
        print(str(excludedPolicyGroups))
        iInfo(f'Excluded ({policyGroupsCount}) Policies with PolicyGroups {excludedPolicyGroups}')

        print()
        policyUsersCount = len(excludedPolicyUsers)
        print(to_len(f'Excluded Policies with PolicyUsers ({str(policyUsersCount)})'))
        print(str(excludedPolicyUsers))
        iInfo(f'Excluded ({str(len(excludedPolicyUsers))}) Policies with PolicyUsers {str(excludedPolicyUsers)}')

        myCounter = 8
        i = 1
        for rs in policies:
            # Excluded Policies with PolicyGroups or PolicyUsers
            excludePolicy = False
            for exPolicy in excludedPolicyGroups:
                if rs['Arn'] == exPolicy['Arn']:
                    iInfo( f"PolicyGroups Excluded from cleanup: {rs['Arn']}")
                    excludePolicy = True
            for exPolicy in excludedPolicyUsers:
                if rs['Arn'] == exPolicy['Arn']:
                    iInfo( f"PolicyUsers Excluded from cleanup: {rs['Arn']}")
                    excludePolicy = True

            if isDebug():
                if excludePolicy:
                    print(f" {to_space('-')}. SKIP", end=' ')

                print(f"Versions:    {len(rs['Versions'])}", end=' ')
                print(f"Groups:      {len(rs['PolicyGroups'])}", end=' ')
                print(f"Users:       {len(rs['PolicyUsers'])}", end=' ')
                print(f"Roles:       {len(rs['PolicyRoles'])}", end=' ')
                print(f"IsTruncated: {rs['IsTruncated']}", end=' ')

                if excludePolicy:
                    print(f"Name: {rs['PolicyName']}", end=' ')
                    print(f"##Excluded##")
                else:
                    print(f"Name: {rs['PolicyName']}")

            if excludePolicy:
                continue

            i += 1

            rsReport = {
                'PolicyName': rs['PolicyName'],
                'DetachPolicyGroups': [],                   # Do not detach if has member
                'DetachPolicyUsers': [],                    # Do not detach if has member
                'DetachPolicyRoles': [],
                'DeletePolicyVersions': [],
                'DeletePolicy': {},
            }

            policy = client.Policy(rs['Arn'])

            # DetachPolicyRoles
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam/policy/detach_role.html
            for rss in rs['PolicyRoles']:
                myMsg = f"Detach PolicyRoles {rss['RoleName']} from policy {rs['Arn']}"
                try:
                    response = policy.detach_role(RoleName=rss['RoleName'])
                    iInfo(myMsg)
                    myCounter = progress_print(counter=myCounter)
                    rsReport['DetachPolicyRoles'].append({
                        'RoleName': rss['RoleName'],
                        'PolicyArn': rss['Arn'],
                        'Response': response
                    })
                except Exception as err:
                    iWarning(str(err))
                    myCounter = progress_print(counter=myCounter, char='-')
                    rsReport['DetachPolicyRoles'].append({
                        'RoleName': rss['RoleName'],
                        'PolicyArn': rs['Arn'],
                        'Error': find_between(err)
                    })

            # DeletePolicyVersions
            myMsg = f"Cleanup Policy Verisons for {rs['PolicyName']} {rs['Arn']}"
            try:
                response = client.list_policy_versions(PolicyArn=rs['Arn'])['Versions']
                for ver in response:
                    if not ver['IsDefaultVersion']:
                        policy_version = client.PolicyVersion(rs['Arn'], ver['VersionId'])
                        try:
                            response = policy_version.delete()
                            myMsg = f"Delete Policy Verison {ver['VersionId']} for {rs['Arn']}"
                            iInfo(myMsg)
                            myCounter = progress_print(counter=myCounter)
                            rsReport['DeletePolicyVersions'].append({
                                'RoleName': rss['RoleName'],
                                'PolicyArn': rs['Arn'],
                                'PolicyVersion': ver['VersionId'],
                                'Response': response
                            })
                        except Exception as err:
                            iWarning(str(err))
                            myCounter = progress_print(counter=myCounter, char='-')
                            rsReport['DeletePolicyVersions'].append({
                                'RoleName': rss['RoleName'],
                                'PolicyArn': rs['Arn'],
                                'PolicyVersion': ver['VersionId'],
                                'Error': find_between(err)
                            })
            except Exception as err:
                iWarning(str(err))
                rsReport['DeletePolicyVersions'].append({
                    'RoleName': rss['RoleName'],
                    'PolicyArn': rs['Arn'],
                    'Error': find_between(err)
                })

            # DeletePolicy (delete)
            myMsg = f"Cleanup Policy {rs['PolicyName']} {rs['Arn']}"
            try:
                response = client.delete_policy(PolicyArn=rs['Arn'])
                myCounter = progress_print(counter=myCounter)
                iInfo(myMsg)
                rsReport['DeletePolicy'] = {
                    'RoleName': rss['RoleName'],
                    'PolicyArn': rs['Arn'],
                    'Response': True
                }
            except Exception as err:
                myCounter = progress_print(counter=myCounter, char='-')
                rsReport['DeletePolicy'] = {
                    'RoleName': rss['RoleName'],
                    'PolicyArn': rs['Arn'],
                    'Error': find_between(err)
                }

            # Append role processes to the final report only if policy exist
            if not ('Error' in rsReport['DeletePolicy'] and 'NoSuchEntity' in rsReport['DeletePolicy']['Error']):
                res.append(rsReport)

        # update class
        self.deleted_policies = res

        return res

    def set_inuse_policies(self, policies: list):
        """Returns list of in-use policies in Groups and Users

        Arguments:
            policies (list): list of policies data from client.get_policy() call
        """
        excludedPolicyGroups = []
        excludedPolicyUsers = []
        # Remove policy from deletion if it has PolicyGroups or PolicyUsers
        for rs in policies:
            if len(rs['PolicyGroups']) > 0:
                if rs['Arn'] not in excludedPolicyGroups:
                    excludedPolicyGroups.append({
                        'PolicyName': rs['PolicyName'],
                        'PolicyId': rs['PolicyId'],
                        'Arn': rs['Arn'],
                        'Description': rs.get('Description', ''),
                        'Path': rs['Path'],
                        'PolicyGroups': rs['PolicyGroups']
                    })
            if len(rs['PolicyUsers']) > 0:
                if rs['Arn'] not in excludedPolicyUsers:
                    excludedPolicyUsers.append({
                        'PolicyName': rs['PolicyName'],
                        'PolicyId': rs['PolicyId'],
                        'Arn': rs['Arn'],
                        'Description': rs['Description'] if 'Description' in rs else '',
                        'Path': rs['Path'],
                        'UserGroups': rs['UserGroups']
                    })

        # update class
        self.excludedPolicyGroups = excludedPolicyGroups  # Policy in-use by Groups
        self.excludedPolicyUsers = excludedPolicyUsers  # Policy in-use by Users

        return {
            'ExcludedPolicyGroups': excludedPolicyGroups,
            'ExcludedPolicyUsers': excludedPolicyUsers,
        }

    def get_roles(self):
        """Returns processed roles data"""
        return self.roles

    def get_policies(self):
        """Returns processed policies for processed roles data"""
        return self.policies

    def get_policies_list(self):
        """Returns list of policies used by processed roles"""
        return self.policies_list

    def get_deleted_roles(self):
        """Returns deleted roles data"""
        return self.deleted_roles

    def get_deleted_policies(self):
        """Returns deleted policies data"""
        return self.deleted_policies

    def get_inuse_policies(self):
        """Returns excluded policies in-use by Groups or Users"""
        return {
            'excludedPolicyGroups': self.excludedPolicyGroups,
            'excludedPolicyUsers': self.excludedPolicyUsers,
        }


class GuardDuty:
    # https://docs.aws.amazon.com/guardduty/latest/APIReference/API_Operations.html
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/guardduty.html

    def __init__(self, region_name=None, profile_name=None, quite=False) -> None:
        sess  = boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()
        self.client = sess.client('guardduty', region_name=region_name) if region_name else sess.client('guardduty')
        self.region = region_name
        self.quite = quite

    def accept_administrator_invitation(self, 
            DetectorId: str, 
            AdministratorId: str, 
            InvitationId: str
        ):
        """Accept administrator Invitation
        
        Args:
            DetectorId (str): detector id is unique per account per region
            AdministratorId (str): Administrator account id
            InvitationId (str): invitation id
        """
        client = self.client

        res = {}
        response = {}
        try:
            response = client.accept_administrator_invitation(
                DetectorId=DetectorId,
                AdministratorId=AdministratorId,
                InvitationId=InvitationId
            )

            iDebug(f'{callerid()} / DetectorId {DetectorId}', pop_meta(response))

            # Consolidated Result
            res = get_response(response)

        except Exception as err:
            iWarning(f'API call faied for {callerid()} / DetectorId {DetectorId} /  AdministratorId {AdministratorId} / InvitationId {InvitationId} {self.region}', err)

        return res

    def create_detector(self, Enable: bool=True):
        client = self.client

        res = {}
        response = {}
        try:
            response = client.create_detector(
                Enable=Enable
            )

            iDebug(callerid(), pop_meta(response))

            # Consolidated Result
            res = response['DetectorId']

        except Exception as err:
            iWarning(f'API call faied for {callerid()} {self.region}', err)

        return res

    def create_members(self, 
            DetectorId: str, 
            AccountDetails: list, 
        ):
        """Create accounts to become members of GuardDuty Master
        
        Args:
            DetectorId (str): detector id is unique per account per region
            AccountDetails (list): [{'AccountId': AccountIds, 'Email': Email}]
        """
        client = self.client

        res = []
        response = {}
        try:
            response = client.create_members(
                DetectorId=DetectorId,
                AccountDetails=AccountDetails,
            )

            iDebug(f'{callerid()} / DetectorId {DetectorId}', pop_meta(response))

            # Consolidated Result
            res = response.get('UnprocessedAccounts', [])

        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} / DetectorId {DetectorId} {self.region}', err)

        return res

    def create_publishing_destination(self, 
            DetectorId: str, 
            DestinationArn: str,
            KmsKeyArn: str
        ):
        """Creates a publishing destination to export findings to. 
        
        Args:
            DetectorId (str): The ID of the GuardDuty detector associated with the publishing destination
            DestinationArn (str): The ARN of the S3 bucket to publish to
            KmsKeyArn (str): The ARN of the KMS key to use for encryption - must be in the same region as S3 Bucket
        """
        client = self.client

        res = []
        response = {}
        try:
            response = client.create_publishing_destination(
                DetectorId=DetectorId,
                DestinationType='S3',
                DestinationProperties={
                    'DestinationArn': DestinationArn,
                    'KmsKeyArn': KmsKeyArn
                }
            )

            iDebug(f'GuardDuty / CreatePublishingDestination / DetectorId {DetectorId}', pop_meta(response))

            # Consolidated Result
            res = response['DestinationId']

        except Exception as err:
            # if PublishingDestination exist below returns correct result instead of false positive warning
            if 'already exists' in str(err).lower():
                res = client.list_publishing_destinations(DetectorId=DetectorId)    
            else:      
                if not self.quite: iWarning(f'Unable to CreatePublishingDestination / DetectorId {DetectorId} {self.region}', err)

        return res

    def create_sample_findings(self, 
            DetectorId: str, 
            FindingTypes: list=[
                'Backdoor:EC2/DenialOfService.Tcp',
                'Backdoor:EC2/Spambot',
                'UnauthorizedAccess:EC2/SSHBruteForce'
            ], 
        ):
        """Create accounts to become members of GuardDuty Master
        
        Args:
            DetectorId (str): detector id is unique per account per region
        """
        client = self.client

        res = []
        response = {}
        try:
            response = client.create_sample_findings(
                DetectorId=DetectorId,
                FindingTypes=FindingTypes,
            )

            iDebug(f'GuardDuty / CreateSampleFindings / DetectorId {DetectorId}', pop_meta(response))

            return True if response['ResponseMetadata'] == 200 else False

        except Exception as err:
            if not self.quite: iWarning(f'Unable to CreateSampleFindings / DetectorId {DetectorId} {self.region}', err)

        return False

    def decline_invitations(self, AccountIds: list):
        client = self.client

        res = {}
        response = {}
        try:
            response = client.decline_invitations(
                AccountIds=AccountIds
            )

            iDebug(f'GuardDuty / DeclineInvitations', pop_meta(response))

            # Consolidated Result
            res = response

            if response.get('UnprocessedAccounts'):
                if not self.quite: iWarning(f'UnprocessedAccounts for DeclineInvitations', response['UnprocessedAccounts'])

        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

        return res

    def delete_detector(self, DetectorId: str):
        client = self.client

        res = {}
        response = {}
        try:
            response = client.delete_detector(
                DetectorId=DetectorId
            )

            iDebug(f'GuardDuty / DeleteDetector', pop_meta(response))

            # Consolidated Result
            res = get_response(response)

        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

        return res

    def delete_invitations(self, AccountIds: list):
        client = self.client

        res = {}
        response = {}
        try:
            response = client.delete_invitations(
                AccountIds=AccountIds
            )

            iDebug(f'GuardDuty / DeleteInvitations', pop_meta(response))

            # Consolidated Result
            res = response

            if response.get('UnprocessedAccounts'):
                if not self.quite: iWarning(f'UnprocessedAccounts for DeleteInvitations', response['UnprocessedAccounts'])

        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

        return res

    def delete_members(self, DetectorId: str, AccountIds: list):
        client = self.client

        res = {}
        response = {}
        try:
            response = client.delete_members(
                DetectorId=DetectorId,
                AccountIds=AccountIds
            )

            iDebug(f'GuardDuty / DeleteMembers', pop_meta(response))

            # Consolidated Result
            res = response.get('UnprocessedAccounts', {})

        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

        return res

    def describe_malware_scans(self, DetectorId: str):
        client = self.client
        response = {}
        nextToken = None
        maxResults = 50

        res = []
        response = {}
        while True:
            try:
                if not nextToken:
                    response = client.describe_malware_scans(
                        DetectorId=DetectorId,
                        MaxResults=maxResults,
                    )
                else:
                    iDebug('nextToken', nextToken)
                    response = client.describe_malware_scans(
                        DetectorId=DetectorId,
                        NextToken=nextToken,
                        MaxResults=maxResults,
                    )

                iDebug(f'{callerid()} / DetectorId {DetectorId}', pop_meta(response))

                # Consolidated Result
                if response['Scans']:
                    for rs in response['Scans']:
                        res.append({'DetectorId': DetectorId} | rs)

            except Exception as err:
                if not self.quite: iWarning(f'API call faied for {callerid()} / DetectorId {DetectorId} {self.region}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res

    def describe_organization_configuration(self, DetectorId: str):
        client = self.client
        response = {}
        nextToken = None
        maxResults = 50

        res = []
        while True:
            try:
                if not nextToken:
                    response = client.describe_organization_configuration(
                        DetectorId=DetectorId,
                        MaxResults=maxResults
                    )
                else:
                    iDebug('nextToken', nextToken)
                    response = client.describe_organization_configuration(
                        DetectorId=DetectorId,
                        NextToken=nextToken,
                        MaxResults=maxResults
                    )

                iDebug(f'{callerid()}/ DetectorId {DetectorId}', pop_meta(response))

                # Consolidated Result
                res.append(pop_meta(response))

            except Exception as err:
                if not self.quite: iWarning(f'API call faied for {callerid()} / DetectorId {DetectorId} {self.region}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res

    def describe_publishing_destination(self, DetectorId: str, DestinationId):
        client = self.client

        res = []
        try:
            response = client.describe_publishing_destination(
                DetectorId=DetectorId,
                DestinationId=DestinationId,
            )

            iDebug(f'{callerid()} / DetectorId {DetectorId}', pop_meta(response))

            # Consolidated Result
            res = pop_meta(response)

        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} / DetectorId {DetectorId} {self.region}', err)

        return res

    def disassociate_from_administrator_account(self, DetectorId: str):
        client = self.client

        res = {}
        response = {}
        try:
            response = client.disassociate_from_administrator_account(
                DetectorId=DetectorId
            )

            iDebug(f'GuardDuty / DisassociateFromAdministratorAccount', pop_meta(response))

            # Consolidated Result
            res = response

        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

        return res

    def disassociate_members(self, DetectorId: str, AccountIds: list):
        client = self.client

        res = {}
        response = {}
        try:
            response = client.disassociate_members(
                DetectorId=DetectorId,
                AccountIds=AccountIds
            )

            iDebug(f'{callerid()} / DetectorId {DetectorId}', pop_meta(response))

            # Consolidated Result
            res = response.get('UnprocessedAccounts', {})

        except Exception as err:
            check = 'The request is rejected since no such resource found' 
            if check in str(err):
                iDebug(f'{callerid()} {self.region}', check)
            else:
                if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

        return res

    def get_administrator_account(self, DetectorId: str):
        client = self.client

        res = {}
        response = {}
        try:
            response = client.get_administrator_account(
                DetectorId=DetectorId,
            )

            iDebug(f'{callerid()} / DetectorId {DetectorId}', pop_meta(response))

            # Consolidated Result
            res = response['Administrator']
            res['DetectorId'] = DetectorId

        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} / DetectorId {DetectorId} {self.region}', err)

        return res

    def get_detector(self, DetectorId: str):
        client = self.client

        res = {}
        response = {}
        try:
            response = client.get_detector(
                DetectorId=DetectorId,
            )

            iDebug(f'{callerid()} / DetectorId {DetectorId}', pop_meta(response))

            # Consolidated Result
            if response:
                res = pop_meta(response=response)

        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

        return res

    def get_invitations_count(self) -> int:
        client = self.client

        res = 0
        response = {}
        try:
            response = client.get_invitations_count()

            iDebug(f'{callerid()}', pop_meta(response))

            # Consolidated Result
            res = response['InvitationsCount']

        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

        return res

    def get_malware_scan_settings(self, DetectorId: str):
        client = self.client

        res = {}
        response = {}
        try:
            response = client.get_malware_scan_settings(
                DetectorId=DetectorId,
            )

            iDebug(f'{callerid()} / DetectorId {DetectorId}', pop_meta(response))

            # Consolidated Result
            if response:
                response = pop_meta(response=response)
                res = {'DetectorId': DetectorId} | response

        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} / DetectorId {DetectorId} {self.region}', err)

        return res

    def get_member_detectors(self, DetectorId: str, AccountIds: list):
        """Returns list of GetMemberDetectors details
        
        Args:
            DetectorId (str): Detector ID
            AccountIds (list): list of account IDs
        """
        client = self.client
        res = []
        response = {}
        nextToken = None

        res = []
        while True:
            try:
                if not nextToken:
                    response = client.get_member_detectors(
                        DetectorId=DetectorId,
                        AccountIds=AccountIds,
                    )
                else:
                    iDebug('nextToken', nextToken)
                    response = client.get_member_detectors(
                        DetectorId=DetectorId,
                        AccountIds=AccountIds,
                        NextToken=nextToken,
                    )

                iDebug(f'{callerid()} / DetectorId {DetectorId}', pop_meta(response))

                # Consolidated Result
                for rs in response['MemberDataSourceConfigurations']:
                    res.append(rs)

            except Exception as err:
                if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

            try:
                nextToken = response.get('UnprocessedAccounts')[0]['AccountId']
            except Exception as err:
                if not self.quite: iWarning(f'API call faied for {callerid()} nextToken: {nextToken} {self.region}', err)

            if not nextToken:
                break

        return res

    def get_members(self, DetectorId: str, AccountIds: list):
        client = self.client
        res = []
        response = {}
        nextToken = None

        res = []
        while True:
            try:
                if not nextToken:
                    response = client.get_members(
                        DetectorId=DetectorId,
                        AccountIds=AccountIds,
                    )
                else:
                    iDebug('nextToken', nextToken)
                    response = client.get_members(
                        DetectorId=DetectorId,
                        AccountIds=AccountIds,
                        NextToken=nextToken,
                    )

                iDebug(f'{callerid()} / DetectorId {DetectorId}', pop_meta(response))

                # Consolidated Result
                for rs in response['Members']:
                    res.append(rs)

            except Exception as err:
                if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

            try:
                nextToken = response.get('UnprocessedAccounts')[0]['AccountId']
            except Exception as err:
                if not self.quite: iWarning(f'API call faied for {callerid()} nextToken {self.region}', err)

            if not nextToken:
                break

        return res

    def invite_members(self, 
                       DetectorId: str, 
                       AccountIds: list, 
                       DisableEmailNotification: bool=True,
                       Message: str='',
                ):
        """Invites accounts to become members of GuardDuty Master"""
        client = self.client

        res = []
        response = {}
        try:
            response = client.invite_members(
                DetectorId=DetectorId,
                AccountIds=AccountIds,
                DisableEmailNotification=DisableEmailNotification,
                Message=Message,
            )

            iDebug(f'{callerid()} / DetectorId {DetectorId}', pop_meta(response))

            # Consolidated Result
            res = response.get('UnprocessedAccounts', [])

        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} / DetectorId {DetectorId} / AccountIds {AccountIds} {self.region}', err)

        return res

    def list_coverage(self, DetectorId: str):
        client = self.client
        response = {}
        nextToken = None
        maxResults = 50

        res = []
        while True:
            try:
                if not nextToken:
                    response = client.list_coverage(
                        DetectorId=DetectorId,
                        MaxResults=maxResults,
                    )
                else:
                    iDebug('nextToken', nextToken)
                    response = client.list_coverage(
                        DetectorId=DetectorId,
                        NextToken=nextToken,
                        MaxResults=maxResults,
                    )

                iDebug(f'{callerid()} / DetectorId {DetectorId}', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['Resources']]

            except Exception as err:
                if not self.quite: iWarning(f'API call faied for {callerid()} / DetectorId {DetectorId} {self.region}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res

    def list_detectors(self):
        client = self.client
        response = {}

        res = []
        try:
            response = client.list_detectors()

            iDebug(f'{callerid()}', pop_meta(response))

            # Consolidated Result
            res = response.get('DetectorIds', [])

        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

        return res

    def list_invitations(self):
        client = self.client
        response = {}
        nextToken = None
        maxResults = 50

        res = []
        while True:
            try:
                if not nextToken:
                    response = client.list_invitations(
                        MaxResults=maxResults,
                    )
                else:
                    iDebug('nextToken', nextToken)
                    response = client.list_invitations(
                        NextToken=nextToken,
                        MaxResults=maxResults,
                    )

                iDebug(f'{callerid()}', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['Invitations']]

            except Exception as err:
                if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res

    def list_members(self, DetectorId: str):
        client = self.client
        response = {}
        nextToken = None
        maxResults = 50

        res = []
        while True:
            try:
                if not nextToken:
                    response = client.list_members(
                        DetectorId=DetectorId,
                        MaxResults=maxResults,
                    )
                else:
                    iDebug('nextToken', nextToken)
                    response = client.list_members(
                        DetectorId=DetectorId,
                        NextToken=nextToken,
                        MaxResults=maxResults,
                    )

                iDebug(f'{callerid()} / DetectorId {DetectorId}', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['Members']]

            except Exception as err:
                if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res

    def list_organization_admin_accounts(self):
        client = self.client
        response = {}
        nextToken = None
        maxResults = 50

        res = []
        while True:
            try:
                if not nextToken:
                    response = client.list_organization_admin_accounts(
                        MaxResults=maxResults,
                    )
                else:
                    iDebug('nextToken', nextToken)
                    response = client.list_organization_admin_accounts(
                        NextToken=nextToken,
                        MaxResults=maxResults,
                    )

                iDebug(f'{callerid()}', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['AdminAccounts']]

            except Exception as err:
                if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res

    def list_publishing_destinations(self, DetectorId: str):
        client = self.client
        response = {}
        nextToken = None
        maxResults = 50

        res = []
        while True:
            try:
                if not nextToken:
                    response = client.list_publishing_destinations(
                        DetectorId=DetectorId,
                        MaxResults=maxResults,
                    )
                else:
                    iDebug('nextToken', nextToken)
                    response = client.list_publishing_destinations(
                        DetectorId=DetectorId,
                        NextToken=nextToken,
                        MaxResults=maxResults,
                    )

                iDebug(f'{callerid()} / DetectorId {DetectorId}', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['Destinations']]

            except Exception as err:
                if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res


class RAM:
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ram.html
    resourceTypes = []
    resources = []
    shareAssociations = []
    resourceShares = []
    principals = []
    regions = []

    def __init__(self, region_name=None, profile_name=None) -> None:
        sess  = boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()
        self.client = sess.client('ram', region_name=region_name) if region_name else sess.client('ram')
        self.region = region_name
        self.maxResults = 50

    def list_resource_types(self, scope='ALL'):
        """Returns list of resouce types

        Args:
            scope (str): One of ALL, REGIONAL, GLOBAL (Default is All)
        """
        client = self.client
        scope = self._resourceRegionScope(scope)
        response = {}
        nextToken = None

        res = []
        while True:
            try:
                if not nextToken:
                    response = client.list_resource_types(
                        resourceRegionScope=scope,
                        maxResults=self.maxResults,
                    )
                else:
                    iDebug('nextToken', nextToken)
                    response = client.list_resource_types(
                        resourceRegionScope=scope,
                        maxResults=self.maxResults,
                        nextToken=nextToken,
                    )

                iDebug(f'{callerid()} / Region {scope}', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['resourceTypes']]

            except Exception as err:
                iWarning(f'Unable to list resourceTypes < RAM / List Resources Types / Region {scope} ', err)

            nextToken = response.get('nextToken')

            if not nextToken:
                break

        return res

    def list_resources(self, scope='ALL', owner='SELF'):
        """Returns list of resources

        Args:
            scope (str): One of ALL, REGIONAL, GLOBAL (Default is All)
            owner (str): One of SELF, OTHER-ACCOUNTS (Default is SELF)
        """
        client = self.client
        scope = self._resourceRegionScope(scope)
        owner = self._resourceOwner(owner)

        response = {}
        nextToken = None
        res = []
        while True:
            try:
                if not nextToken:
                    response = client.list_resources(
                        resourceOwner=owner,
                        resourceRegionScope=scope,
                        maxResults=self.maxResults,
                    )
                else:
                    iDebug('nextToken', nextToken)
                    response = client.list_resources(
                        resourceOwner=owner,
                        resourceRegionScope=scope,
                        maxResults=self.maxResults,
                        nextToken=nextToken,
                    )

                iDebug(f'{callerid()} / Region {scope} / Owner {owner}', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['resources']]

            except Exception as err:
                iWarning(f'API call faied for {callerid()} / Region {scope} / Owner {owner}', err)

            nextToken = response.get('nextToken')

            if not nextToken:
                break

        return res

    def get_resource_share_associations(self, aType='PRINCIPAL', aStatus=None):
        """Returns list of resouce types

        Args:
            aType (str): One of PRINCIPAL, RESOURCE (Default is PRINCIPAL)
            aStatus (str): One ASSOCIATING, ASSOCIATED, FAILED, DISASSOCIATING, DISASSOCIATED (Default is ASSOCIATING)
        """
        client = self.client
        aType = self._associationType(aType)
        aStatus = self._associationStatus(aStatus)

        response = {}
        nextToken = None
        res = []
        while True:
            try:
                if not nextToken:
                    if aStatus is None:
                        response = client.get_resource_share_associations(
                            associationType=aType,
                            maxResults=self.maxResults
                        )
                    else:
                        response = client.get_resource_share_associations(
                            associationType=aType,
                            associationStatus=aStatus,
                            maxResults=self.maxResults
                        )
                else:
                    if aStatus is None:
                        response = client.get_resource_share_associations(
                            associationType=aType,
                            nextToken=nextToken,
                            maxResults=self.maxResults
                        )
                    else:
                        response = client.get_resource_share_associations(
                            associationType=aType,
                            associationStatus=aStatus,
                            nextToken=nextToken,
                            maxResults=self.maxResults
                        )

                iDebug(f'{callerid()} / Type {aType}', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['resourceShareAssociations']]

            except Exception as err:
                iWarning(f'API call faied for {callerid()} / Type {aType}', err)

            nextToken = response.get('nextToken')

            if not nextToken:
                break

        return res

    def get_resource_shares(self, owner='SELF', status=None):
        """Returns list of resouce types

        Args:
            owenr ( str): One of SELF, OTHER-ACCOUNTS (Default is SELF)
            status (str): One of PENDING, ACTIVE, FAILED, DELETING, DELETED (Default is PENDING)
        """
        owner = self._resourceOwner(owner)
        status = self._resourceShareStatus(status) if status is not None else None

        client = self.client
        nextToken = None

        res = []
        response = {}
        while True:
            try:
                if not nextToken:
                    if status is None:
                        response = client.get_resource_shares(
                            resourceOwner=owner,
                            maxResults=self.maxResults,
                        )
                    else:
                        response = client.get_resource_shares(
                            resourceShareStatus=status,
                            resourceOwner=owner,
                            maxResults=self.maxResults,
                        )
                else:
                    if status is None:
                        response = client.get_resource_shares(
                            resourceOwner=owner,
                            nextToken=nextToken,
                            maxResults=self.maxResults,
                        )
                    else:
                        response = client.get_resource_shares(
                            resourceShareStatus=status,
                            resourceOwner=owner,
                            nextToken=nextToken,
                            maxResults=self.maxResults,
                        )

                iDebug(f'{callerid()} / Owner {owner}', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['resourceShares']]

            except Exception as err:
                iWarning(f'API call faied for {callerid()} / Owner {owner}', err)

            nextToken = response.get('nextToken')

            if not nextToken:
                break

        return res

    def list_principals(self, owner='SELF'):
        """Returns list of resources

        Args:
            owner (str): One of SELF, OTHER-ACCOUNTS (Default is SELF)
        """
        client = self.client
        owner = self._resourceOwner(owner)

        res = []
        response = {}
        nextToken = None
        while True:
            try:
                if not nextToken:
                    response = client.list_principals(
                        resourceOwner=owner,
                        maxResults=self.maxResults,
                    )
                else:
                    iDebug('nextToken', nextToken)
                    response = client.list_principals(
                        resourceOwner=owner,
                        maxResults=self.maxResults,
                        nextToken=nextToken,
                    )

                iDebug(f'{callerid()} / Owner {owner}', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['principals']]

            except Exception as err:
                iWarning(f'API call faied for {callerid()} / Owner {owner}', err)

            nextToken = response.get('nextToken')

            if not nextToken:
                break

        return res

    def _resourceRegionScope(self, scope):
        scopes = ['ALL', 'REGIONAL', 'GLOBAL']
        return scopes[0] if scope not in scopes else scope

    def _resourceOwner(self, owner):
        owners = ['SELF', 'OTHER-ACCOUNTS']
        return owners[0] if owner not in owners else owner

    def _associationType(self, aType):
        types = ['PRINCIPAL', 'RESOURCE']
        return types[0] if aType not in types else aType

    def _associationStatus(self, status):
        statuses = ['ASSOCIATING', 'ASSOCIATED', 'FAILED', 'DISASSOCIATING', 'DISASSOCIATED']
        return statuses[0] if status not in statuses else status

    def _resourceShareStatus(self, status):
        statuses = ['PENDING', 'ACTIVE', 'FAILED', 'DELETING', 'DELETED']
        return statuses[0] if status not in statuses else status


class Route53Resolver:

    def __init__(self, region_name=None, profile_name=None) -> None:
        sess  = boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()
        self.client = sess.client('route53resolver', region_name=region_name) if region_name else sess.client('route53resolver')
        self.region = region_name

    def delete_resolver_endpoint(self, resolver_id: str):
        client = self.client
        res = {}
        try:
            response = client.delete_resolver_endpoint(ResolverEndpointId=resolver_id)
            res = response

        except Exception as err:
            iWarning(f'API call faied for {callerid()}', err)

        return res

    def delete_resolver_rule(self, resolver_rule_id: str):
        client = self.client
        res = {}
        try:
            response = client.delete_resolver_rule(ResolverRuleId=resolver_rule_id)
            res = response
        except Exception as err:
            iWarning(f'Unable to delete Route53 Resolver Rules', err)

        return res

    def list_resolver_endpoints(self) -> list:
        client = self.client
        res = []
        try:
            response = client.list_resolver_endpoints()
            if len(response['ResolverEndpoints'] > 0):
                for id in range(len(response['ResolverEndpoints'])):
                    res.append(response['ResolverEndpoints'][id]['Id'])

        except Exception as err:
            iWarning(f'API call faied for {callerid()}', err)

        return res

    def list_resolver_rules(self) -> list:
        client = self.client
        res = []
        try:
            response = client.list_resolver_rules()
            for rule_id in range(len(response['ResolverRules'])):
                res.append(response['ResolverRules']['Id'])

        except Exception as err:
            iWarning(f'API call faied for {callerid()}', err)

        return res


class SecurityHub:

    def __init__(self, region_name=None, quite=False) -> None:
        sess = boto3.Session() if not region_name else boto3.Session(region_name=region_name)
        self.client = sess.client('securityhub') if not region_name else sess.client('securityhub', region_name=region_name)
        self.region = region_name
        self.quite = quite

    def accept_administrator_invitation(self, AdministratorId: str, InvitationId: str):
        client = self.client

        res = {}
        response = {}
        try:
            response = client.accept_administrator_invitation(
                AdministratorId=AdministratorId,
                InvitationId=InvitationId
            )

            iDebug(f'securityhub / {callerid()}', pop_meta(response))

            # Consolidated Result
            res = response

        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} / AdministratorId {AdministratorId} / InvitationId {InvitationId} {self.region}', err)

        return res

    def create_members(self, 
                       AccountDetails: list, 
                ):
        """Create accounts to become members of securityhub Master
        
        Args:
            AccountDetails (list): [{'AccountId': 'string', 'Email': 'string'}]
        """
        client = self.client

        res = []
        response = {}
        try:
            response = client.create_members(
                AccountDetails=AccountDetails,
            )

            iDebug(f'{callerid()}', pop_meta(response))

            # Consolidated Result
            res = response.get('UnprocessedAccounts', [])

        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

        return res

    def decline_invitations(self, AccountIds: list):
        client = self.client

        res = {}
        response = {}
        try:
            response = client.decline_invitations(
                AccountIds=AccountIds
            )

            iDebug(f'{callerid()}', pop_meta(response))

            # Consolidated Result
            res = response

            if response.get('UnprocessedAccounts'):
                iWarning(f'UnprocessedAccounts for {callerid()}', response['UnprocessedAccounts'])

        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

        return res

    def delete_invitations(self, AccountIds: list):
        client = self.client

        res = {}
        response = {}
        try:
            response = client.delete_invitations(
                AccountIds=AccountIds
            )

            iDebug(f'{callerid()}', pop_meta(response))

            # Consolidated Result
            res = response

            if response.get('UnprocessedAccounts'):
                iWarning(f'UnprocessedAccounts for {callerid()}', response['UnprocessedAccounts'])

        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

        return res

    def delete_members(self, AccountIds: list) -> list:
        """Returns List of DeleteMembers"""
        client = self.client

        res = {}
        try:
            response = client.delete_members(
                AccountIds=AccountIds
            )

            iDebug(f'{callerid()}', pop_meta(response))

            res = response.get('UnprocessedAccounts')

        except Exception as err:
            check = 'The request is rejected since no such resource found' 
            if check in str(err):
                iDebug(f'{callerid()} {self.region}', check)
            else:
                if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

        return res

    def describe_action_targets(self, ActionTargetArns: list = []):
        client = self.client
        response = {}
        nextToken = None
        maxResults = 50

        res = []
        while True:
            try:
                if not nextToken:
                    if ActionTargetArns:
                        response = client.describe_action_targets(
                            ActionTargetArns=ActionTargetArns,
                            MaxResults=maxResults,
                        )
                    else:
                        response = client.describe_action_targets(
                            MaxResults=maxResults,
                        )
                else:
                    iDebug('nextToken', nextToken)
                    if ActionTargetArns:
                        response = client.describe_action_targets(
                            ActionTargetArns=ActionTargetArns,
                            NextToken=nextToken,
                            MaxResults=maxResults,
                        )
                    else:
                        response = client.list_security_control_definitions(
                            NextToken=nextToken,
                            MaxResults=maxResults,
                        )

                iDebug(f'{callerid()}', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['ActionTargets']]

            except Exception as err:
                if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res

    def describe_hub(self, HubArn: str | None = None):
        """Returns dict of Hub status"""
        client = self.client

        res = {}
        try:
            if HubArn:
                response = client.describe_hub(
                    HubArn=HubArn
                )
            else:
                response = client.describe_hub()

            iDebug(f'{callerid()}', pop_meta(response))

            res = pop_meta(response)

        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

        return res

    def describe_organization_configuration(self):
        client = self.client

        res = {}
        response = {}
        try:
            response = client.describe_organization_configuration()

            iDebug(f'{callerid()}', pop_meta(response))

            res = response
        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

        return res

    def describe_standards(self, EnabledByDefault: bool=True):
        """Returns a  of the available standards in Security Hub
        
        Args:
            EnabledByDefault (bool): returns only enabled standards if True or return all
        """
        client = self.client
        maxResults = 50
        response = {}
        nextToken = None

        res = []
        while True:
            try:
                if not nextToken:
                    response = client.describe_standards(
                        MaxResults=maxResults,
                    )
                else:
                    iDebug('nextToken', nextToken)
                    response = client.describe_standards(
                        MaxResults=self.maxResults,
                        NextToken=nextToken,
                    )

                iDebug(f'{callerid()}', pop_meta(response))

                # Consolidated Result
                if EnabledByDefault:
                    [res.append(rs) for rs in response['Standards'] if rs['EnabledByDefault']]
                else:
                    [res.append(rs) for rs in response['Standards']]
            except Exception as err:
                if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res

    def disassociate_from_administrator_account(self):
        client = self.client

        res = {}
        response = {}
        try:
            response = client.disassociate_from_administrator_account()

            iDebug(f'{callerid()}', pop_meta(response))

            # Consolidated Result
            res = get_response(response)

        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

        return res


    def disassociate_members(self, AccountIds: list):
        client = self.client

        res = {}
        response = {}
        try:
            response = client.disassociate_members(
                AccountIds=AccountIds
            )

            iDebug(f'{callerid()}', pop_meta(response))

            # Consolidated Result
            res = response.get('UnprocessedAccounts', {})

        except Exception as err:
            check = 'The request is rejected since no such resource found' 
            if check in str(err):
                iDebug(f'{callerid()} {self.region}', check)
            else:
                if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

        return res

    def enable_security_hub(self):
        client = self.client

        res = {}
        response = {}
        try:
            response = client.enable_security_hub()

            iDebug(f'{callerid()}', pop_meta(response))

            # Consolidated Result
            if response:
                response = pop_meta(response=response)
                res = response

        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

        return res

    def get_administrator_account(self):
        client = self.client

        res = {}
        response = {}
        try:
            response = client.get_administrator_account()

            iDebug(f'{callerid()}', pop_meta(response))

            # Consolidated Result
            res = response['Administrator']

        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

        return res

    def get_enabled_standards(self, StandardsSubscriptionArns: list = []):
        client = self.client
        response = {}
        nextToken = None
        maxResults = 50

        res = []
        try:
            if not nextToken:
                if StandardsSubscriptionArns:
                    response = client.get_enabled_standards(
                        StandardsSubscriptionArns=StandardsSubscriptionArns,
                        MaxResults=maxResults,
                    )
                else:
                    response = client.get_enabled_standards(
                        MaxResults=maxResults,
                    )
            else:
                if StandardsSubscriptionArns:
                    response = client.get_enabled_standards(
                        StandardsSubscriptionArns=StandardsSubscriptionArns,
                        NextToken=nextToken,
                        MaxResults=maxResults,
                    )
                else:
                    response = client.get_enabled_standards(
                        NextToken=nextToken,
                        MaxResults=maxResults,
                    )

            iDebug(f'{callerid()}', pop_meta(response))

            # Consolidated Result
            [res.append(rs) for rs in response['StandardsSubscriptions']]

        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

        return res

    def get_insights(self, InsightArns: list = []):
        client = self.client
        response = {}
        nextToken = None
        maxResults = 50

        res = []
        while True:
            try:
                if not nextToken:
                    if InsightArns:
                        response = client.get_insights(
                            InsightArns=InsightArns,
                            MaxResults=maxResults,
                        )
                    else:
                        response = client.get_insights(
                            MaxResults=maxResults,
                        )

                else:
                    iDebug('nextToken', nextToken)
                    if InsightArns:
                        response = client.get_insights(
                            InsightArns=InsightArns,
                            NextToken=nextToken,
                            MaxResults=maxResults,
                        )
                    else:
                        response = client.get_insights(
                            NextToken=nextToken,
                            MaxResults=maxResults,
                        )

                iDebug(f'{callerid()}', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['Insights']]

            except Exception as err:
                if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res

    def get_invitations_count(self):
        client = self.client

        res = 0
        response = {}
        try:
            response = client.get_invitations_count()

            iDebug(f'{callerid()}', pop_meta(response))

            # Consolidated Result
            res = response['InvitationsCount']

        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

        return res

    def get_members(self, AccountIds: list):
        client = self.client
        response = {}
        nextToken = None

        res = []
        while True:
            try:
                if not nextToken:
                    response = client.get_members(
                        AccountIds=AccountIds,
                    )
                else:
                    iDebug('nextToken', nextToken)
                    response = client.get_members(
                        AccountIds=AccountIds,
                        NextToken=nextToken,
                    )

                iDebug(f'{callerid()}', pop_meta(response))

                # Consolidated Result
                for rs in response['Members']:
                    res.append(rs)

            except Exception as err:
                if not self.quite: iWarning(f'API call faied for GetMembers {self.region}', err)

            try:
                nextToken = response.get('UnprocessedAccounts')[0]['AccountId']
            except Exception as err:
                if not self.quite: iWarning(f'API call faied for {callerid()} nextToken {self.region}', err)

            if not nextToken:
                break

        return res

    def invite_members(self, AccountIds: list):
        """Invites accounts to become members of SecurityHub Master"""
        client = self.client

        res = {}
        response = {}
        try:
            response = client.invite_members(AccountIds=AccountIds)

            iDebug(f'{callerid()}', pop_meta(response))

            # Consolidated Result
            res = response.get('UnprocessedAccounts', [])

        except Exception as err:
            if not self.quite: iWarning(f'API call faied for {callerid()} / AccountIds {AccountIds} {self.region}', err)

        return res

    def list_invitations(self):
        client = self.client
        response = {}
        nextToken = None
        maxResults = 50

        res = []
        while True:
            try:
                if not nextToken:
                    response = client.list_invitations(
                        MaxResults=maxResults,
                    )
                else:
                    iDebug('nextToken', nextToken)
                    response = client.list_invitations(
                        NextToken=nextToken,
                        MaxResults=maxResults,
                    )

                iDebug(f'{callerid()}', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['Invitations']]

            except Exception as err:
                if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res

    def list_members(self, OnlyAssociated: bool = False):
        client = self.client
        response = {}
        nextToken = None
        maxResults = 50

        res = []
        while True:
            try:
                if not nextToken:
                    response = client.list_members(
                        OnlyAssociated=OnlyAssociated,
                        MaxResults=maxResults,
                    )
                else:
                    iDebug('nextToken', nextToken)
                    response = client.list_members(
                        OnlyAssociated=OnlyAssociated,
                        NextToken=nextToken,
                        MaxResults=maxResults,
                    )

                iDebug(f'{callerid()}', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['Members']]

            except Exception as err:
                if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res

    def list_organization_admin_accounts(self):
        client = self.client
        response = {}
        nextToken = None
        maxResults = 50

        res = []
        while True:
            try:
                if not nextToken:
                    response = client.list_organization_admin_accounts(
                        MaxResults=maxResults,
                    )
                else:
                    iDebug('nextToken', nextToken)
                    response = client.list_organization_admin_accounts(
                        NextToken=nextToken,
                        MaxResults=maxResults,
                    )

                iDebug(f'{callerid()}', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['AdminAccounts']]

            except Exception as err:
                if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res

    def list_security_control_definitions(self, StandardsArn: str | None = None):
        client = self.client
        response = {}
        nextToken = None
        maxResults = 50

        res = []
        while True:
            try:
                if not nextToken:
                    if StandardsArn:
                        response = client.list_security_control_definitions(
                            StandardsArn=StandardsArn,
                            MaxResults=maxResults,
                        )
                    else:
                        response = client.list_security_control_definitions(
                            MaxResults=maxResults,
                        )
                else:
                    iDebug('nextToken', nextToken)
                    if StandardsArn:
                        response = client.list_security_control_definitions(
                            StandardsArn=StandardsArn,
                            NextToken=nextToken,
                            MaxResults=maxResults,
                        )
                    else:
                        response = client.list_security_control_definitions(
                            NextToken=nextToken,
                            MaxResults=maxResults,
                        )

                iDebug(f'{callerid()}', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['SecurityControlDefinitions']]

            except Exception as err:
                if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res


class STS:

    def __init__(self, 
                 profile_name=None,
                 region_name=None,
                 account='', 
                 dont_quit=True, 
                 role='cs/p-support',
                 ) -> None:
        if account:
            sess = get_session(account, dont_quit=True, role=role)
        else:
            sess = boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()
        
        self.client = sess.client('sts') if not region_name else sess.client('sts', region_name=region_name)
        self.region = region_name

    def get_caller_identity(self):
        """Returns STS GetCallerIdentity dict"""
        client = self.client

        res = {}
        try:
            response = client.get_caller_identity()

            iDebug(f'{callerid()}', pop_meta(response))
            res = pop_meta(response)

        except Exception as err:
            iWarning(f'API call faied for {callerid()}', err)

        return res


class Organization:

    def __init__(self, profile_name=None, quite=False) -> None:
        sess = boto3.Session(profile_name=profile_name) if profile_name else boto3.Session()
        self.client = sess.client('organizations')
        self.quite = quite

    def describe_account(self, account_id):
        """Returns organizations:DescribeAccount dict"""
        client = self.client
        response = {}

        res = {}
        try:
            response = client.describe_account(AccountId=account_id)

            iDebug(f'{callerid()}', pop_meta(response))
            res = response.get('Account')

        except Exception as err:
            if not self.quite:
                iWarning(f'API call faied for {callerid()}', err)

        return res

    def describe_policy(self, policy_id):
        """Returns organizations:DescribePolicy dict"""
        client = self.client
        response = {}

        res = {}
        try:
            response = client.describe_policy(PolicyId=policy_id)

            iDebug(f'{callerid()}', pop_meta(response))
            '''Flatten data
            'Policy': {
                'PolicySummary': {
                    'Id': 'string',
                    'Arn': 'string',
                    'Name': 'string',
                    'Description': 'string',
                    'Type': 'SERVICE_CONTROL_POLICY'|'TAG_POLICY'|'BACKUP_POLICY'|'AISERVICES_OPT_OUT_POLICY',
                    'AwsManaged': True|False
                },
                'Content': 'string'
            }
            '''   
            data = response.get('Policy')
            if data.get('PolicySummary'):
                for key in data['PolicySummary'].keys():
                    res[key] = data['PolicySummary'][key]
            
            if data.get('Content'):
                res['Content'] = json.loads(data.get('Content'))

        except Exception as err:
            iWarning(f'API call faied for {callerid()}', err)

        return res

    def list_accounts(self):
        client = self.client
        response = {}
        nextToken = None

        res = []
        while True:
            try:
                if not nextToken:
                    response = client.list_accounts()
                else:
                    iDebug('nextToken', nextToken)
                    response = client.list_accounts(
                        NextToken=nextToken,
                    )

                iDebug(f'{callerid()}', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['Accounts']]

            except Exception as err:
                if not self.quite: iWarning(f'API call faied for {callerid()}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res

    def list_policies(self, filter='SERVICE_CONTROL_POLICY'):
        """Returns organizations:ListPolicies list

        Args:
            filter (str): One of 'SERVICE_CONTROL_POLICY'|'TAG_POLICY'|'BACKUP_POLICY'|'AISERVICES_OPT_OUT_POLICY'
        """
        client = self.client
        response = {}
        nextToken = None

        res = []
        maxResults = 50

        while True:
            try:
                if not nextToken:
                    response = client.list_policies(
                        Filter=filter,
                        # MaxResults=maxResults,
                    )
                else:
                    iDebug('nextToken', nextToken)
                    response = client.list_policies(
                        Filter=filter,
                        NextToken=nextToken,
                        # MaxResults=maxResults,
                    )

                iDebug(f'{callerid()}', pop_meta(response))

                # Consolidated Result
                [res.append(rs) for rs in response['Policies']]

            except Exception as err:
                if not self.quite: iWarning(f'API call faied for {callerid()} {self.region}', err)

            nextToken = response.get('NextToken')

            if not nextToken:
                break

        return res


if __name__ == '__main__':
    UNITTEST = True
    rName = cur_file().title()
    ppwide(f'Utilties Fucntions / {rName}')

    cur_colored = COLORED
    COLORED = True

    ppwide(f'Utilties Fucntions / {rName} / cur_dir()')
    ppjson(cur_dir())
    file = cur_dir()['File']

    ppwide(f'Utilties Fucntions / {rName} / AST')
    ast = AST(file)
    ast.print_info()
