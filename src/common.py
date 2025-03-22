#!/usr/bin/env python

'''
Some common functions which only clutter the main code, so moving them here to a separate file
 ## History:
  # 17-Feb-2024: Protect immutable constants, whitelist mutable gloabl config vars 
  # 21-Jan-2024: Add Line# to Logs
  # 25-May-2023: Fix Log Levels
  # 19-May-2023: Add whichLog()
  # 11-May-2023: Add isFile() and sysExit()
  # 03-May-2023: Add success()
  # 01-May-2023: Add fmt_acc()
  # 28-Apr-2023: Add LOGLEVEL='TRACE' and functions trace() & isTrace()
  # 04-Apr-2023: Add isDebug()
  # 05-Oct-2019: copied from bu-enablement repo
'''

import logging
import os
import re
import sys
import inspect

from inspect import getframeinfo, stack
from typing import Final

global SUCCESS, FAILURE, SKIPPED, APPROVED, CREATED, DENIED, EXTENSION, REVOKED

SUCCESS = 'passed'
FAILURE = 'failed'
SKIPPED = 'skipped'

APPROVED  = 'approved'
CREATED   = 'created'
DENIED    = 'denied'
EXTENSION = 'extension'
REVOKED   = 'revoked'

global CWD, LOGLEVEL, LV_TRA, LV_DEB, LV_INF, LV_WRN, LV_ERR, LV_CRI

CWD =  os.getcwd()
LOG_FILE = os.environ.get('LOG_FILE')
LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING')

# Log Levels
LV_TRA = LOGLEVEL in [ 'TRACE' ]
LV_DEB = LOGLEVEL in [ 'DEBUG', 'TRACE' ]
LV_INF = LOGLEVEL in [ 'INFO', 'DEBUG', 'TRACE' ]
LV_WRN = LOGLEVEL in [ 'WARN', 'WARNING', 'INFO', 'DEBUG', 'TRACE' ]
LV_ERR = LOGLEVEL in [ 'ERROR', 'SUCCESS', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'TRACE' ]
LV_CRI = LOGLEVEL in [ 'CRITICAL', 'ERROR', 'SUCCESS', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'TRACE' ]


if LOG_FILE:
    if LOGLEVEL in [ 'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG' ]:
        logging.basicConfig(
            filename=LOG_FILE, 
            format='%(asctime)s :: %(levelname)s :: %(message)s',
            encoding='utf-8', 
            level=LOGLEVEL
        )
    else:
        logging.basicConfig(
            filename=LOG_FILE, 
            format='%(asctime)s :: %(levelname)s :: %(message)s',
            encoding='utf-8', 
            level='DEBUG'
        )


def obj2str(data):
    res = ''
    try:
        if type(data) == str:
            res = data

        elif type(data) == list:
            res = ', '.join(data)

        elif type(data) == dict:
            res = ', '.join([ f'{k}={v}' for k,v in data.items() ])

        elif type(data) == tuple:
            res = ', '.join(data)

        elif type(data) == set:
            res = ', '.join(data)

    except Exception as err:
        trace(f"Error in obj2str: {err}, data :: {data}")

    res = str(data)

    # Remove ansi escape codes by using regex
    res = re.sub(r'\x1b\[[0-9;]*m', '', res)

    return res

def args2str(*args, **kwargs):
    res = ''
    if args:
        res += obj2str(args) + ' '

    if kwargs:
        res += obj2str(kwargs)
    
    return res

def print2err(*args, **kwargs):
    """Prints like print command but in stderr instead of stdout"""
    print( *args, file=sys.stderr, **kwargs )

def trace(*args, **kwargs):
    """Prints like print command if LOGLEVEL is TRACE"""
    if LV_TRA: 
        caller = getframeinfo(stack()[1][0])
        filename = caller.filename.replace(f'{CWD}/', '')
        print(
            f'L#{caller.lineno} ::',
            f'{filename} ::',
            "TRACE ::", 
            *args, file=sys.stderr, **kwargs
        )

def debug(*args, **kwargs):
    """Prints like print command if LOGLEVEL is DEBUG or lower"""
    if LV_DEB: 
        caller = getframeinfo(stack()[1][0])
        filename = caller.filename.replace(f'{CWD}/', '')
        print(
            f'L#{caller.lineno} ::',
            f'{filename} ::',
            "DEBUG ::", 
            *args, file=sys.stderr, **kwargs
        )
        if LOG_FILE:
            logging.debug(f"L#{caller.lineno} :: {filename} :: {args2str(*args, **kwargs)}")
        

