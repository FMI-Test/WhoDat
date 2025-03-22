#!/usr/bin/env python

import argparse
import concurrent.futures
import requests
import oracledb
import textwrap

from awsutil import *
from common import *
from util import *
from validateutil import *
from DataModels import *


rWidth = 150


'''
Host: p91-2-3-scan.corporate.ge.com
Port: 1621
ServiceName: oneidmp.corporate.ge.com
Database: IDM
'''
# Replace with your actual credentials
HOST = 'p91-2-3-scan.corporate.ge.com'
PORT = '1621'
SVCN = 'oneidmp.corporate.ge.com'
USER = os.environ.get('USER')
PASS = os.environ.get('PASS')

# hostname:port/servicename
dsn = f'{HOST}:{PORT}/{SVCN}'

iTrace(f'HOST: {HOST}')
iTrace(f'PORT: {PORT}')
iTrace(f'SVCN: {SVCN}')
iTrace(f'USER: {USER}')
iTrace(f'dsn: {dsn}')

VAL = Validator('OracleDB')

# Create a connection
conn = oracledb.connect(user=USER, password=PASS, dsn=dsn, disable_oob=True)
outcome = SUCCESS if conn else FAILURE
VAL.put(task='Connect to OracleDB', outcome=outcome, note='Connect to OracleDB')

iTrace(f'conn: {conn}')

# Create a cursor
cursor = conn.cursor()
outcome = SUCCESS if cursor else FAILURE
VAL.put(task='Create a cursor', outcome=outcome, note='Create a cursor')

# Execute a query
table = 'IDM.DW_GROUP_AVIATION_V'
query = f"SELECT * FROM {table}"
cQuery = f"SELECT COUNT(*) FROM {table}"

sumData = {
    'Table': table,
    'Query': query,
    'Count': cQuery,
}
print_color_dict(sumData)

# Fetch data
cursor.execute(query)
outcome = SUCCESS if cursor else FAILURE
VAL.put(task='Task 1', outcome=outcome, note=f'Execute : {query}')

cMap = []
# Access column metadata (including column names)
for key in cursor.description:
    cMap.append(key[0])
outcome = SUCCESS if cMap else FAILURE
VAL.put(task='Access column metadat', outcome=outcome, note=f'Get cursor.description')


tMap = {
    'GROUP_ID': 'GroupId', 
    'LDAP_HOST': 'LDAP', 
    'LDAP_OU': 'LDAP_OU', 
    'GROUP_NAME': 'GroupName', 
    'PRIMARY_MANAGER_SSO': 'PrimaryManager', 
    'ATTR_GECPASECURITYGROUP': 'SG', # Group SG 
    'ATTR_GECPAGROUPECSTATUS': 'Status', 
}

data = []
# Fetch and display results
for i, rec in enumerate(cursor):
    if i > 10:
        break

    # build recordset
    rs = {}
    for j, val in enumerate(rec): 
        key = cMap[j]
        if tMap.get(key):
            rs[tMap.get(key)] = val

    data.append(rs)
    iDebug(rs)
outcome = SUCCESS if data else FAILURE
VAL.put(task='Fetch data', outcome=outcome, note=f'{len(data)} Records')
    

dm = DataModel()
dm.print_table(data)

# Count Records
cursor.execute(cQuery)
recCount = cursor.fetchone()[0]
sumData['Records'] = f'{recCount:,}'
outcome = SUCCESS if recCount else FAILURE
VAL.put(task='Fetch data', outcome=outcome, note=f'{recCount} Records')

# Print Oucome
VAL.print_outcome()

# Print Summary
print_color_dict(sumData, sep=' : ', lcol='', rcol='iYellow')

print()
print(f"cMap: {iColor(cMap, 'iYellow')}")
print(f"tMap: {iColor(tMap, 'iYellow')}")

# Close Connection
cursor.close()
conn.close()
