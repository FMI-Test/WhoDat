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
    GET IAM Roles & Their Trust Relashionships for Given File
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

parser.add_argument('-i', '--input-file', required=True, help='File in json format')
parser.add_argument('-o', '--output-path', metavar='', default='/tmp/oneidm', help='Output Path')
parser.add_argument('-v', '--verbose',  action='store_true', help="Increase verbosity & show data file")
options = parser.parse_args()

INPUT_FILE = options.input_file
OUTPUT_FILE = INPUT_FILE.replcae('.csv', '.json')
data = get_csv(INPUT_FILE)

DATAFOLDER = os.environ.get('DATAFOLDER', options.output_path)
ENV = {
    'GR2': f"### GR2-0 / Convert CSV to JSON",
    'DATAFOLDER': DATAFOLDER,
    'Title': 'Convert CSV to JSON',
    'Task': 'Convert CSV to JSON' 
}

rWidth = 132

ppwide(ENV['GR2'], width=rWidth)

# Logs
print('Args:', iColor(vars(options), 'iYellow'))
print('File:', iColor(INPUT_FILE, 'iYellow'))


ts = get_ts()

# Process
put_json(OUTPUT_FILE, data)

took = took_ts_hms(ts)
print()
print('Took           :', iColor(took, 'iYellow'))
print('File     :', iColor(INPUT_FILE, 'iYellow'))
print('Output File    :', iColor(OUTPUT_FILE, 'iYellow'))
