#!/usr/bin/env python

import boto3
import oracledb
import requests
import urllib.parse

from common import *
from util import *
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

def callerid():
    """When called from a class returns class:ClassMethodName"""
    stack = inspect.stack()
    the_class = stack[1][0].f_locals["self"].__class__.__name__
    the_method = stack[1][0].f_code.co_name
    the_method = the_method.replace('_', ' ').title().replace(' ','')
    return f"{the_class.lower()}:{the_method}"

class DB():
    """Connect to Oracle Database
    
    Args:
        user (str): db username, required
        password (str): db password, required
        host (str): db host, default to 'p91-2-3-scan.corporate.ge.com'
        port (str): db port, default to '1621'
        svcn (str): db servicename, default to 'oneidmp.corporate.ge.com'
        db (str): db name, default to 'IDM'
    """

    def __init__(self, 
                 user: str, 
                 password: str='', 
                 host: str='p91-2-3-scan.corporate.ge.com',
                 port: str='1621',
                 svcn: str='oneidmp.corporate.ge.com',
                 db: str='IDM'
                 ) -> None:
        """Connect to Oracle Database
        
        Args:
            user (str): db username, required
            password (str): db password, required
            host (str): db host, default to 'p91-2-3-scan.corporate.ge.com'
            port (str): db port, default to '1621'
            svcn (str): db servicename, default to 'oneidmp.corporate.ge.com'
            db (str): db name, default to 'IDM'
        """
        
        # self.DB = db
        # self.GROUP = f'{db}.DW_GROUP_AVIATION_V'
        # self.GROUP_OWNER = f'{db}.DW_GROUP_OWNER_AVIATION_V'
        # self.GROUP_MANAGER = f'{db}.DW_GROUP_MANAGER_AVIATION_V'
        # self.GROUP_MEMBER = f'{db}.DW_GROUP_MEMBER_AVIATION_V'
        # self.IDENTITY = f'{db}.DW_IDENTITY_AVIATION_V'


        # Overwrite above with below
        self.DB = db
        self.GROUP = f'{db}.DW_IDM_GROUP'
        self.GROUP_OWNER = f'{db}.DW_IDM_GROUP_OWNER'
        self.GROUP_MANAGER = f'{db}.DW_IDM_GROUP_MANAGER'
        self.GROUP_MEMBER = f'{db}.DW_IDM_GROUP_MEMBER'
        self.USER = f'{db}.IDM_USER_VW'

        iTrace(f'self.DB            : {self.DB}')
        iTrace(f'self.GROUP         : {self.GROUP}')
        iTrace(f'self.GROUP_OWNER   : {self.GROUP_OWNER}')
        iTrace(f'self.GROUP_MANAGER : {self.GROUP_MANAGER}')
        iTrace(f'self.GROUP_MEMBER  : {self.GROUP_MEMBER}')
        iTrace(f'self.USER          : {self.USER}')

        # Connect to Oracle DB        
        # https://oracle.github.io/python-oracledb/
        # https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html
        dsn = f'{host}:{port}/{svcn}'
        self.conn = oracledb.connect(user=user, password=password, dsn=dsn, disable_oob=True)

        iTrace(f'dsn       : {dsn}')
        iTrace(f'self.conn : {self.conn}')

    def execute(self, query: str, count_query: str='', tr_map: dict={}) -> dict:
        """Execute a query and return the rows

        Args:
            query (str): SQL query to extract data, e.g. 'SELECT COUNT(*) FROM IDM.DW_GROUP'
            count_query (str): SQL query to get record counts. e.g. 'SELECT COUNT(*) FROM IDM.DW_GROUP'
            tr_map (dict): Translation dictionary to filter & rename columns, default return all columns

        Returns (dict): {'Data': [], 'Meta': {}}, Meta is Meta-Data such as Query, Count, Start, Took
        """
        iTrace(f'query       : {query}')
        iTrace(f'count_query : {count_query}')
        iTrace(f'tr_map      : {tr_map}')

        cursor = self.conn.cursor()

        iTrace(f'self.conn : {self.conn}')
        iTrace(f'cursor    : {cursor}')

        ts = get_ts()
        res = {
            'Data': [],
            'Meta': {
                'Query': query,
                'CountQuery': count_query,
                'Start': str(get_dt()),
                'Took': '',
                'Count': '',
            },
        }

        # Execute query
        cursor.execute(query)

        # Access column metadata (including column names)
        cMap = []
        for key in cursor.description:
            cMap.append(key[0])
        iTrace(f'cMap : {cMap}')

        # iTrace(f'rSet : {len(rSet)}')

        # Fetch and display results
        for i, rec in enumerate(cursor):
            # Build recordset
            rs = {}
            for j, val in enumerate(rec):
                # If translation map given then filter & rename columns 
                if tr_map:
                    key = cMap[j]
                    if tr_map.get(key):
                        rs[tr_map.get(key)] = val
                # If translation map not given then return all columns
                else:
                    rs[cMap[j]] = val

            res['Data'].append(rs)

        # Count Records
        if count_query:
            cursor.execute(count_query)
            recCount = cursor.fetchone()[0]
            res['Meta']['Count'] = f'{recCount:,}'

        res['Meta']['Took'] = took_ts(ts)
        
        return res

    def get_views(self):
        """Return available View for current Database"""
        query = f'''
        SELECT '{self.DB}' AS object_type, table_name 
        FROM all_tables 
            WHERE table_name LIKE 'DW%' OR table_name LIKE '{self.DB}%' 
        UNION ALL 
        SELECT 'View' AS object_type, view_name 
            FROM all_views 
            WHERE owner = '{self.DB}' 
        ORDER BY table_name 
        '''
        iDebug(f"Query : {query}")
        res = self.execute(query)

        return res

    def _count_query(self, query):
        """Return Count Query for counting query records"""
        needle = find_between(query, 'SELECT', 'FROM')
        count_query = query.replace(needle, ' COUNT(*) ')
        iDebug(f"Query : {query}")
        iDebug(f"Count Query : {count_query}")

        return count_query

    def _group_tr(self):
        """Filter & Translation for Groups"""
        return {
            'GROUP_ID': 'GroupId', 
            'LDAP_HOST': 'LDAP', 
            'LDAP_OU': 'LDAP_OU', 
            'GROUP_NAME': 'GroupName', 
            'PRIMARY_MANAGER_SSO': 'PrimaryManager', 
            'ATTR_GECPASECURITYGROUP': 'SG', # Group SG 
            'ATTR_GECPAGROUPECSTATUS': 'Status', 
        }
    
    def _owner_tr(self):
        """Filter & Translation for Groups"""
        return {
            'GROUP_ID': 'GroupId', 
            'OWNER': 'SSO', 
            'FIRST_NAME': 'FirstName', 
            'LAST_NAME': 'LastName', 
            'EMAIL_ADDRESS': 'Email', 
            # 'MANAGER_PERSON_NUM': 'ManagerSSO',
            'PERSON_STATUS': 'Status', 
        }

    def get_users(self, filter: str|list=''):
        """Returns (dict): {'Data': [], 'Meta': {}}, Meta is Meta-Data such as Query, Count, Start, Took
        
        Args:
            filter (str): Filter for either SSO, GU_EMAIL_DISP

        Filter Match:   
            filter (str=''): return all SOX DLs. 
            filter (str): return all DLs matching the string with '='. 
            filter (list): return all DLs matching the list with 'IN'. 

        Examples:
            filter = 'SSO' # Returns all DL for the SSO
            filter = '@GE ...' # Return DL info for the DL Name 
            filter = 'g12345678' # Return DL info for the DL ID
            filter = ['SSO1', 'SSO2, ...] # return DL for multiple SSO 
        """

        select = f"""
SELECT
    GU.PERSON_NUM_SSO AS GU_SSO, 
    GU.EMAIL_DISPLAY_NAME AS GU_EMAIL_DISP, 
    GU.FIRST_NAME AS GU_NAME, 
    GU.LAST_NAME AS GU_LAST, 
    GU.SSO_EXPIRATION_DATE AS GU_EXP,
    GU.MANAGER_PERSON_NUM AS GM_SSO,

    GM.EMAIL_DISPLAY_NAME AS GM_EMAIL_DISP,
    GM.SSO_EXPIRATION_DATE AS GM_EXP,
    GM.PERSON_STATUS AS GM_STATUS, 
    GM.BUSINESS_SEGMENT AS GM_BU_SEG, 

    GU.EMAIL_ADDRESS AS GU_EMAIL, 
    GU.PERSON_STATUS AS GU_STATUS, 
    GU.PERSON_TYPE AS GU_TYPE, 
    GU.COMPANYNAME AS GU_COMP, 
    GU.JOB_TITLE AS GU_TITLE, 
    GU.JOB_FUNCTION AS GU_FUNC, 
    GU.INDUSTRY_FOCUS_NAME AS GU_BU, 
    GU.BUSINESS_SEGMENT AS GU_BU_SEG, 
    GU.DEPARTMENT_NAME AS GU_DEP
FROM IDM.IDM_USER GU
JOIN IDM.IDM_USER GM ON GU.MANAGER_PERSON_NUM = GM.PERSON_NUM_SSO 
        """

        iDebug(f'{callerid()} / Filter :: :: {filter}')
        # Return all SSO or Name
        if not filter:
            where = f"GU.BUSINESS_SEGMENT IN ('Aviation Digital Technology', 'Aviation Corporate Holdings', 'GE Vernova rTSA')"
            query = f"""
{select}
WHERE {where}
ORDER BY GU.EMAIL_DISPLAY_NAME ASC
            """

        # Filter Multi-Value: PERSON_NUM_SSO, EMAIL_DISPLAY_NAME
        if filter and type(filter) == str:
            iDebug(f'{callerid()} / str')
            whereRs = [
                f"GU.PERSON_NUM_SSO = '{filter}'",
                f"lower(GU.EMAIL_DISPLAY_NAME) = '{filter.lower()}'",
                f"lower(GU.EMAIL_ADDRESS) = '{filter.lower()}'",
            ]
            where = ' OR '.join(whereRs)

            query = f"""
{select}
WHERE {where}
ORDER BY GU.EMAIL_DISPLAY_NAME ASC
            """

        # Filter Multi-Value: Email, SSO, Display Name, First & Last Name
        if filter and type(filter) == list:
            # To simplify join filter with ; and process it
            filter = ';'.join(filter)
            iDebug(f'{callerid()} / List')

            # EMAIL_ADDRESS
            if '@' in filter:
                needles = filter.lower().split(';')
                where = f"lower(GU.EMAIL_ADDRESS) IN {tuple(needles)}"
                iDebug(f'{callerid()} / Has @ / Filter :: {where}')

            # EMAIL_DISPLAY_NAME
            elif '(' in filter:
                needles = [x.replace(';', ',')+')' for x in filter.split(')') if x]
                where = f"GU.EMAIL_DISPLAY_NAME IN {tuple(needles)}"
                where = where.replace(",)", ")")
                iDebug(f'{callerid()} / Has ( / Filter :: {where}')

            # SSO - Fix Condition for non-sso entry
            elif ';' in filter and ' ' not in filter:
                needles = filter.split(';')
                where = f"GU.PERSON_NUM_SSO IN {tuple(needles)}"
                iDebug(f'{callerid()} / Has ; without Space / Filter :: {where}')

            # LAST_NAME, FIRST_NAME, EMAIL_DISPLAY_NAME
            elif ';' in filter and ' ' in filter:
                # split filter with ';' and strip leading & trailing spaces from needles
                needles = [x.strip() for x in filter.split(';')]
                where = f"(GU.FIRST_NAME IN {tuple(needles)} AND GU.LAST_NAME IN {tuple(needles)}) OR GU.EMAIL_DISPLAY_NAME IN {tuple(needles)}"
                iDebug(f'{callerid()} / Has ; without Space / Filter :: {where}')

            # LAST_NAME, FIRST_NAME[;...]
            elif '(' not in filter:
                # 'Mehta, Kapil;'                
                # 'Mehta, Kapil;Malave, Ben'
                iDebug(f'{callerid()} / Has No (')            
                needles = filter.lower().split(';')
                whereRs = []
                for needle in needles:
                    if ',' in needle:
                        # 'Mehta, Kapil'
                        needle = needle.replace(' ', '')
                        needle = needle.split(',')
                        if len(needle) == 0:
                            iWarning(f"{callerid()} / Skipping empty Needle!")
                        if len(needle) == 1:
                            whereRs.append(f"lower(GU.LAST_NAME) = '{needle[0]}'")
                        if len(needle) == 2:
                            whereRs.append(f"(lower(GU.LAST_NAME) = '{needle[0]}' AND lower(GU.FIRST_NAME) = '{needle[1]}')")
                        if len(needle) > 2:
                            iWarning(f"{callerid()} / Skipping '{len(needle)}' parts Needle instead of '2'!")

                where = ' OR '.join(whereRs)

            iDebug(f"needles {iColor(needles, 'iYellow')}")
            iDebug(f"WHERE {iColor(where, 'iYellow')}")
            query = f"""
{select} 
WHERE {where}
ORDER BY GU.EMAIL_DISPLAY_NAME ASC
        """

        iDebug('SQL:', iColor(query, 'Yellow'))
        count_query = self._count_query(query)
        res = self.execute(query, count_query)

        return res

    def get_groups(self, filter: str|list=''):
        """Returns (dict): {'Data': [], 'Meta': {}}, Meta is Meta-Data such as Query, Count, Start, Took
        
        Args:
            filter (str): Filter for either of GROUP_ID, GROUP_NAME, SSO

        Filter Match:   
            filter (str=''): return all SOX DLs. 
            filter (str): return all DLs matching the string with '='. 
            filter (list): return all DLs matching the list with 'IN'. 

        Examples:
            filter = 'SSO' # Returns all DL for the SSO
            filter = '@GE ...' # Return DL info for the DL Name 
            filter = 'g12345678' # Return DL info for the DL ID
            filter = ['SSO1', 'SSO2, ...] # return DL for multiple SSO 
        """
        table = self.GROUP

        # Escape filter
        if isinstance(filter, str):
            filter = filter.replace("'", "''")
        if isinstance(filter, list):
            filter = [f.replace("'", "''") for f in filter]

        # Return all SOX DL
        if not filter:
            query = f"""
SELECT 
    G.GROUP_ID, 
    G.LDAP_HOST, 
    G.LDAP_OU, 
    G.GROUP_NAME, 
    G.PRIMARY_MANAGER_SSO AS GM_SSO, 
    GM.EMAIL_DISPLAY_NAME AS GM_EMAIL_DISP, 
    GM.PERSON_STATUS AS GM_STATUS, 
    GM.PERSON_TYPE AS GM_TYPE, 
    GM.JOB_TITLE AS GM_TITLE, 
    GM.JOB_FUNCTION AS GM_FUNC, 
    GM.INDUSTRY_FOCUS_NAME AS GM_BU, 
    GM.BUSINESS_SEGMENT AS GM_BU_SEG, 
    GM.DEPARTMENT_NAME AS GM_DEP, 
    GM.SSO_EXPIRATION_DATE AS GM_SSO_EXP,
    CASE
        WHEN SUBSTR(M.MEMBER, 1, 3) = 'cn=' THEN REGEXP_SUBSTR(M.MEMBER, 'cn=([^,]+)', 1, 1, NULL, 1)
        ELSE M.MEMBER
    END AS GU_SSO,
    (GU.EMAIL_DISPLAY_NAME || '' || NG.GROUP_NAME) AS GU_EMAIL_DISP,     
    GU.PERSON_STATUS AS GU_STATUS, 
    GU.PERSON_TYPE AS GU_TYPE, 
    GU.JOB_TITLE AS GU_TITLE, 
    GU.JOB_FUNCTION AS GU_FUNC, 
    GU.INDUSTRY_FOCUS_NAME AS GU_BU, 
    GU.BUSINESS_SEGMENT AS GU_BU_SEG, 
    GU.DEPARTMENT_NAME AS GU_DEP,
    GU.SSO_EXPIRATION_DATE AS GU_SSO_EXP
FROM IDM.DW_IDM_GROUP G
JOIN IDM.IDM_USER GM ON G.PRIMARY_MANAGER_SSO = GM.PERSON_NUM_SSO 
JOIN IDM.DW_IDM_GROUP_MEMBER M ON G.GROUP_ID = M.GROUP_ID 
LEFT JOIN IDM.IDM_USER GU ON M.MEMBER = GU.PERSON_NUM_SSO 
LEFT JOIN IDM.DW_IDM_GROUP NG ON NG.GROUP_ID = REGEXP_SUBSTR(M.MEMBER, 'cn=([^,]+)', 1, 1, NULL, 1)
WHERE ( G.GROUP_NAME LIKE '@GE Cloud%' 
    -- Filter for Commercial & GovCloud DLs which ends to 12 Gits AWS Account ID 
    OR ( G.GROUP_NAME LIKE '@GE AWS_%' AND REGEXP_LIKE(G.GROUP_NAME, '[0-9]{12}$') ) 
    OR ( G.GROUP_NAME LIKE '@GE GOVAWS_%' AND REGEXP_LIKE(G.GROUP_NAME, '[0-9]{12}$') ) 
) AND ( G.GROUP_NAME LIKE '%141111311552' 
    OR G.GROUP_NAME LIKE '%188894168332' 
    OR G.GROUP_NAME LIKE '%207755114178' 
    OR G.GROUP_NAME LIKE '%264560008398' 
    OR G.GROUP_NAME LIKE '%277688789493' 
    OR G.GROUP_NAME LIKE '%376079469356' 
    OR G.GROUP_NAME LIKE '%432403552778' 
    OR G.GROUP_NAME LIKE '%504948279284' 
    OR G.GROUP_NAME LIKE '%556003251088' 
    OR G.GROUP_NAME LIKE '%589623221417' 
    OR G.GROUP_NAME LIKE '%736489861251' 
    OR G.GROUP_NAME LIKE '%737859062117' 
    OR G.GROUP_NAME LIKE '%020202940623' 
    OR G.GROUP_NAME LIKE '%147947222044' 
    OR G.GROUP_NAME LIKE '%330271845325' 
    OR G.GROUP_NAME LIKE '%610798319622' 
    OR G.GROUP_NAME LIKE '%715477192348' 
    OR G.GROUP_NAME LIKE '%896094434431' 
) 
ORDER BY G.GROUP_NAME ASC, G.GROUP_ID ASC 
"""

        if filter and type(filter) == str:
            order = 'G.GROUP_NAME ASC, G.GROUP_ID ASC, G.PRIMARY_MANAGER_SSO ASC, GU.EMAIL_DISPLAY_NAME ASC'
            if filter.startswith('g'):
                where = f"G.GROUP_ID = '{filter}' "
            elif filter.startswith('@'):
                where = f"G.GROUP_NAME = '{filter}' " 
            else:
                where = f"M.MEMBER = '{filter}' "

            query = f"""
SELECT 
    G.GROUP_ID, 
    G.LDAP_HOST, 
    G.LDAP_OU, 
    G.GROUP_NAME, 
    G.PRIMARY_MANAGER_SSO AS GM_SSO, 
    GM.EMAIL_DISPLAY_NAME AS GM_EMAIL_DISP, 
    GM.PERSON_STATUS AS GM_STATUS, 
    GM.PERSON_TYPE AS GM_TYPE, 
    GM.JOB_TITLE AS GM_TITLE, 
    GM.JOB_FUNCTION AS GM_FUNC, 
    GM.INDUSTRY_FOCUS_NAME AS GM_BU, 
    GM.BUSINESS_SEGMENT AS GM_BU_SEG, 
    GM.DEPARTMENT_NAME AS GM_DEP, 
    GM.SSO_EXPIRATION_DATE AS GM_SSO_EXP,
    CASE
        WHEN SUBSTR(M.MEMBER, 1, 3) = 'cn=' THEN REGEXP_SUBSTR(M.MEMBER, 'cn=([^,]+)', 1, 1, NULL, 1)
        ELSE M.MEMBER
    END AS GU_SSO,
    (GU.EMAIL_DISPLAY_NAME || '' || NG.GROUP_NAME) AS GU_EMAIL_DISP,     
    GU.PERSON_STATUS AS GU_STATUS, 
    GU.PERSON_TYPE AS GU_TYPE, 
    GU.JOB_TITLE AS GU_TITLE, 
    GU.JOB_FUNCTION AS GU_FUNC, 
    GU.INDUSTRY_FOCUS_NAME AS GU_BU, 
    GU.BUSINESS_SEGMENT AS GU_BU_SEG, 
    GU.DEPARTMENT_NAME AS GU_DEP,
    GU.SSO_EXPIRATION_DATE AS GU_SSO_EXP
FROM IDM.DW_IDM_GROUP G
JOIN IDM.IDM_USER GM ON G.PRIMARY_MANAGER_SSO = GM.PERSON_NUM_SSO 
JOIN IDM.DW_IDM_GROUP_MEMBER M ON G.GROUP_ID = M.GROUP_ID 
LEFT JOIN IDM.IDM_USER GU ON M.MEMBER = GU.PERSON_NUM_SSO 
LEFT JOIN IDM.DW_IDM_GROUP NG ON NG.GROUP_ID = REGEXP_SUBSTR(M.MEMBER, 'cn=([^,]+)', 1, 1, NULL, 1)
WHERE {where}  
ORDER BY {order}
"""

        # Filter Multi-Value: GROUP_ID, GROUP_NAME, SSO
        if filter and type(filter) == list:
            filter = str(tuple(filter)).replace('"', "'")
            query = f"""
SELECT 
    G.GROUP_ID, 
    G.LDAP_HOST, 
    G.LDAP_OU, 
    G.GROUP_NAME, 
    G.PRIMARY_MANAGER_SSO AS GM_SSO, 
    GM.EMAIL_DISPLAY_NAME AS GM_EMAIL_DISP, 
    GM.PERSON_STATUS AS GM_STATUS, 
    GM.PERSON_TYPE AS GM_TYPE, 
    GM.JOB_TITLE AS GM_TITLE, 
    GM.JOB_FUNCTION AS GM_FUNC, 
    GM.INDUSTRY_FOCUS_NAME AS GM_BU, 
    GM.BUSINESS_SEGMENT AS GM_BU_SEG, 
    GM.DEPARTMENT_NAME AS GM_DEP, 
    GM.SSO_EXPIRATION_DATE AS GM_SSO_EXP,
    CASE
        WHEN SUBSTR(M.MEMBER, 1, 3) = 'cn=' THEN REGEXP_SUBSTR(M.MEMBER, 'cn=([^,]+)', 1, 1, NULL, 1)
        ELSE M.MEMBER
    END AS GU_SSO,
    (GU.EMAIL_DISPLAY_NAME || '' || NG.GROUP_NAME) AS GU_EMAIL_DISP,     
    GU.PERSON_STATUS AS GU_STATUS, 
    GU.PERSON_TYPE AS GU_TYPE, 
    GU.JOB_TITLE AS GU_TITLE, 
    GU.JOB_FUNCTION AS GU_FUNC, 
    GU.INDUSTRY_FOCUS_NAME AS GU_BU, 
    GU.BUSINESS_SEGMENT AS GU_BU_SEG, 
    GU.DEPARTMENT_NAME AS GU_DEP,
    GU.SSO_EXPIRATION_DATE AS GU_SSO_EXP
FROM IDM.DW_IDM_GROUP G
JOIN IDM.IDM_USER GM ON G.PRIMARY_MANAGER_SSO = GM.PERSON_NUM_SSO 
JOIN IDM.DW_IDM_GROUP_MEMBER M ON G.GROUP_ID = M.GROUP_ID 
LEFT JOIN IDM.IDM_USER GU ON M.MEMBER = GU.PERSON_NUM_SSO 
LEFT JOIN IDM.DW_IDM_GROUP NG ON NG.GROUP_ID = REGEXP_SUBSTR(M.MEMBER, 'cn=([^,]+)', 1, 1, NULL, 1)
WHERE G.GROUP_ID IN {filter}
	OR G.GROUP_NAME IN {filter}
	OR M.MEMBER IN {filter}
ORDER BY G.GROUP_NAME ASC, G.GROUP_ID ASC, G.PRIMARY_MANAGER_SSO ASC, GU.EMAIL_DISPLAY_NAME ASC
"""
            
        iDebug('SQL:', iColor(query, 'Yellow'))
        count_query = self._count_query(query)
        tr_map = self._group_tr()
        res = self.execute(query, count_query)

        return res

    def get_groups_by_ids(self, ids: list):
        """Get Groups by GROUP_ID list

        Args:
            group_id (list): Group IDs, e.g. ['g01251725', 
            'g01277279', 
            'g01277393']
        Returns (dict): {'Data': [], 'Meta': {}}, Meta is Meta-Data such as Query, Count, Start, Took"""
        table = self.GROUP
        query = f"SELECT * FROM {table} WHERE GROUP_ID IN {tuple(ids)}"
        count_query = self._count_query(query)
        tr_map = self._group_tr()
        res = self.execute(query, count_query, tr_map)

        return res
        
    def get_groups_by_names(self, names: list):
        """Get a group by GROUP_NAME list

        Args:
            group_name (list): Group Names .e.g. ['group1', 
            'group2', 
            'group3']

        Returns (dict): {'Data': [], 'Meta': {}}, Meta is Meta-Data such as Query, Count, Start, Took"""
        table = self.GROUP
        query = f"SELECT * FROM {table} WHERE GROUP_NAME IN {tuple(names)}"
        count_query = self._count_query(query)
        tr_map = self._group_tr()
        res = self.execute(query, count_query, tr_map)

        return res

    def get_groups_owners(self):
        """Returns (dict): {'Data': [], 'Meta': {}}, Meta is Meta-Data such as Query, Count, Start, Took"""
        table = self.GROUP_OWNER
        query = f"SELECT * FROM {table} WHERE ROWNUM <= 50"
        count_query = self._count_query(query)
        tr_map = self._owner_tr()
        res = self.execute(query, count_query, tr_map)

        return res

    def get_groups_owners_by_ids(self, ids: list):
        """Returns (dict): {'Data': [], 'Meta': {}}, Meta is Meta-Data such as Query, Count, Start, Took
        
        Args:
            ids (list): can be any of SSO or Group ID or mix of both
        """
        table = self.GROUP_OWNER
        query = f"SELECT * FROM {table} WHERE OWNER IN {tuple(ids)} OR GROUP_ID IN {tuple(ids)}"
        count_query = self._count_query(query)
        tr_map = self._owner_tr()
        res = self.execute(query, count_query, tr_map)

        return res

    def get_table(self, table='', tr_map={}, limit: int=10):
        """Returns (dict): {'Data': [], 'Meta': {}}, Meta is Meta-Data such as Query, Count, Start, Took"""
        '''
        IDM.DW_GROUP_AVIATION_V
        IDM.DW_GROUP_MANAGER_AVIATION_V
        IDM.DW_GROUP_MEMBER_AVIATION_V
        IDM.DW_GROUP_OWNER_AVIATION_V
        IDM.DW_IDENTITY_AVIATION_V
        IDM.DW_JOB_TRANSFER_AVIATION_V
        IDM.IDM_USER_VW
        '''
        table = 'IDM.DW_GROUP_AVIATION_V'
        query = f"SELECT * FROM {table}"
        if limit and limit > 0:
            query += f" WHERE ROWNUM <= {limit}"
        count_query = self._count_query(query)
        res = self.execute(query, count_query)

        return res

