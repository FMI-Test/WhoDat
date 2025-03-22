#!/usr/bin/env python

import argparse
import concurrent.futures
import requests
import textwrap

from awsutil import *
from common import *
from util import *
from validateutil import *

rWidth = 150
DL_LIST_FILE = '/tmp/oneidm/gege-all-dl-list.json'
printdoc('Copy Below Code to Bulk Process Above DL List to Extract Groups & Users Info', 
         width=rWidth,
         doc=textwrap.dedent('''\
         # Process Groups & Build User Cache Data
            time while read -r line; do whois "$line"; done < <(cat DL_LIST_FILE | jq -r . | tr -d '[],"' | awk '{print $1, $2}')
    
        # Process DL Groups & Users Data
            src/oneidm-groups-report.py --input-file DL_LIST_FILE

        '''),
        etl = {'DL_LIST_FILE': DL_LIST_FILE}
)

ts_now = get_ts()
ts_exp = 1712975267.237566


dt_now = get_dt().replace('T', ' ')
dt_exp = datetime.fromtimestamp(ts_exp).isoformat()

res ={
    'TS Now': ts_now,
    'TS Exp': ts_exp,
    'DT Now': dt_now,
    'DT Exp': dt_exp,
}

printhh("Cache Expiration")
blue_green_dict_print(res, sep=' : ' )

arr = [
    1234,
    1234.5,
    .9879,
    0.999,    
    '1234',
    '12345.098',
    '.9879',
    '0.999',
    'g1235374',
    'sdfghjk',
]

def is_number(q):
    try:
        float(q)
        return True
    except ValueError:
        return False

data = []
for q in arr:
    data.append({
        'Value': q,
        'Type': typeof(q),
        'isNumber': is_number(q),

    })

dm = DataModel()
dm.print_table(data)

# Yaml highlight
file = 'inputs/divest.tasks.yml'
data = get_yaml(file)

printhh("ppyamlc")
ppyamlc(data)

printhh("ppyamlc_file")
ppyamlc_file(file)