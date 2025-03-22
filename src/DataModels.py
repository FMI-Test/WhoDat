#!/usr/bin/env python

import boto3
import requests
import urllib.parse

from common import *
from util import *
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer


class ApiCall():

    def __init__(self, NAAPI_KEY=None, HRUS_KEY=None, CMC_KEY=None) -> None:
        self.NAAPI_KEY = NAAPI_KEY
        self.HRUS_KEY = HRUS_KEY
        self.CMC_KEY = CMC_KEY

    def _sso_dm(self, brief=False):
        if brief:
            return {
                'Status': 'gessostatus',
                'SSO': 'uid',
                'Name': 'cn',
                'eMail': 'mail',
                'Type': 'employeeType',
                'Title': 'title',
                'Func.': 'gessojobfunction',
                'Role': 'gehrbusinesssegment',
            } 
    
        return {
            'Status': 'gessostatus',
            'SSO': 'uid',
            'Name': 'cn',
            'eMail': 'mail',
            'Mobile': 'mobile',
            'Start': 'gessoeffectivestartdate',
            'End': 'gessoeffectiveenddate',
            'Type': 'employeeType',
            'Title': 'title',
            'Comp.': 'gessocompanyname',
            'Func.': 'gessojobfunction',
            'Role': 'gehrbusinesssegment',
        }


    def _sso_print(self, data, brief=False):
        '''Print sso data extracted from api call 
        '''
        sMap = self._sso_dm() if not brief else self._sso_dm(brief=brief)

        iSpace = 5
        cWidth = 31

        ppwide('Employee Data from HR_US')

        res = []
        for i, rec in enumerate(data):
            iTrace(rec)
            i += 1
            rs = {}
            sColor = tColor = 'Gray'
            for key in sMap.keys():
                rKey = sMap[key]
                rs[key] = rec.get(rKey)
                
            sColor = 'Green' if rs.get('Status') == 'A' else 'Red'
            tColor = 'Yellow' if rs.get('Contractor') == '' else 'Blue'

            res.append(rs)

            if not brief:
                print(
                    lspace(f'{i}.', iSpace),
                    'Status:', iColor(rspace(rs['Status'], cWidth), sColor),
                    'Type  :', iColor(rs['Type'], tColor),
                )
                print(
                    lspace('', iSpace),
                    'Name  :', rspace(rs['Name'], cWidth),
                    'Comp. :',rs['Comp.'],
                )
                print(
                    lspace('', iSpace),
                    'eMail :', rspace(rs['eMail'], cWidth),
                    'Func. :', rs['Func.'],
                )
                print(
                    lspace('', iSpace),
                    'Mobile:', rspace(rs['Mobile'], cWidth),
                    'Role  :', rs['Role'],
                )
                print(
                    lspace('', iSpace),
                    'Start :', rspace(rs['Start'], cWidth),
                    'End   :', rs['End'],
                )

        if brief:
            dm = DataModel()
            dm.print_table(res)
            

    def get_sso_data(self, query, echo=False, brief=False):
        '''Return json reponse of API call to HR US
        
        Args:
            query (str): SSO or email address
            
        Returns json object
        '''
        url = 'https://hr-us.gecloud.io/'
        
        if isInt(query):
            query = f'user?sso={query}'

        if '@' in str(query):
            query = f'user?email={query}'

        iTrace('get_sso_data query:', query)

        res = self._api_call(url, self.HRUS_KEY, query)

        if echo and 'data'in res and isinstance(res['data'], list): 
            self._sso_print(res['data'], brief=brief)

        return res


    def get_idm_data(self, query):
        '''Return json reponse of API call to HR US
        
        Args:
            query (str): SSO or email address
            
        Returns json object
        '''
        url = 'https://hr-us.gecloud.io/'
        
        if isInt(query):
            query = f'idm?sso={query}'

        if '@' == str(query).startswith('@'):
            query = f'idm?email={query}'

        if str(query).startswith('g') and isInt(str(query)[1:]):
            query = f'idm?groupId={query}'

        return self._api_call(url, self.HRUS_KEY, query)


    def _api_call(self, url, api_key, query=None, ssl=True):
        url += '/' if url[-1] != '/' else ''
        host = find_between(url, '://', '/')
        verify = True if not ssl else False
        url = f'{url}{query}'
        
        iTrace(f"API Call to '{url}")

        headers = {
            'Connection': 'keep-alive', 
            'x-api-key': api_key,
            'Accept-Encoding': 'gzip, deflate', 
            'cache-control': 'no-cache', 
            'Content-Type': 'application/json',
            'host': host,
            'Accept': '*/*'
        }

        res = {}
        data = requests.request("GET", url, headers=headers, verify=ssl)
        res['statusCode'] = data.status_code
        data = data.json()
        if isinstance(data, dict): data = [data]

        res['data'] = data
        if isTrace(): ppjson(res)

        return res