class OneIDM():

    def __init__(self) -> None:
        self.model = {}

    @staticmethod
    def get_group_color_map():
        return  {
            # DB Format
            'GROUP_NAME': {
                '@GE GOVAWS': 'Orange',
            },
            'GM_STATUS': {
                'A': 'iGreen',
                'I': 'iRed',
            },
            'GU_SSO': {
                # Highlight Nested-Groups - it has 'g'
                'g': 'iYellow',
            },
            'GU_EMAIL_DISP': {
                # Highlight Nested-Groups - it has '@'
                '@': 'iYellow',
                'FUNCTIONAL': 'iYellow',
                'Functional': 'iBlue',
                'Service': 'iMagenta',
                'Shared': 'iMagenta',
                'None': 'iRed',
                '**': 'iRed',
            },
            'GU_EMAIL': {
                'None': 'iRed',
            },
            # User SSO Query
            'GU_STATUS': {
                'A': 'iGreen',
                'I': 'iRed',
            },
            'GU_TYPE': {
                'CONTRACTOR': 'iGreen',
                'EMPLOYEE': 'iBlue',
                'FUNCTIONAL': 'iMagenta',
                'GROUP': 'iYellow',
                'None': 'iYellow',
            },
            'GU_BU_SEG': {  
                'Aviation Digital Technology': 'iGreen',
                'Aviation Corporate Holdings': 'iGreen',
                'GE Vernova rTSA': 'iGreen',
            },
            # Data-Model Format
            'GroupAccountBU': {
                'Corporate CoreTech': 'iBlue',
                'Corporate Cyber': 'Green',
            },
            'UserBUSegment': {
                'Aviation Digital Technology': 'iGreen',
                'Aviation Corporate Holdings': 'iGreen',
                'GE Vernova rTSA': 'iGreen',
            },
            'GM_EMAIL_DISP': {
                'None': 'iRed',
            }
        }

    @staticmethod
    def get_user_color_map():
        return {
            # DB Format
            'PERSON_STATUS': {
                'A': 'iGreen',
                'I': 'iYellow',
            },
            'BUSINESS_SEGMENT': {
                'Aviation Digital Technology': 'iGreen',
                'Aviation Corporate Holdings': 'iGreen',
                'GE Vernova rTSA': 'iGreen',
            },
            # Data-Model Format
            'GU_EMAIL_DISP': {
                # Highlight Nested-Groups - it has '@'
                '@': 'iYellow',
                'Service': 'iYellow',
                'Shared': 'iYellow',
                'None': 'iRed',
            },
            'GU_EMAIL': {
                'None': 'iRed',
            },
            # User SSO Query
            'GU_STATUS': {
                'A': 'iGreen',
                'I': 'iRed',
            },
            'GU_TYPE': {
                'CONTRACTOR': 'iGreen',
                'EMPLOYEE': 'iBlue',
                'FUNCTIONAL': 'iYellow',
                'None': 'iRed',
            },
            'GU_BU_SEG': {  
                'Aviation Digital Technology': 'iGreen',
                'Aviation Corporate Holdings': 'iGreen',
                'GE Vernova rTSA': 'iGreen',
            },
            'Status': {
                'A': 'iGreen',
                'I': 'iYellow',
            },
            'BU Segment': {
                'Aviation Digital Technology': 'iGreen',
                'Aviation Corporate Holdings': 'iGreen',
                'GE Vernova rTSA': 'iGreen',
            }
        }


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


