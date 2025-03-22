#!/usr/bin/env python

import argparse
import concurrent.futures
import requests
import textwrap

from awsutil import *
from common import *
from util import *
from validateutil import *

ts = get_ts()

# Process
prefix= None
includes = []
excludes = []

cKey = '__cache__'
cPath = os.environ.get('CACHE_PATH', cur_dir()['Path'] + '/__cache__')
myDir = cPath + '/*.json'
rss = get_dir(myDir)

res = []
counterSub = 10
counterIndent = 8
counterLimit = 108
obJectPerLine = (counterLimit - counterIndent) * counterSub
myCounter = 8
ppwide(f'### GR2 / Get Cache Objects / . Represnt {counterSub:,} Objects, Full Line Represents {obJectPerLine:,} Objects')
for i, cFile in enumerate(rss['Files']):
    i += 1
    if i % counterSub == 0:
        myCounter = progress_print(counter=myCounter, indent=counterIndent, limit=counterLimit)

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
        cName = cFile[len(cKey):-5]  # -5 is len('.json')
        cFile = cache_file(cName)
        cData = get_json(cFile)
        cData['Expired'] = True if get_ts() > float(cData['Expiration']) else False
        cData.pop('Data', None)
        res.append(cData)

# Summary
took = took_ts_hms(ts)
cacheCount = len(res)
cacheCount = f'{cacheCount:,}'
print()
print('Cache Objects  :', iColor(cacheCount, 'iYellow'))
print('Took           :', iColor(took, 'iYellow'))

sts = STS(profile_name='GECC')

ppjson(sts.get_caller_identity())