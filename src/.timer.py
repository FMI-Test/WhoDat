#!/usr/bin/env python

import argparse
import concurrent.futures
import requests
import textwrap

from awsutil import *
from common import *
from util import *
from validateutil import *

FILE = '/tmp/timer'
recordSet = file_read_lines(FILE)

ts = get_ts()

data = []
for rs in recordSet:
    data.append({
        'Took': rs[0:12],
        'Total': 0,
        'Description': rs[17:]
    })

dm = DataModel()
dm.print_table(data)

print(f"Took: {took_ts_hms(ts)}")
