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

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''\
    Report Cache & Delete Expired Cache
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

parser.add_argument('-d', '--delete-expired', action='store_true', help='Delete Expired cache files')
parser.add_argument('-e', '--delete-empty', action='store_true', help='Delete Expired cache files')
parser.add_argument('-v', '--verbose',  action='store_true', help="Increase verbosity & show data file")
options = parser.parse_args()

ts = get_ts()

TITLE = f"### GR2 / Get Cache Objects"
ppwide(f"{TITLE}")

# Logs:
print('Args:', iColor(vars(options), 'iYellow'))

# Process
prefix= None
includes = []
excludes = []
emptyCache = []
emptyDelete = 0
activeCache = 0
expiredCache = 0

cKey = '__cache__'
cPath = os.environ.get('CACHE_PATH', cur_dir()['Path'] + '/__cache__')
myDir = cPath + '/*.json'
rss = get_dir(myDir)

res = []
deleteExpiredCount = 0
counterSub = 10
counterIndent = 8
counterLimit = 108
obJectPerLine = (counterLimit - counterIndent) * counterSub
myCounter = 8
ppwide(f"{TITLE} / . Represnts {counterSub:,} Objects, Full Line Represents {obJectPerLine:,} Objects")
for i, cFile in enumerate(rss['Files']):
    i += 1
    if i % counterSub == 0:
        myCounter = progress_print(counter=myCounter, indent=counterIndent, limit=counterLimit)

    # Get Cache Data
    cName = cFile[len(cKey):-5]  # -5 is len('.json')
    cFile = cache_file(cName)
    cData = get_json(cFile)


    # Backward Comptaibility
    if not cData.get('Type'): cData['Type'] = typeof(cData['Data'])
    if not cData.get('Size'): cData['Size'] = len(cData['Data'])

    cData['Created'] = cData['Created'][0:19]
    cData['Expired'] = True if get_ts() > float(cData['Expiration']) else False
    cData['Expiration'] = str(cache_ts2dt(cData['Expiration']))[0:19]

    # Empty Cache
    isEmpty = False if cData['Data'] else True
    if isEmpty:
        cData.pop('Data', None)
        if cData.get('Meta'):
            cData['Query'] = cData['Meta']['query']
        emptyCache.append(cData)
    
    if isEmpty and options.delete_empty:
        emptyDelete += 1
        delete_cache(cName)

    add = False
    if not prefix or (prefix and cFile.startswith(cKey + prefix)):
        add = True

    if add:
        for key in includes:
            if key in cFile:
                add = True

        for key in excludes:
            if key in cFile:
                add = False

    if add:
        # append only cache metadata plus calculated Expired
        if cData['Expired']:
            expiredCache += 1
        else:
            activeCache += 1
        
        # cData.pop('Query', None)
        cData.pop('Data', None)
        cData.pop('Meta', None)
        res.append(cData)
        if cData['Expired'] and options.delete_expired:
                deleteExpiredCount += 1
                delete_cache(cName)


# Print data
print()
printhh(f"{TITLE} / Cache Objects ")
dm = DataModel()
dm.print_table(res)

printhh(f"### GR2 / Empty Cache Object")
dm.print_table(emptyCache)

# Summary
took = took_ts_hms(ts)
cacheCount = len(res)
cacheCount = f'{cacheCount:,}'
activeCount = f"{activeCache:,}"
emptyCount = len(emptyCache)
emptyCount = f"{emptyCount:,}"
emptyDelCount = f"{emptyDelete:,}"
expiredCout = f"{expiredCache:,}"

cName = 'TEST'
set_cache(cName=cName, cData={'Test': 'TTL of 604800 or in a week'}, ttl=60480)
cData = get_cache(cName, fullData=True)
print()
ppwide(f"{TITLE}")
blue_green_dict_print( {
        'Args': vars(options),
        'Took': took,
        'Cache Objects': cacheCount,
        'Active Cache': activeCount,
        'Empty Cache': emptyCount,
        'Expired Cache': expiredCout,
        'Deleted Empty': emptyDelCount,
        'Deleted Expired': deleteExpiredCount,
        '': '',
        'Cache Created': cData['Created'],
        'Cache Expiration': cData['Expiration'],
        'Cache TTL': 60480,
    },
    ' : ', lcol='', rcol='iYellow'
    )