def info(*args, **kwargs):
    """Prints like print command if LOGLEVEL is INFO or lower"""
    if LV_INF: 
        caller = getframeinfo(stack()[1][0])
        filename = caller.filename.replace(f'{CWD}/', '')
        print(
            f'L#{caller.lineno} ::',
            f'{filename} ::',
            "INFO ::", 
            *args, file=sys.stderr, **kwargs
        )
        if LOG_FILE:
            logging.info(f"L#{caller.lineno} :: {filename} :: {args2str(*args, **kwargs)}")

def warning(*args, **kwargs):
    """Prints like print command if LOGLEVEL is WARNING or lower"""
    if LV_WRN: 
        caller = getframeinfo(stack()[1][0])
        filename = caller.filename.replace(f'{CWD}/', '')
        print(
            f'L#{caller.lineno} ::',
            f'{filename} ::',
            "WARNING ::", 
            *args, file=sys.stderr, **kwargs
        )
        if LOG_FILE:
            logging.warning(f"L#{caller.lineno} :: {filename} :: {args2str(*args, **kwargs)}")

def success(*args, **kwargs):
    """Prints like print command if LOGLEVEL is ERROR or lower"""
    if LV_ERR: 
        caller = getframeinfo(stack()[1][0])
        filename = caller.filename.replace(f'{CWD}/', '')
        print(
            f'L#{caller.lineno} ::',
            f'{filename} ::',
            "SUCCESS ::", 
            *args, file=sys.stderr, **kwargs
        )
        if LOG_FILE:
            logging.info(f"L#{caller.lineno} :: {filename} :: {args2str(*args, **kwargs)}")


def error(*args, **kwargs):
    """Prints like print command if LOGLEVEL is ERROR or lower"""
    if LV_ERR: 
        caller = getframeinfo(stack()[1][0])
        filename = caller.filename.replace(f'{CWD}/', '')
        print(
            f'L#{caller.lineno} ::',
            f'{filename} ::',
            "ERROR ::",
            *args, file=sys.stderr, **kwargs
        )
        if LOG_FILE:
            logging.error(f"L#{caller.lineno} :: {filename} :: {args2str(*args, **kwargs)}")

        
def abort(*args, **kwargs):
    """Prints like print command if LOGLEVEL is CRITICAL and exits with 1"""
    if LV_CRI: 
        caller = getframeinfo(stack()[1][0])
        filename = caller.filename.replace(f'{CWD}/', '')
        print(
            f'L#{caller.lineno} ::',
            f'{filename} ::',
            "ABORT ::", 
            *args, file=sys.stderr, **kwargs
        )
        if LOG_FILE:
            logging.critical(f"L#{caller.lineno} :: {filename} :: {args2str(*args, **kwargs)}")
    sys.exit(1)

def critical(*args, **kwargs):
    """Prints like print command if LOGLEVEL is CRITICAL and exits with 1"""
    if LV_CRI: 
        caller = getframeinfo(stack()[1][0])
        filename = caller.filename.replace(f'{CWD}/', '')
        print(
            "CRITICAL ::", 
            f'L#{caller.lineno} ::',
            f'{filename} ::',
            *args, file=sys.stderr, **kwargs
        )
        if LOG_FILE:
            logging.critical(f"L#{caller.lineno} :: {filename} :: {args2str(*args, **kwargs)}")
    sys.exit(1)

def sysExit(*args, **kwargs):
    """Exits with 0 - no error - use it like print command"""
    if LV_CRI: 
        caller = getframeinfo(stack()[1][0])
        filename = caller.filename.replace(f'{CWD}/', '')
        print(
            "EXIT:", 
            f'L#{caller.lineno} ::',
            f'{filename} ::',
            *args, file=sys.stderr, **kwargs
        )
    sys.exit(0)

def isCodeBuild():
    """Return True if runs in CodeBuild else Flase - Local call"""
    # https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-env-vars.html
    return True if os.environ.get('CODEBUILD_BUILD_NUMBER') else False

def isDebug():
    """Returns True if DEBUG else False"""
    return LV_DEB

def isWarning():
    """Returns True if WARNING else False"""
    return LV_WRN


def isInt(i):
    """Returns True if given object is int or float"""
    try:
        float(i)
        return True
    except ValueError:
        return False

def isfloat(i):
    """Returns True if given object is float"""
    return isinstance(i, float)

def isLocal():
    """Return True if not runs in CodeBuild else Flase - CodeBuild call"""
    return not isCodeBuild()

def isTrace():
    """Returns True if TRACE else False"""
    return LV_TRA

def whichLog():
    return LOGLEVEL

def fmt_acc(account, account_alias=None):
    """Returns (account) [account_alias]"""
    account_alias = account if account_alias is None else account_alias
    return f'({account}) [{account_alias}]'

def isFile(file):
    """Returns True of False"""
    return os.path.isfile(file)

def isDir(my_path):
    """Returns True if exist or False"""
    return os.path.exists(my_path)