class DataModel():

    def __init__(self) -> None:
        self.model = {}

    def get_model(self, data:list) -> dict:
        """Returns dict of {key: max_len(key_values), ...}"""
        # Singleton - Returns CSV like Data Model whith all fields 
        if len(self.model) > 0: return self.model

        res = {}
        for rs in data:
            for key in rs.keys():
                val_len = len(str(rs[key]))
                if key not in res:
                    res[key] = len(key)
                
                if val_len > res[key]:
                    res[key] = val_len
        
        self.model = res

        return res

    def dynamo_marshaller(self, data):
        """Returns json object of dynamo call of res['Items]"""
        d = TypeDeserializer()
        return {k: d.deserialize(value=v) for k, v in data.items()}

    def get_default_color_set(self):
        return {
            'Status': {
                # TEA Staus
                'Request': 'Yellow',
                'Active': 'Yellow',
                'Expired': 'Gray',
                'Grant': 'Green',
                'Deny': 'Red',
                'Revoke': 'Gray',

                # SSO Status
                'A': 'Green',
                'I': 'Red',

                # CMC Status
                'Active': 'Yellow',
                'Building': 'Yellow',
                'Decommissioning': 'Red',
                'Ejected': 'Red',
            },
            # TMP
            'Outcome': {
                'FAILED': 'Red',
                'PASSED': 'Green',
                'SKIPPED': 'Yellow',
            }
        }

    def get_table_width(self, data:list, space:int=2) -> int:
        dm = self.get_model(data)
        row_width = 5
        cols_width = row_width + space
        for key in dm.keys():
            cols_width += dm[key] + space
        cols_width -= space

        return cols_width

    def print_table(self, 
                    data: list, 
                    colors_map: dict | None= None, 
                    space: int=2,
                    hline: bool=False,
                    limit: int=0,
                    ) -> None:
        """Prints tabular output of data with auto width
        
        Args:
            data (list): list of dict data to render the tabular output
            color_set (dict or None): if not given will load default color set, {} to skip color
            space (int): space between columns
            hline (bool): print horizontal line between rows, default False

        color_set example for CMC data:
        {
            'Status': {
                # CMC Status
                'Active': 'Yellow',
                'Building': 'Yellow',
                'Decommissioning': 'Red',
                'Ejected': 'Red',
            }
        }

        """
        UTC_NOW = datetime.now(timezone.utc).isoformat(timespec= 'seconds')[0:19] # remove +00:00
        LOC_NOW = datetime.now().isoformat(timespec= 'seconds')[0:19] # remove +00:00

        colors = colors_map if colors_map else self.get_default_color_set()
        iDebug('colors:', colors)

        dm = self.get_model(data)
        spc = ' ' * space

        row_width = 5
        cols_width = row_width + space

        # Skip if no data given
        if not data:
            print('Local:', LOC_NOW, 'UTC:', UTC_NOW)
            return
        
        # Calculate Column Max Lenght
        print('Row'.rjust(row_width) + spc, end = '')
        for key in dm.keys():
            cols_width += dm[key] + space
            # Print Header
            print(rspace(key, dm[key]) + spc, end = '')
        cols_width -= space
        print()
        wline('-', cols_width)

        # Process and Print Row Data
        for i, rs in enumerate(data):
            if limit > 0 and i >= limit: break
            # Handle multi-line in multi-rows
            firstKey = list(dm.keys())[0]
            # Print counter :: Multi-line rows has first column data for the first line
            if rs.get(firstKey):
                i += 1
                # Print horizontal-line if row is not the first row and print horizontal-line is True
                if hline and i > 1:
                    wline('-', cols_width)
                print(str(i).rjust(row_width - 1) + '.' + spc, end = '') # - 1 for .
            # Do not Print counter :: Multi-line rows has empty first column data for the second line onward
            else:
                print(''.rjust(row_width) + spc, end = '')

            # Iterate through columns
            for key in dm.keys():
                obj = rs.get(key, '')
                print_obj = rspace(rs.get(key, ''), dm[key])

                # Add color if color-map given for the column
                iMap = colors.get(key, {})
                if isinstance(colors, dict) and isinstance(iMap, dict):
                    for cKey in iMap.keys():
                        if cKey in print_obj:
                            print_obj = iColor(print_obj, iMap[cKey]) 

                print(str(print_obj) + spc, end = '')
            print()
            
        wline('-', cols_width)

        # Print Header in the footer for large table
        if i > 50:
            print('Row'.rjust(row_width) + spc, end = '')
            for key in dm.keys():
                print(rspace(key, dm[key]) + spc, end = '')
            print()
            wline('-', cols_width)

        showLimit = f'(showing {limit:,} of {len(data):,} records)' if (limit > 0 and limit < len(data) )else ''
        print(
            iColor(f"Local: {LOC_NOW}", 'iBlue'),
            iColor(f"UTC: {UTC_NOW}", 'iGreen'),
            iColor(showLimit, 'iYellow'),
        )
        

