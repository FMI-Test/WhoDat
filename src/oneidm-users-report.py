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
        export HRUS_KEY=$( cat ./.HRYS_KEY )

    GitHub: https://github.build.ge.com/GR2-0/Transitional-Master-Payer-Migration
    ''')
)

parser.add_argument('-i', '--input-file', default='/tmp/oneidm/uid.json', help='Input File is a json file of groups.')
parser.add_argument('-v', '--verbose',  action='store_true', help="Increase verbosity & show data file")
options = parser.parse_args()
 
INPUT_FILE = options.input_file

DATAFOLDER = os.environ.get('DATAFOLDER', '/tmp/oneidm')
INPUT = os.environ.get('INPUT', 'tst')

DLS_FILE = f"{DATAFOLDER}/{INPUT}-dl-list.json"
GRP_FILE = f"{DATAFOLDER}/{INPUT}-gid-data.json"
UID_FILE = f"{DATAFOLDER}/{INPUT}-uid-data.json"

dt = get_dt_local()[0:10]
OUTPUT_FILE = f'/tmp/oneidm/{INPUT}-Users-Report.csv'

ENV = {
    'GR2': f"### GR2-0 / OneIDM Extract Employee From Processed JSON File",
    'DATAFOLDER': DATAFOLDER,
    'Title': 'OneIDM Extract API',
    'Task': 'OneIDM Extract API' 
}
rWidth = 132

print(ENV['GR2'])

# Logs
print('Args:', iColor(vars(options), 'iYellow'))

uMap = {
    'SSO': 'uid',
    'Status': 'gessostatus',
    'Type': 'employeeType',
    'Full Name': 'cn',
    'End Date': 'gessoeffectiveenddate',
    'Department': 'gessodepartment',
    'BU Segment': 'gehrbusinesssegment',
}

ts = get_ts()
dm = DataModel()
res = get_json(INPUT_FILE)

data = []
data2 = []
inactive_data = []
for key in res.keys():
    rs = res[key]
    
    # Group or null data
    if not rs.get('uid'):
        continue

    data.append({
        'SSO': rs.get('uid'),
        'Status': rs.get('gessostatus'),
        'Type': rs.get('employeeType'),
        'Full Name': rs.get('cn'),
        'End Date': rs.get('gessoeffectiveenddate'),
        'BU Segment': rs.get('gehrbusinesssegment', ''),
    })

    if rs.get('gessostatus') != 'A':
        inactive_data.append({
            'SSO': rs.get('uid'),
            'Status': rs.get('gessostatus'),
            'Type': rs.get('employeeType'),
            'Full Name': rs.get('cn'),
            'End Date': rs.get('gessoeffectiveenddate'),
            'BU Segment': rs.get('gehrbusinesssegment', ''),
        })


    if not rs.get('gehrbusinesssegment'):
        rs.pop('meta', None)
        data2.append(rs)

# Print Data
print()
cMap = OneIDM.get_user_color_map()
dm.print_table(data,colors_map=cMap)

# Print Not Active Users
print()
dm.print_table(inactive_data)

put_csv(OUTPUT_FILE, data)
put_json(OUTPUT_FILE.replace('.csv', '.json'), data2)

data_sum = {
    'Took': took_ts_hms(ts),
    'Input Data': INPUT_FILE,
    'Output CSV': OUTPUT_FILE,
    'Users Count': f"{len(res):,}",
    'Not Active Users Count': f"{len(inactive_data):,}",
}

print()
blue_green_dict_print(data_sum, sep=' : ', lcol='', rcol='iYellow')