class AccessReview():

    def __init__(self) -> None:
        self.ACTIONS = ['Request', 'Grant', 'Deny', 'Revoke']

        self.DATA = {
            'Events': [],
            'Count': 0
        }

        self.TIMES = []
        for i in range(8, 17, 2):
            self.TIMES.append(f'{ndigits(i, 2)}:00:00')

    def make_data(self):
        """Returns a generated DATA['Events']"""
        for m in range(9, 13): # month
            for d in range(1,30, 5): # day
                for i in range (0, 2): # request per day
                    acc = ''
                    a = rand(1, 10)
                    while len(acc) < 12: acc += f'{a}'
                    sso = '00'
                    while len(sso) < 5: sso += f'{rand(1,4)}'
                    ssp = '000'
                    while len(ssp) < 5: ssp += f'{rand(1, 4)}'

                    date0 = f'2023-{ndigits(m, 2)}-{ndigits(d, 2)}'
                    date1 = f'2023-{ndigits(m, 2)}-{ndigits(d + 1, 2)}'

                    time0 = self.TIMES[rand(0, len(self.TIMES))]
                    time = int(time0[0:2])
                    time1 = f'{ndigits(time + 1 , 2)}:00:00'

                    dt0 = f'{date0} {time0}' # today now
                    dt1 = f'{date0} {time1}' # today + 1h
                    dt2 = f'{date1} {time1}' # tomorrow + 1h

                    action = self.ACTIONS[rand(0, len(self.ACTIONS))]

                    if action == 'Request':
                        self.DATA['Events'].append({
                            'Date': dt0,
                            'Account': acc,
                            'SSO': sso,
                        })

                    if action == 'Deny':
                        self.DATA['Events'].append({
                            'Date': dt0,
                            'Account': acc,
                            'SSO': sso,
                            'SSP': ssp,
                            'Access': action,
                            'AccessDate': dt1,
                        })

                    if action == 'Grant':
                        self.DATA['Events'].append({
                            'Date': dt0,
                            'Account': acc,
                            'SSO': sso,
                            'SSP': ssp,
                            'Access': action,
                            'AccessDate': dt1,
                        })

                    if action == 'Revoke':
                        self.DATA['Events'].append({
                            'Date': dt0,
                            'Account': acc,
                            'SSO': sso,
                            'SSP': ssp,
                            'Access': 'Grant',
                            'AccessDate': dt1,
                            'Revoke': 'Lambda',
                            'RevokeDate': dt2,
                        })

                    self.DATA['Count'] += 1

        return self.DATA
    
    def summary(self, data:list=[]):
        """Returns summary of actions counts from data"""

        res = {
            'Request': len(data),
            'Active': 0,
            'Expired': 0,
            'Grant': 0,
            'Deny': 0,
            'Revoke': 0,
        }

        access_types = []
        for rs in data:
            if 'SSP' not in rs: res['Expired'] +=1
            
            access = rs.get('Status', '')
            if access not in access_types: access_types.append(access)

            res['Grant']  += 1 if access in ['Grant', 'Revoke'] else 0
            res['Deny']   += 1 if access == 'Deny' else 0
            res['Revoke'] += 1 if access == 'Revoke' else 0
            res['Active'] += 1 if access == 'Grant' else 0

        if isDebug():
            print('Reported Summary')
            ppjson(res)
            ppjson(access_types)
            print()

        return res

    def summerize(self, data:list=[], width=90, no_print = False) -> dict:
        """Returns Summerized Account, SSO, SSP"""

        res = {
            'Account': {'Count':0, 'Items': []},
            'SSO': {'Count':0, 'Items': []},
            'SSP': {'Count':0, 'Items': []},
        }

        # Genrate unique items per key
        for rs in data:
            for key in res.keys():
                if rs.get(key) is not None and rs.get(key) not in res[key]['Items']: 
                    res[key]['Items'].append(rs[key])

        # Count len items per key
        if no_print is False:
            print()
            print('Summerized Unique Values')
            wline('-', width)

        col_width = maxLen(res.keys())
        for key in res.keys():
            res[key]['Count'] = len(res[key]['Items'])
            items = res[key]['Items']
            res[key]['Items'] = sorted(items)

            if no_print is False:
                print(iColor(key.ljust(col_width), 'Blue'), ':', res[key])
        
        return res

    def validate(self, data:list=[], width=90, no_print = False) -> list:
        """Returns error array & print validation if no_print is True"""
        err = []
        pass_color = 'Green'
        fail_color = 'Red'
        
        # Report
        rs = self.summary(data)
        iDebug(iColor('Report:', 'Blue'), rs)

        # Assert
        rss = {
            'Request': rs['Expired'] + rs['Grant'] + rs['Deny'],
            'Active': rs['Grant'] - rs['Revoke'],
            'Expired': rs['Request'] - rs['Grant'] - rs['Deny'],
            'Grant': rs['Request'] - rs['Expired'] - rs['Deny'],
            'Deny': rs['Request'] - rs['Expired'] - rs['Grant'],
            'Revoke': rs['Grant'] - rs['Active']
        }
        iDebug(iColor('Assert:', 'Blue'), rss)

        for key in rs.keys():
            if rs[key] != rss[key]: err.append({key: {'Asserted': rss[key], 'Reported': rs[key]}})

        if no_print is False:
            col_width = 10
            # Header
            print('Validation'.ljust(20), end = '')
            for key in rs.keys(): print(iColor(key.rjust(col_width), 'Blue' if rs[key] == rss[key] else 'Red'), end = '') 
            print()
            wline('-', width)

            # Report
            print(iColor('Report'.ljust(20), pass_color if len(err) == 0 else fail_color), end = '')
            for key in rs.keys(): print(iColor(str(f'{rs[key]:,}').rjust(col_width), 'Blue' if rs[key] == rss[key] else 'Red'), end = '') 
            print()

            # Assert
            print(iColor('Assert'.ljust(20), 'Blue'), end = '')
            for key in rs.keys(): print(iColor(str(f'{rss[key]:,}').rjust(col_width), 'Blue'), end = '') 
            print()

            wline('-', width)

        return err
    
    def formulas(self, width=90):
        """Prints validation formulas"""
        print()
        print('Validation Fourmulas')
        wline('-', width)
        # Request + Expired + Grant + Deny + Revoke
        data = {
            'Request': 'Expired + Grant + Deny',
            'Active': 'Grant - Revoke',
            'Expired': 'Request - Grant - Deny',
            'Grant': 'Request - Expired - Deny',
            'Deny': 'Request - Expired - Grant',
            'Revoke': 'Grant - Active',
        }
        blue_green_dict_print(data, ' = ')

    def lifecycle(self, width=90):
        """Returns request lifecycle"""
        print()
        print('Request Lifecycle')
        wline('-', width)
        print(
            iColor('Request', 'Blue'), '>',
            iColor('Expired', 'Red'), '>',
            iColor('Done', 'Green'),
        )
        print(
            iColor('Request', 'Blue'), '>',
            iColor('Deny', 'Red'), '>',
            iColor('Done', 'Green'),
        )
        print(
            iColor('Request', 'Blue'), '>',
            iColor('Grant', 'Green'), '>',
            iColor('Extende', 'iGray'), '>', 
            iColor('Revoke', 'Red'), '>',
            iColor('Done', 'Green'),
        )


class DataFilter():

    def __init__(self) -> None:
        self.filters = {}

    def filter_dict_by_date(self, data:dict, query:str) -> bool:
        """Returns True (exclude - out of range) or False (include - in range)

        Params:
            data (dict): dictionary
            query (str): key=form[,to]
                key (str): date key in dictionary
                from (str): starting date filter. ex: 2023-10-10
                to (str): ending date filter (optional). ex: 2023-10-21

        Returns True or False
        """
        res = self.filter_list_by_date([data], query=query)
        return True if len(res) == 0 else False
    
    def filter_dict_by_query(self, data:dict, query:str) -> bool:
        """Returns True (exclude - out of range) or False (include - in range)
        
        Params:
            data(list): list of dictionaries. ex: [{}, {}, ...]
            query (Str): value[,value2[...]]

        Returns True or False    
        """
        res = self.filter_list_by_query([data], query=query)
        return True if len(res) == 0 else False
    
    def filter_list_by_date(self, data:list, query:str) -> list:
        """Returns filtered result
        
        Params:
            data (list): list of dictionaries. ex [{}, {}, ...]
            query (str): key=form[,to]
                key (str): date key in dictionary
                from (str): starting date filter. ex: 2023-10-10
                to (str): ending date filter (optional). ex: 2023-10-21

        Returns list
        """
        res = []
        date_filter = {}
        try:
            try:
                assert '=' in query
            except AssertionError:
                iWarning("Invalid date query format, of 'key=from[,to]', given:", query)
                return res
            
            date_ele = query.replace('=', ',').split(',')
            date_filter['key'] = date_ele[0]
            date_filter['from'] = date_ele[1]
            date_filter['to'] = date_ele[2] if len(date_ele) > 2 else None
            self.filters['Date'] = date_filter
        except Exception as err:
            iWarning("Invalid date query format, instead of 'key=from[,to]', given:", query)
            return res
        
        for rs in data:
            include = False
            # Date Filter
            key = date_filter['key']
            if key in rs and rs[key] >= date_filter['from']:
                if date_filter['to'] is None:
                    iTrace('From', rs)
                    include = True
                if date_filter['to'] is not None and rs[key] <= date_filter['to']:
                    iTrace('From to', rs)
                    include = True
            
            if include is True: res.append(rs)

        return res
    
    def filter_list_by_query(self, data:list, query:str) -> list:
        """Returns filtered result
        
        Params:
            data(list): list of dictionaries. ex: [{}, {}, ...]
            query (Str): val1[,val2[...]][OR=val1,val2[...]][NOR=val1[,val2[...]]]

        Returns list
        """
        res = []

        nor_key = 'NOR='
        nor_queries = None if nor_key not in query else query.split(nor_key)[1].split(',')
        if nor_queries is not None: 
            query = query.split(nor_key)[0]
            self.filters['norQueries'] = nor_queries
        
        or_key = 'OR='
        or_queries = None if or_key not in query else query.split(or_key)[1].split(',')
        if or_queries is not None: 
            query = query.split(or_key)[0]
            self.filters['orQueries'] = or_queries

        queries = query.split(',')
        self.filters['Query'] = queries
        for rs in data:
            include = False

            # Process ANDs
            q_sum = 0
            if queries != '':
                for q in queries:
                    if q in str(rs): q_sum += 1
                if q_sum == len(queries): include = True

            # Include ORs
            if or_queries is not None and self.mix_has_needle(rs, or_queries): include = True

            # Exclude NORs
            if nor_queries is not None and self.mix_has_needle(rs, nor_queries): include = False

            # Enforce ANDs
            if queries != '' and q_sum != len(queries): include = False

            if include is True: res.append(rs)

        return res

    def get_filters(self) -> dict:
        """Returns dictionary of filters"""
        return self.filters

    def mix_has_needle(self, mix, needle:list) -> bool:
        """Returns True or False if at least one ele in needle's list is in mix input (Logical or)"""
        return len([ele for ele in needle if(ele in str(mix))]) > 0

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
