#!/usr/bin/env python

import argparse
import ast
import boto3
import concurrent.futures
import csv
import datetime
import inspect
import ipaddress
import logging
import json
import math
import os
import platform
import random
import re
import sys
import textwrap
import time
import uuid
import yaml

from argparse import ArgumentParser
from botocore.exceptions import ClientError
from colorama import init as colorama_init
from datetime import date, datetime, timezone, timedelta
from inspect import getframeinfo, stack
from colorama import Fore, Style
from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers.web import *
from pygments.lexers.data import *

from types import SimpleNamespace
if platform.system() == 'Windows':
    from colorama import just_fix_windows_console
    just_fix_windows_console()

from common import *
colorama_init()

# Mutable & un-protected CONTANSTS 
global CACHE_PATH, CACHE_TTL, COLORED, UNITTEST, CFG_IND_SIZE, CFG_TAB_SIZE, CFG_LEN_SIZE, CFG_IND, CFG_TAB, CFG_REP, CFG_LIN

CACHE_PATH = os.environ.get('CACHE_PATH')
CACHE_TTL = 8600      # default cache expiration in seconds

LOG_FILE = os.environ.get('LOG_FILE')
LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING')

COLORED = os.environ.get('COLORED')
UNITTEST = False
CWD =  os.getcwd()

CFG_IND_SIZE = 2
CFG_TAB_SIZE = 4
CFG_LEN_SIZE = 120

CFG_IND = ' ' * CFG_IND_SIZE
CFG_TAB = ' ' * CFG_TAB_SIZE
CFG_REP = '#'
CFG_LIN = '-'

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

def extract(string:str, needle:str):
    """Extract & return anything before needle
    
    Args:
        string (str): heystack string to use
        needle (str): needle to find in heystack

    Returns left match before needle or '' if not found
    """
    nIndex = string.find(needle)
    res = string[0:nIndex].strip() if nIndex != -1 else ''
    return res

def rextract(string:str, needle:str):
    """Extract & return anything after needle
    
    Args:
        string (str): heystack string to use
        needle (str): needle to find in heystack

    Returns right match after needle or '' if not found
    """
    nWidth = len(needle)
    nIndex = string.rfind(needle)
    res = string[nIndex + nWidth:].strip() if nIndex != -1 else ''
    return res

def list_cfg():
    """Returns list of Config Variables"""
    return [
        'CACHE_PATH',
        'CACHE_TTL',
        'LOGLEVEL',
        'COLORED',
        'UNITTEST',
        'CWD',
        'CFG_IND_SIZE',
        'CFG_TAB_SIZE',
        'CFG_LEN_SIZE',
        'CFG_IND',
        'CFG_TAB',
        'CFG_REP',
        'CFG_LIN',
    ]

def cur_cfg():
    """Returns & prints current config variables"""
    gVars = globals()
    eVars = {
        'CACHE_PATH': 'str: path for cache files',
        'LOGLEVEL': 'str: log level',
        'COLORED': 'bool: enable or disable',
        'UNITTEST': 'bool: enable or disable',
        'CWD': 'str: current working directory',

        'CFG_IND_SIZE': 'int: indent size',
        'CFG_TAB_SIZE': 'int: tab size',
        'CFG_LEN_SIZE': 'int: wide lenght size',

        'CFG_IND': 'str: indent in spaces',
        'CFG_TAB': 'str: tab in spaces',
        'CFG_REP': 'str: repeat character for wide print',
        'CFG_LIN': 'str: repeat character for wide line',

    }
    res = []
    for k in eVars.keys():
        v = eVars[k]
        res.append({
            'Name': k,
            'Value': gVars.get(k),
            'Type': extract(v, ':'),
            'Description': rextract(v, ':'),
        })

    return res

def set_cfg(name:str, value):
    """Set config value or add one if not exist"""
    if name in list_cfg():
        globals()[name] = value
    else:
        iWarning('Invalid Config! Valid Configs:', list_cfg())

def log_levels():
    """Returns ordered list of valid log levels from lowest to highest"""
    return [
        'TRACE',
        'DEBUG',
        'INFO',
        'WARNING',
        'ERROR',
        'CRITICAL',
    ]


def print_stderr(*args, **kwargs):
    """Prints like print command but in stderr instead of stdout"""
    print( *args, file=sys.stderr, **kwargs )

## Color Error Log for Local Runs

def maxLen(arr: dict | list) -> int:
    """Returns max lenght of list items or dictionary keys"""
    if not arr: return 0
    if isinstance(arr, dict):
        arr = arr.keys()
    rs = [len(k) for k in arr]
    return max(rs)

def iTrace(*args, **kwargs):
    """Prints like print if LOGLEVEL is TRACE"""
    caller = inspect.stack()[1]
    filename = caller.filename.replace(f'{CWD}/', '')
    if LV_TRA:
        print(
            iColor( f'L#{caller.lineno}', 'iGray' ), '::',
            iColor( f'{filename}', 'iGray' ), '::',
            iColor( 'TRACE'.ljust(maxLen(log_levels())), 'Gray' ), '::',
            *args, file=sys.stderr, **kwargs
        )


def iDebug(*args, **kwargs):    
    """Prints like print if LOGLEVEL is DEBUG or lower"""
    caller = inspect.stack()[1]
    filename = caller.filename.replace(f'{CWD}/', '')
    if LV_DEB:
        print(
            iColor( f'L#{caller.lineno}', 'iGray' ), '::',
            iColor( f'{filename}', 'iGray' ), '::',
            iColor( 'DEBUG'.ljust(maxLen(log_levels())), 'Yellow' ), '::',
            *args, file=sys.stderr, **kwargs
        )
        if LOG_FILE:
            logging.debug(f"L#{caller.lineno} :: {filename} :: {args2str(*args, **kwargs)}")


def iInfo(*args, **kwargs):
    """Prints like print if LOGLEVEL is INFO or lower"""
    caller = inspect.stack()[1]
    filename = caller.filename.replace(f'{CWD}/', '')
    if LV_INF:
        print(
            iColor( f'L#{caller.lineno}', 'iGray' ), '::',
            iColor( f'{filename}', 'iGray' ), '::',
            iColor( 'INFO'.ljust(maxLen(log_levels())), 'Green' ), '::',
            *args, file=sys.stderr, **kwargs
        )
        if LOG_FILE:
            print(f'Writing log to :: {LOG_FILE}')
            logging.info(f"L#{caller.lineno} :: {filename} :: {args2str(*args, **kwargs)}")


def iWarning(*args, **kwargs):
    """Prints like print if LOGLEVEL is WARNING or lower"""
    caller = inspect.stack()[1]
    filename = caller.filename.replace(f'{CWD}/', '')
    if LV_WRN:
        print(
            iColor( f'L#{caller.lineno}', 'iGray' ), '::',
            iColor( f'{filename}', 'iGray' ), '::',
            iColor( 'WARNING'.ljust(maxLen(log_levels())), 'Red' ), '::',
            *args, file=sys.stderr, **kwargs
        )
        if LOG_FILE:
            logging.warning(f"L#{caller.lineno} :: {filename} :: {args2str(*args, **kwargs)}")


def iSuccess(*args, **kwargs):
    """Prints like print if LOGLEVEL is ERROR or lower"""
    caller = inspect.stack()[1]
    filename = caller.filename.replace(f'{CWD}/', '')
    if LV_ERR:
        print(
            iColor( f'L#{caller.lineno}', 'iGray' ), '::',
            iColor( f'{filename}', 'iGray' ), '::',
            iColor( 'SUCCESS'.ljust(maxLen(log_levels())), 'Green' ), '::',
            *args, file=sys.stderr, **kwargs
        )


def iError(*args, **kwargs):
    """Prints like print if LOGLEVEL is ERROR or lower"""
    caller = inspect.stack()[1]
    filename = caller.filename.replace(f'{CWD}/', '')
    if LV_ERR:
        print(
            iColor( f'L#{caller.lineno}', 'iGray' ), '::',
            iColor( f'{filename}', 'iGray' ), '::',
            iColor( 'ERROR'.ljust(maxLen(log_levels())), 'Red' ), '::',
            *args, file=sys.stderr, **kwargs
        )
        if LOG_FILE:
            logging.error(f"L#{caller.lineno} :: {filename} :: {args2str(*args, **kwargs)}")


def iAbort(*args, **kwargs):
    """Prints like print if LOGLEVEL is CRITICAL and exits with 1"""
    caller = inspect.stack()[1]
    filename = caller.filename.replace(f'{CWD}/', '')
    if LV_CRI:
        print(
            iColor( f'L#{caller.lineno}', 'iGray' ), '::',
            iColor( f'{filename}', 'iGray' ), '::',
            iColor( 'ABORT'.ljust(maxLen(log_levels())), 'Red' ), '::',
            *args, file=sys.stderr, **kwargs
        )
        if LOG_FILE:
            logging.critical(f"L#{caller.lineno} :: {filename} :: {args2str(*args, **kwargs)}")
    sys.exit(1)


def iCritical(*args, **kwargs):
    """Prints like print if LOGLEVEL is CRITICAL and exits with 1"""
    caller = inspect.stack()[1]
    filename = caller.filename.replace(f'{CWD}/', '')
    if LV_CRI:
        print(
            iColor( f'L#{caller.lineno}', 'iGray' ), '::',
            iColor( f'{filename}', 'iGray' ), '::',
            iColor( 'CRITICAL'.ljust(maxLen(log_levels())), 'Red' ), '::',
            *args, file=sys.stderr, **kwargs
        )
        if LOG_FILE:
            logging.critical(f"L#{caller.lineno} :: {filename} :: {args2str(*args, **kwargs)}")
    sys.exit(1)


def iSysExit(*args, **kwargs):
    """Exits with 0 - no error"""
    caller = inspect.stack()[1]
    filename = caller.filename.replace(f'{CWD}/', '')
    if LV_CRI:
        print(
            iColor( f'L#{caller.lineno}', 'iGray' ), '::',
            iColor( f'{filename}', 'iGray' ), '::',
            iColor( 'SysExit(0)'.ljust(maxLen(log_levels())), 'Red' ), '::',
            *args, file=sys.stderr, **kwargs
        )
    sys.exit(0)


def awsPartition():
    """Returns 'aws-us-gov' for GovCloud & 'aws' for Commercial"""
    sts = boto3.client('sts')
    return sts.get_caller_identity()['Arn'].split(':')[1]

def isGovRegion():
    """Returns True or False"""
    return awsPartition() == 'aws-us-gov'


def estRegion():
    """Returns True if region is us-east or us-gov-east-1"""
    return 'us-gov-east-1' if isGovRegion() else 'us-east-1'


def isGovSts():
    """Returns True if current sts profile is GovCloud"""
    return awsPartition() == 'aws-us-gov'

## Folder Management


def uni_path(path=''):
    """Converts Windows "\" in file path to universal/linux "/" in file path"""
    return path.replace('\\', '/').replace('/./', '/')


def clean_path(path):
    """Returns removed '../' from middle of given absolute path"""
    path = uni_path(path)
    paths = path.split('/')

    while '..' in paths:
        if paths[0] == '..':
            break
        for i, path in enumerate(paths):
            if path == '..' and i > 0:
                try:
                    paths.pop( i )
                    paths.pop( i - 1 )
                except Exception:
                    pass

    res = '/'.join(paths)

    return res


def file_title(name):
    """Returns Title Case of file, used by cur_dir()"""
    res = name
    rMap = ['-', '_' ]
    for key in rMap:
        res = res.replace(key, ' ')

    res = res.title().strip()
    res = correct_capitalization(res)

    return res


def cur_dir():
    """Returns dict of current dir and file who called this function"""
    caller_frame = inspect.stack()[1]
    file = caller_frame.filename.replace('//', '/')
    fullPath = os.path.realpath(file)
    path, filename = os.path.split(fullPath)
    name = os.path.splitext(filename)[0]
    title = file_title( name )

    PREFIX = os.environ.get('PREFIX', '')
    # Remove trailing _ or -
    if PREFIX and (PREFIX[-1] == '-' or PREFIX[-1] == '_'):
        PREFIX = PREFIX[0:-1]
    PrefixName = f'{PREFIX.lower()}-{name}' if PREFIX else name

    res = {
        'CWD': os.getcwd(),
        'Path': clean_path(path),
        'File': file,
        'FileName': filename,
        'Name': name,
        'PrefixName': PrefixName,
        'Title': title,
        'GR2': '### GR2-0 / ' + title,
    }

    for k in res.keys():
        res[k] = uni_path(res[k])

    return res


def cur_file(add_path=None, prefix=None):
    """Returns string

    Args:
        add_path (str): optional
        prefix (str): optional

    Returns:
        current-file
        add_path/current-file
        add_path/prefix-current-file
        prefix-current-file
    """
    add_path = add_path+'/' if add_path else ''
    prefix = prefix+'-' if prefix else ''
    caller_frame = inspect.stack()[1]
    file = caller_frame.filename
    fullPath = os.path.realpath(file)
    path, filename = os.path.split(fullPath)
    res = os.path.splitext(filename)[0]
    return add_path+prefix+res


def mk_folder(my_path):
    """Makes folder if not exist"""
    if not os.path.exists(my_path):
        os.makedirs(my_path)


def rm_empty_folder(my_path):
    """Removes folder if is empty"""
    if not os.path.exists(my_path):
        return
    folders = list(os.walk(my_path))
    for folder in folders:
        # print("All Folder -> ",folder)
        # remove only empty folders
        if not folder[2]:
            os.rmdir(folder[0])

## Print Utils


def terminal_size():
    """Returns dict of terminal columns & lines size

        {
            'columns': int,
            'lines': int
        }
    """
    ts = os.get_terminal_size()
    return {
        'columns': ts.columns,
        'lines': ts.lines
    }


def rspace(string, width: int = 3, trunk: bool = False):
    """Returns right spaced string

    Args:
        string (str): input
        width (int): desired width
        trunk (bool): trunk if string is larger that width
    """
    if trunk and len(string) > width:
        return string[0:width-3]+'...'
    return str(string) + ' '*(width-len(str(string))) if len(str(string)) < width else string


def lspace(string, width=3, trunk=False):
    """Returns left spaced string

    Args:
        string (str): input
        width (int): desired width
        trunk (bool): trunk if string is larger that width
    """
    if trunk and len(string) > width:
        return string[0:width-3]+'...'
    return ' '*(width-len(str(string))) + str(string) if len(str(string)) < width else string


def ndigits(string, width=3):
    """Returns leading zero string up to width

    Args:
        string (str): input
        width (int): desired width
    """
    return '0'*(width-len(str(string))) + str(string) if len(str(string)) < width else string


def progress_print(counter: int=8, indent: int=8, limit: int=88, char: str='.'):
    """Show progress bar with . 

    Usage:
        myCounter = 8 # outside the loop
            myCounter = progress_print(counter=myCounter) # inside the loop
    
    Args:
        counter (int): current progress
        indent (int): left indent for first progress print
        limit (int): how many items per each progress bar per line
        char (char): single character for progess bar, default is .
    """
    if counter == indent:
        sys.stdout.write(' '*indent)

    counter += 1
    if counter > limit:
        print()
        counter = indent
    else:
        sys.stdout.write('.')

    sys.stdout.flush()

    return counter


def to_len(string=CFG_REP, delimeter=CFG_REP, width=CFG_LEN_SIZE):
    """Returns 'string' with following 'delimeter' up to given 'width'

    Args:
        string    (str): Optional string. default #
        delimeter (str): Optional string. default #
        width     (int): Optional width. default CFG_LEN_SIZE
    """
    string = ' ' if len(string) == 0 else string
    delimeter = ' ' if not delimeter else delimeter
    spc = string if string == delimeter else ' '
    res = string + spc
    while len(res) < width:
        res += delimeter

    return res


def ppwide(string: str=CFG_REP, delimeter: str=CFG_REP, width: int=CFG_LEN_SIZE):
    """Prints 'string' with following 'delimeter' up to given 'width'

    Args:
        string    (str): Optional string. default #
        delimeter (str): Optional string. default #
        width     (int): Optional width. default CFG_LEN_SIZE
    """
    print(to_len(string, delimeter, width))


def ppwide_err(string: str=CFG_REP, delimeter: str=CFG_REP, width: int=CFG_LEN_SIZE):
    """Prints to sys.stderr 'string' with following 'delimeter' up to given 'width'

    Args:
        string    (str): Optional string. default #
        delimeter (str): Optional string. default #
        width     (int): Optional width. default CFG_LEN_SIZE
    """
    print(to_len(string, delimeter, width), file=sys.stderr)


def printl(char: str, **kwargs) -> None:
    """Prints to_len - see to_len() """
    print(to_len(char, **kwargs))


def printh(char: str, rep='-', width: int = 120):
    print(char)
    wline(rep=rep, width=width)


def printhh(char: str, rep='-', width: int = 120):
    print()
    printh(char, rep=rep, width=width)


def printdoc(title: str, doc='', etl: dict={}, rep='-', width: int = 120):
    """Prints doc lines and replace key with val from etl dict
    
    Args:
        title (str): Title of doc
        doc (str): Multi-line doc wrapped in triple qoute or double-qoute, # used for comment 
        etl (dict): dictonary of {Search: Replace}
        width (int): width of wideline after Title
    """
    print()
    printh(title, rep=rep, width=width)
    data = doc.split('\n')
    for line in data:
        for key in etl.keys():
            line.replace(key, etl[key])
            color = 'iGreen' if line.strip().startswith('#') else 'iYellow'
            print(iColor(line, color))


def printll(char: str, **kwargs) -> None:
    """Prints to_len with leading an ampty line- see to_len() """

    print()
    printl(char, **kwargs)


def to_space(string, width=3):
    """Returns leading space to width i.e. func(1, 3) returns '  1'

    Args:
        string (str|int): Input to make it left spaced up to width
        width      (int): Width of output. Default 3
    """
    return ' '*(width-len(str(string))) + str(string) if len(str(string)) < width else string


def wline(rep=CFG_LIN, width: int=CFG_LEN_SIZE):
    """Prints an spacer line"""
    print(to_len(string=rep, delimeter=rep, width=width))


def colors():
    """Returns list of valid colors"""
    return [
        'Black',
        'Gray',
        'Red',
        'Green',
        'Yellow',
        'Blue',
        'Magenta',
        'Cyan',
        'White',
        'iBlack',
        'iGray',
        'iRed',
        'iGreen',
        'iYellow',
        'iBlue',
        'iMagenta',
        'iCyan',
        'iWhite',
    ]


def iColors():
    """Returns list of extended colors - used internally"""
    return [
        'LIGHTBLACK_EX',
        'LIGHTRED_EX',
        'LIGHTGREEN_EX',
        'LIGHTYELLOW_EX',
        'LIGHTBLUE_EX',
        'LIGHTMAGENTA_EX',
        'LIGHTCYAN_EX',
        'LIGHTWHITE_EX',
    ]


def cStyle():
    """Returns list of valid styles used by print in color"""
    return [
        'DIM',
        'NORMAL',
        'BRIGHT'
    ]


def incolor(string, color: str, cStyle: str = 'normal'):
    """Returns string in color with given cStyle

    Args:
        string (any): any printable object
        color (str): any valid color in iColors()
        cStyle (str): any valid style of 'DIM', 'NORMAL', 'BRIGHT' - not case sensetive
    """
    if COLORED is None:
        return string

    cTitle = color.title()
    if cTitle[0:1] == 'I':
        cTitle = color[0:1].lower()+color[1:].title()
    cTitle = cTitle.replace('Gray', 'Black')
    cTitle = cTitle.replace('iGray', 'iBlack')

    sColor = None
    paint = None
    nc = getattr(Style, 'RESET_ALL')
    if cTitle[0:1] == 'i':
        sColor = f'LIGHT{cTitle[1:].upper()}_EX'
        if sColor in iColors():
            paint = getattr(Fore, sColor)
    elif cTitle in colors():
        paint = getattr(Fore, cTitle.upper())

    sString = 'NORMAL'
    styles = [ 'DIM', 'NORMAL', 'BRIGHT' ]
    if cStyle.upper() in styles:
        sString = cStyle.title()
        cStyle = getattr(Style, cStyle.upper())

    if isTrace():
        print(f'Color : {color}')
        print(f'cTitle: {cTitle}')
        print(f'sColor: {sColor}')
        print(f'cStyle: {sString}')

    if paint:
        return f"{paint}{cStyle}{string}{nc}"

    return string


def iColor(string, color: str):
    """Adds shell color to given string ends with reset color

    Args:
        string (str): Input
        color  (str): Color name. Case sensitive.

    Color List:
        Black, Gray, Red, Green, Yellow, Blue, Magenta, Cyan, White
    """
    if isCodeBuild():
        return string
    
    string = str(string)
    rs = {
        'NC': '\033[0m',         # Text Reset
        'Black': '\033[0;30m',   # Black
        'Gray': '\033[0;90m',    # Gray
        'Red': '\033[0;91m',     # Red
        'Green': '\033[0;92m',   # Green
        'Yellow': '\033[0;93m',  # Yellow
        'Blue': '\033[0;94m',    # Blue
        'Magenta': '\033[0;95m', # Magenta
        'Cyan': '\033[0;96m',    # Cyan
        'White': '\033[0;97m',   # White
        
        # Extended Normal Colors
        'Brown': '\033[38;5;136m',  # Brown
        'Orange': '\033[38;5;208m', # Orange
        'Lemon': '\033[38;5;48m',   # Lemon
        'Rose': '\033[38;5;160m',   # Rose
        'Pink': '\033[38;5;200m',   # Pink

        # 1: Bold Colors
        'bBlack': '\033[1;30m',   # Black
        'bGray': '\033[1;90m',    # Gray
        'bRed': '\033[1;91m',     # Red
        'bGreen': '\033[1;92m',   # Green
        'bYellow': '\033[1;93m',  # Yellow
        'bBlue': '\033[1;94m',    # Blue
        'bMagenta': '\033[1;95m', # Magenta
        'bCyan': '\033[1;96m',    # Cyan
        'bWhite': '\033[1;97m',   # White

        # 3: Italic Colors
        'iBlack': '\033[3;30m',   # Black
        'iGray': '\033[3;90m',    # Gray
        'iRed': '\033[3;91m',     # Red
        'iGreen': '\033[3;92m',   # Green
        'iYellow': '\033[3;93m',  # Yellow
        'iBlue': '\033[3;94m',    # Blue
        'iMagenta': '\033[3;95m', # Magenta
        'iCyan': '\033[3;96m',    # Cyan
        'iWhite': '\033[3;97m',   # White

        # 4: Underline Colors
        'uBlack': '\033[4;30m',   # Black
        'uGray': '\033[4;90m',    # Gray
        'uRed': '\033[4;91m',     # Red
        'uGreen': '\033[4;92m',   # Green
        'uYellow': '\033[4;93m',  # Yellow
        'uBlue': '\033[4;94m',    # Blue
        'uMagenta': '\033[4;95m', # Magenta
        'uCyan': '\033[4;96m',    # Cyan
        'uWhite': '\033[4;97m',   # White
    }

    if color in rs and platform.system() != 'Windows':
        return f"{rs[color]}{string}{rs['NC']}"
    else:
        return string


def blue_green(lstr, rstr, sep=' ', lcol='Blue', rcol='Green'):
    """Returns lstr in blue and rstr in green

    Args:
        lst (str): left string
        rstr (str): right string
        sep (str): left and right strings sepatator, default is ' '
        lcol (str): any valid color for left string, default 'Blue'
        rcol (str): any valid color for right string, default 'Green' 
    """
    return iColor(lstr, lcol) + sep + iColor(rstr, rcol)


def blue_green_dict_print(data: dict = {}, sep=' ', lcol='Blue', rcol='Green'):
    """Prints in blue key + sep + green value of dict with aligned keys

    Args:
        data (dict): any dictionary, empty key will print empty line
        sep (str): left and right strings sepatator, default is ' '
        lcol (str): any valid color for left string, default 'Blue'
        rcol (str): any valid color for right string, default 'Green' 
    """
    width = maxLen(data.keys())
    for key in data.keys():
        if not key and not data[key]:
            print()
            continue
        print(blue_green(key.ljust(width), data[key], sep=sep, lcol=lcol, rcol=rcol))


def print_color_dict(data: dict = {}, sep=' : ', lcol='', rcol='iYellow'):
    """Prints key : IYellow value of dict with aligned keys
    Args:
        data (dict): any dictionary, empty key will print empty line
        sep (str): left and right strings sepatator, default is ' : '
        lcol (str): any valid color for left string, default ''
        rcol (str): any valid color for right string, default 'iYellow' 

    """
    blue_green_dict_print(data=data, sep=sep, lcol=lcol, rcol=rcol)

## String, array & int

def append_unique(res:list, obj:str|int):
    """Append string to array if string not in array"""
    if obj not in res: res.append(obj)
    return res

def replace_all(string:str, lookup: list|dict|str, update: str=''):
    """Returns string of every match in 'lookup:list' replace with 'update:str' 
    or every 'key' match in 'lookup:dict' to 'key.value'

    Args:
        string (str): input string as heystack
        lookup (list | dict): 
            if (list) then replace all matches with given replace
            if (dict) then replace each match of key to its value
            if (str) and no update then remove all matches in str
            if (str) and update then repalce str[n] with update[n]
        update (str): used only if search is 'list', default ''

    Examples: 
        '2023-12-30T16:49:47.756011+00:00', lookup=[':','.','+'], update='_'
        '2023-12-30T16_49_47_756011_00_00'
        '2023-12-30T16:49:47.756011+00:00', lookup={'T': ' ', ':': '-', '+': '_'}
        '2023-12-30 16-49-47.756011_00-00'     
        '2023-12-30T16:49:47.756011+00:00', lookup='T+', update='  '
        '2023-12-30 16-49-47.756011_00-00'     
    """

    res = string
    if isinstance(lookup, str):
        for i, rs in enumerate(lookup):
            if len(update) < i:
                res = res.replace(rs, update[i])
            else:
                res = res.replace(rs, '')

    if isinstance(lookup, list):
        for rs in lookup:
            res = res.replace(rs, update)

    if isinstance(lookup, dict):
        for key in lookup.keys():
            res = res.replace(key, lookup[key])

    return res


def round_up(n, digits=0):
    """Returns round up (ceiling) of n to given digits floating point precision"""
    return math.ceil(n * 10**digits) / 10**digits if digits != 0 else math.ceil(n)


def round_down(n, digits=0):
    """Returns round down (floor) of n to given digits floating point percision"""
    return math.floor(n * 10**digits) / 10**digits if digits != 0 else math.floor(n)


## File Management

def flatten_data(data):
    """Returns flatten data separated by _"""
    res = {}
 
    def flatten(obj, name=''):
        """Returns flatten data object - internal function"""
        if isinstance(obj, dict): 
            for o in obj:
                flatten(obj[o], name + o + '_')
        elif isinstance(obj, list): 
            for i, o in enumerate(obj):
                flatten(o, name + str(i) + '_')
        else:
            res[name[:-1]] = obj
 
    flatten(data)
    return res


def remove_extension(file: str):
    """Rturn filename without extension"""
    res = file
    if '.' in file:
        while res and not res.endswith('.'):
            res = res[0:-1]
    
    while res and res.endswith('.'):
        res = res[0:-1]

    return res


def isFile(file):
    """Returns True if given file is a file"""
    return os.path.isfile(file)


def rm_file(file):
    """Removes given file if given file is a file"""
    if os.path.isfile(file):
        os.remove(file)
    return os.path.isfile(file)


def dot_path(string):
    """Returns . delimetered path insted of slash or backslash. ex. buildspec/migration.yml -> builspec.migration.yml"""
    return string.replace('\\', '/').replace('/', '.')


def file_read_lines(my_file):
    """Return False or array of given files lines"""
    res = []
    try:
        with open(my_file) as file:
            rs = file.readlines()
            for r in rs:
                r = r.replace('\r\n', '').replace('\n', '').strip()
                res.append(r)
            return res
    except Exception as err:
        iError('util.file_read_lines, file:', my_file, 'Error:', err)
    return res

def file_read_input_file(my_file):
    """Reads input files & returns list of json dict
    
    Args:
        my_file (str): input file

    Expected format: No space items of lines - repalce space on each column with -
        AccountId AccountName Region SKU BU Email 

    Returns list of: { AccountId, AccountName, Region, SKU, BU, Email } 
    """
    res = []
    if not isFile(my_file):
        iWarning('Unable to read given file!')
        return res

    accounts = file_read_lines(my_file)

    if not accounts:
        iWarning('Given file is empty!')
        return res

    for acc in accounts:
        acc  = acc.replace('\r\n','').replace('\n', '')
        if not acc:
            continue

        iDebug("LB Removed  :", acc)

        if acc.startswith('#'):
            res.append({'Comment': acc})
            continue

        while '  ' in acc:
            acc = acc.replace('  ',' ')

        iDebug("Single space:", acc)
        
        acc = acc.split(' ')
        AccountId=  acc[0]
        AccountName = acc[1]
        Region = acc[2] 
        SKU = acc[3]
        BU = acc[4]

        # 6 column has email
        if len(acc) > 5:
            Email = acc[5]
            rs = {
                'AccountId': AccountId,
                'AccountName': AccountName,
                'Region': Region,
                'SKU': SKU,
                'BU': BU,
                'Email': Email,
            }
        else:
            rs = {
                'AccountId': AccountId,
                'AccountName': AccountName,
                'Region': Region,
                'SKU': SKU,
                'BU': BU,
            }

        iDebug(rs)
        res.append(rs)

    return res

def file_append_line(my_file, line):
    """Appends line to the given file and returns True of False if fails"""
    try:
        with open(my_file, 'a') as file:
            file.write(line + '\n')
            return True
    except Exception as err:
        iError('util.file_append_line, file:', my_file, 'Line:', line, 'Error:', err)
    return False

def file_append_lines(my_file, lines:list):
    """Appends lines to the given file and returns True of False if fails"""
    try:
        with open(my_file, 'a') as file:
            for line in lines:
                file.write(line + '\n')
            return True
    except Exception as err:
        iError('util.file_append_line, file:', my_file, 'Line:', line, 'Error:', err)
    return False

def add_comment_to_yaml(file_path, comments: list|str):
    """Add comments to a YAML File"""
    with open(file_path, 'r') as file:
        data = get_yaml(file_path)

    # Convert to list if is not
    if isinstance(comments, str):
        comments = [comments]

    with open(file_path, 'w') as file:
        for comment in comments:
            # Do not add # if already exist in comment
            if comment.strip().startswith('#'):
                file.write(f"{comment}\n")
            # If empty line just add an empty line
            elif not comment:
                file.write(f"\n")
            # Add # to comment without #
            else:
                file.write(f"# {comment}\n")

        # Append YAML Data
        yaml.dump(data, file, default_flow_style=False)

def file_prepend_lines(my_file, lines:list):
    """Prepend lines to the given file and returns True of False if fails"""
    flines = file_read_lines(my_file)
    try:
        with open(my_file, 'w') as file:
            # Prepend lines
            for line in lines:
                file.write(line + '\n')

            # Append lines of file
            for line in flines:
                file.write(line + '\n')
            return True
    except Exception as err:
        iError('util.file_append_line, file:', my_file, 'Line:', line, 'Error:', err)
    return False


def get_dir(path):
    """Returns dict of Path, Dirs, & Files for path of [start][*][.ext] 

    Args:
        path (str | None): path to search or [start][*][.ext]
    """
    res = {'Path': '', 'Files': [], 'Paths': []}

    if not path:
        path = cur_dir()['Path']
    iTrace('path:', path)

    full_path = clean_path(path)
    iTrace('full_path:', full_path)
    paths = full_path.split('/')
    iTrace('paths:', paths)

    filter = paths[-1]
    iTrace('filter:', filter)
    paths.pop(-1)
    path = '/'.join(paths)
    res['Path'] = path
    iTrace('path:', path)

    files = os.listdir(path)

    files = [f for f in files if os.path.isfile( path + '/' + f )]

    start = end = None
    if filter.startswith('.'):
        iDebug('.')
        end = filter

    if filter.startswith('*'):
        iDebug('*')
        filter = filter[1:]
        end = filter

    if '*' in filter[1:]:
        iDebug('start * end')
        filters = filter.split('*')
        start = filters[0]
        end = filters[-1]

    iTrace(f'start: {start}')
    iTrace(f'end: {end}')

    # filtered files
    for file in files:
        if start and end:
            if file.startswith(start) and file.endswith(end):
                iDebug('start & end', file)
                res['Files'].append(file)

        elif start:
            if file.startswith(start):
                iDebug('start', file)
                res['Files'].append(file)

        elif end:
            if file.endswith(end):
                iDebug('end', file)
                res['Files'].append(file)

    # filter paths
    res['Paths'] = []
    for file in res['Files']:
        res['Paths'].append(path + '/' + file)

    return res


def get_file(my_file):
    """Returns content of file or False if fails"""
    try:
        with open(my_file, 'r') as file:
            res = file.read()
            return res
    except Exception as err:
        iError('util.get_file, file:', my_file, 'Error:', err)
    return False


def put_file(my_file, data):
    """Returns True if data written to file otherwise False"""
    try:
        with open(my_file, 'w') as file:
            file.write(str(data)+'\n')
            return True
    except Exception as err:
        iError('util.put_file, file:', my_file, 'Error:', err)
    return False


def get_csv(my_file, encoding='utf-8'):
    """Returns content of given csv file
    
    Reads:
        data: [
            [key1, key2, key3, ...], # first row
            [val1, val2, val3, ...], # each row items
            ...
        ]

    Returns:
        data: [
            {key1: val1, key2: val2, key3: val3,  ...}, # any row
            {key1: val1, key2: val2, key3: val3,  ...}, # any row
            ...
        ]

    """
    res = []
    keys = []
    try:
        with open(my_file, newline='', encoding=encoding) as csvfile:
            rs = csv.reader(csvfile, quoting=csv.QUOTE_ALL)
            for i, rs in enumerate(rs):
                # extract keys from first recoed
                if i == 0: 
                    keys = rs
                    continue

                # Convet values to dict of key: val
                rec = {}
                for j, key in enumerate(keys):
                    rec['account'] = ''
                    rec[key] = rs[j] if len(rs) <= len(keys) else ''

                # extract account id    
                rec['account'] = rec.get('arn', '').split(':')[4]
                res.append(rec)
        return res
    except Exception as err:
        iError('util.get_csv, file:', my_file, 'Error:', err)

    return res


def put_csv(my_file, data, encoding='utf-8'):
    """Writes csv file & handles missing keys - columns

    Args:
        file (str):
            csv_filename.csv
        data: [
            {key: val, key1: val1, ...}, # each row items
            {key: val, key1: val1, ...}, # each row items
            ...
        ]

    Returns True or False
    """

    # build full key map
    KEYS = []
    for rs in data:
        for key in rs.keys():
            if key not in KEYS:
                KEYS.append(key)
    try:
        with open(my_file, 'w', newline='', encoding=encoding) as csv_file:
            writer = csv.writer(csv_file)

            for i, rs in enumerate(data):
                if i == 0:
                    writer.writerow(KEYS)
                    iTrace(rs.keys())

                values = {}
                for key in KEYS:
                    values[key] = rs.get(key)
                writer.writerow(values.values())
    except Exception as err:
        if 'Permission denied' in str(err):
            iWarning('Permission error! You might have the same file opened in excel! Close it & retry!')
        iError('util.put_csv, file:', clean_path(my_file), 'Error:', err)
        return False
    return True


def get_json(my_file: str):
    """Returns json file"""
    try:
        with open(my_file, 'r', encoding='utf-8') as json_file:
            res = json.load(json_file)
        return res
    except Exception as err:
        iError('util.get_json, file:', my_file, 'Error:', err)
        return {}


def put_json(my_file, my_data, minify=True, default=str, sort_key=False, ensure_ascii=False):
    try:
        with open(my_file, 'w', encoding='utf-8') as json_file:
            if minify:
                json.dump(my_data, json_file, default=default, sort_keys=False, ensure_ascii=ensure_ascii )
            else:
                json.dump(my_data, json_file, indent=4, default=default, sort_keys=False, ensure_ascii=ensure_ascii )
        return True
    except Exception as err:
        iError('util.put_json, file:', my_file, 'Error:', err)
    return False


def pretty_json(jsonData=[]):
    """Returns Pretty Json"""
    return json.dumps(jsonData, indent=4, default=str, ensure_ascii=False)


def ppjson(data):
    """Prints Pretty Json"""
    print(pretty_json(data))


def ppjsonc(data):
    """Prints Pretty Json in color"""
    print(highlight(
        pretty_json(data),
        lexer=JsonLexer(),
        formatter=Terminal256Formatter(),
    ))


def get_yaml(my_file):
    """Returns content of YAML file"""
    try:
        with open(my_file, 'r') as file:
            my_data = yaml.safe_load(file)
        return my_data
    except Exception as err:
        iError('util.get_yaml, file:', my_file, 'Error:', err)
        return {}


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        """Fixes yaml Dumper error"""
        return True


def put_yaml(my_file, my_data):
    """Writes given data to given file"""
    try:
        with open(my_file, 'w') as file:
            res = yaml.dump(my_data, file, Dumper=NoAliasDumper)
        return res
    except Exception as err:
        iError('util.put_yaml, file:', my_file, 'Error:', err)


def pretty_yaml(yamlData=[], indent=4):
    """Returns Pretty Yaml"""
    return yaml.dump(yamlData, indent=indent, sort_keys=False, Dumper=NoAliasDumper)


def ppyaml(data, indent=4):
    """Prints Pretty Yaml"""
    print(pretty_yaml(data, indent=indent))


def ppyamlc(data):
    """Prints Pretty Yaml in color - wihout comments"""
    print(highlight(
        pretty_yaml(data),
        lexer=YamlLexer(),
        formatter=Terminal256Formatter(),
    ))


def ppyamlc_file(file):
    """Prints Pretty Yaml in color from file - including comments"""
    data = get_file(file)
    print(highlight(
        data,
        lexer=YamlLexer(),
        formatter=Terminal256Formatter(),
    ))


## File Management - Maps


def pytest_map(index=None):
    res = {
        'pretest-report.json',
        'posttest-report.json',
        'aws-pytest-compare.json',
    }

    return res


def validation_map(index=None):
    """Returns validation map for TMP Migration"""
    res = [
        ## Sanity Check
        'sanity-check-cmc.json',
        'sanity-check-org.json',
        'sanity-check-org-invite.json',
        'sanity-check-ou-mapping.json',
        'sanity-check-resources.json',
        'sanity-check-users.json',
        'sanity-check-policies.json',
        'sanity-check-roles.json',
        ## Migration
        'migration-leave-org.json',
        'migration-handshake.json',
        'migration-move-to-ou.json',
        ## reshare & reconfig
        'waf-backup.json',
        'waf-reconfig-phase-1.json',
        'waf-reconfig-phase-2.json',
        'waf-reconfig-phase-3.json',
        'reshare-ram.json',
        ## Pre/Post Outcome
        'network-connectivity.json',   # may move to build.finally before validation
        'aws-pytest-compare.json',     # Moved to build.finally before validation
        'vgw-check.json',

        ## Files generated by pre-migration
        'pre-pytests-result.json',
        'pre-network-connectivity.json',
    ]

    return res


## Data Management


def get_uuid():
    """Returns uuid4"""
    return str(uuid.uuid4())


def get_uuid_url(url):
    """Return UUID for given url"""
    return str(uuid.uuid3(uuid.NAMESPACE_URL, url))


def correct_capitalization(string):
    """Returns correct capilatiziation of given string or sentence"""
    string_arr = string.split(' ')
    res = []
    svcs = [
        'API', 'AWS', 'BGP', 'CloudTrail', 'CloudWatch', 'CMC', 'CodeBuild', 'DevOps', 'DevOps', 
        'DevSecOps', 'DHCP', 'DNS', 'DynamoDB', 'EBS', 'EC2', 'EC2', 'ECR', 'ECS', 'EFS', 
        'EventBridge', 'GE', 'GR-Limited', 'GR-Standard', 'GR-2', 'HealthCare', 'IAM', 'IATL', 'IDP', 'IDPs', 
        'IPV4', 'IPV6', 'KMS', 'MFA', 'MFA', 'NAT', 'NAT', 'NFW', 'OU', 'RAM', 'SAML', 
        'SecDevOps', 'SecOps', 'SecretManager', 'TGW', 'VGW', 'VM', 'WAF', 'ElastiCache',
        'EMR', 'GuardDuty', 'RDS', 'VPN', 'vWAN', 'WAN', 'CIRT', 'BU', 'SKU', 'DNS', 'CT', 
        'vNet', 'TM', 'FlowLogs', 'TMP', 'MMP', 
    ]
    for rs in string_arr:
        tr = rs
        for svc in svcs:
            if rs.lower() == svc.lower():
                tr = svc
        
        res.append(tr)

    return ' '.join(res)


def cmc_json_csv(data):
    """Returns CMC normalized data with no missing keys for pre-selection of keys"""
    keys = ['provision_date', 'status', 'suspended_date', 'subtype', 'account_id', 'vendor', 'business_unit', 'account_name', 'owner', 'migration_date', 'sku', 'connected_region', 'owners', 'ejected_date', 'pop_locations']
    res = []

    res.append(keys)
    for rs in data:
        row = []
        for col in keys:
            val = rs[col] if col in rs else ''
            row.append(val)
        res.append(row)

    return res


def csv_json(data):
    """Returns python list of each csv line assuming each csv lines is a list of given data"""
    res = []
    keys = data[0]
    for i, rs in enumerate(data):
        row = {}
        for j, r in enumerate(rs):
            # print(f'{keys[j]}: {r}')
            row[keys[j]] = r
        res.append(row)

    return res


def find_after(char, needle):
    """Returns form needle to the end of given char

    Args:
        char (str): Heystack to search for
        needle (str): needle string to match everything to the end

    """
    res = str(char)
    try:
        leftIndex = res.index(needle) + len(needle)
        return res[leftIndex:]
    except Exception as err:
        return char


def find_between(char, left='(', right=')'):
    """Returns first occurance of string between to gives boundaries or char if not found

    Args:
        char (str): Heystack to search for
        left (str): left string to find a match
        right (str): right string to find a match

    """
    res = str(char)
    try:
        leftIndex = res.index(left) + len(left)
        rightIndex = res.index(right, leftIndex)
        # Return if exist
        return res[leftIndex:rightIndex]
    except Exception as err:
        # Return Original if not exist
        return char


def format_aws_acc(acc):
    """Returns nnnn-nnnn-nnnn"""
    acc = str(acc)
    res = ''
    for i in range(0, len(acc), 4):
        chars = acc[i:i+4]
        res += chars if not res else '-'+chars
    return res


def get_dict_item(data: dict, index: int):
    """Returns dict item by its index or {} if not found!"""
    try:
        rs = list(data.items())[index]
        return {rs[0]: rs[1]}
    except Exception as err:
        iWarning('utl.get_dict_item error:', err)
        return {}


def get_dict_item_len(data: dict, index: int):
    try:
        rs = list(data.items())[index]
        return len(rs[1])
    except Exception as err:
        iWarning('utl.get_dict_item_len error:', err)
        return 0


def typeof(obj, check_type=None):
    """Returns true or false if object type is match with check 
    
    Args:
        obj (any): object to check its types
        check_type (str): any valid type
    """
    obj_type = find_between(type(obj), "'", "'")

    if not check_type:
        return obj_type

    return True if obj_type == check_type else False


def url_sep(url):
    """Returns urls separator of ? or &

    Args:
        url (str): an URL

    Returns:
        url? : if no parameter in url
        url& : if there is any parameter url
    """
    return url + ( '&' if '?' in url else '?' )


def ffname(string):
    """Returns safe filename"""
    res = string.lower()
    sReplace = ['  ', ' ', '!', '/', '--']  # Replace these with '_'
    for r in sReplace:
        res = res.replace(r, '-')
    return res


def sort_dict(aDict: dict) -> dict:
    """Returns sorted dictionary"""
    keys = list(aDict.keys())
    keys.sort()
    return {i: aDict[i] for i in keys}


def sort_list_dict_by_key(aList, key):
    """Return sorted list by dictionary values of key"""
    return sorted(aList, key=lambda d: d[key])

## AWS Util


def filter_dict_arr(rSet:list | dict, rKey:None | str=None, Key:None | str=None, Vals:list=[]):
    """Returns filtered list of dictionaries

    Args:
        rSet (list):        Data list of dictionaries
        rKey (None|str):    List key. If input is a dictionary this is the key of desired list
        Key (None|str):     Dictionary key to filter
        Vals (None|list):   Dictionary value to match

    Returns list
    """
    if Key is None or len(Vals) == 0:
        return rSet
    rss = rSet if rKey is None else rSet[rKey]
    res = []
    for rs in rss:
        if Key in rs:
            for val in Vals:
                if val in rs[Key]:
                    res.append(rs)

    return res if rKey is None else {rKey: res}

def get_region_location(region=None):
    """Returns AWS Region name, region or dictionary as of 21-Apr-2023

    Args:
        region (str): Region region.
            If provided & is in below dictonary returns region name
            If provided & is not in below dictonary returns provided region
            If not provided returns below dictonary
    """
    rs = {
        'af-south-1': 'Africa (Cape Town)',
        'ap-east-1': 'Asia Pacific (Hong Kong)',
        'ap-northeast-1': 'Asia Pacific (Tokyo)',
        'ap-northeast-2': 'Asia Pacific (Seoul)',
        'ap-northeast-3': 'Asia Pacific (Osaka)',
        'ap-south-1': 'Asia Pacific (Mumbai)',
        'ap-south-2': 'Asia Pacific (Hyderabad)',
        'ap-southeast-1': 'Asia Pacific (Singapore)',
        'ap-southeast-2': 'Asia Pacific (Sydney)',
        'ap-southeast-3': 'Asia Pacific (Jakarta)',
        'ap-southeast-4': 'Asia Pacific (Melbourne)',
        'ap-southeast-5': 'Asia Pacific (Malaysia)',
        'ca-central-1': 'Canada (Central)',
        'ca-west-1': 'Canada (Calgary)',
        'eu-central-1': 'Europe (Frankfurt)',
        'eu-central-2': 'Europe (Zurich)',
        'eu-north-1': 'Europe (Stockholm)',
        'eu-south-1': 'Europe (Milan)',
        'eu-south-2': 'Europe (Spain)',
        'eu-west-1': 'Europe (Ireland)',
        'eu-west-2': 'Europe (London)',
        'eu-west-3': 'Europe (Paris)',
        'il-central-1': 'Israel (Tel Aviv)',
        'me-central-1': 'Middle East (UAE)',
        'me-south-1': 'Middle East (Bahrain)',
        'sa-east-1': 'South America (São Paulo)',
        'us-east-1': 'US East (N. Virginia)',
        'us-east-2': 'US East (Ohio)',
        'us-west-1': 'US West (N. California)',
        'us-west-2': 'US West (Oregon)',
        'us-gov-east-1': 'AWS GovCloud (US-East)',
        'us-gov-west-1': 'AWS GovCloud (US-West)',
    }
    if region and region in rs:
        return rs[region]
    if region and region not in rs:
        # if region not found return the region
        return region
    
    return rs

def get_region_fmt(region, wide: bool=False):
    """Return formated region region_location
    
    Args:
        wide (bool): if True format all region & location to the same width with emptay space in the middle
    """

    if wide:
        return f"{iColor(rspace(get_region_location(region), 25), 'Gray')} {iColor(lspace(region, 14), 'iYellow')}"
   
    return f"{get_region_location(region)} {region}"

def aws_iam_action(svc, methods=None):
    """Returns IAM Action from boto or cli

    Args: Single Service Call
        svc (str): AWS Service Name. ex: ram

    methods (list): AWS Service call methods. ex:
        ['associate_resource_share', 'create_permission', 'create_resource_share']

    Args: Multiple Services Call
        svc (list): A list of dictionaries of AWS Service Name & mehods. ex:
        [
            {
                'service': 'ram',
                'methods': ['associate_resource_share', 'create_permission', 'create_resource_share']
            },
            {
                'service': '...', # next service
                'methods': [...]   # next service used methodes
            }
        ]

    """

    res = {'Action': []}
    rs = []

    if isinstance(svc, list):
        rs = svc
    elif isinstance(svc, str) and isinstance(methods, list):
        rs.append( {'service': svc, 'methods': methods} )
    else:
        sysExit('util / aws_iam_action / Invalid input!')

    try:
        for r in rs:
            svc = r['service'].lower()
            for method in r['methods']:
                string = method.replace('-', ' ').replace('_', ' ').title().replace(' ', '')
                res['Action'].append(f'{svc}:{string}')
    except Exception as err:
        iError('util / aws_iam_action / Invalid input!', err)
        return res

    res['Action'].sort()
    print(pretty_yaml(res))

    return res


def upload_file_to_s3(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    Args:
        file_name (str): File to upload
        bucket (str): Bucket to upload to
        object_name (str): S3 object name. If not specified then file_name is used

    Return:
        True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as err:
        iError(err)
        return False
    return True


## Time, Cache & Session


def get_dt():
    """Returns UTC datetime in ISO format - 2023-12-30T16:26:35.054030+00:00"""
    return datetime.now(timezone.utc).isoformat()


def get_dt4file():
    """Returns UTC microsecond datetime to use in filename
    Given   : 2023-12-30T16:26:35.054030+00:00
    Returns : 2023-12-30T16-26-35.054030

    """
    res = get_dt()[0:26]
    res = res.replace(':', '-')

    return res


def get_dt_local():
    """Returns datetime in ISO format"""
    return datetime.now().isoformat()


def iso8601Time() -> str:
    """Returns UTC datetime in ISO 8601 format"""
    return datetime.now(timezone.utc).isoformat()


def excel2date(date_int=None):
    """Returns excel date of given arg

    Args:
        date_int (int): excel date as nnnnn
    """
    res = ''

    today = get_dt()
    iTrace('today :', today)
    today_excel = date2excel(today)
    days_offset = date_int - 2 - today_excel

    iTrace('today_excel :', today_excel)

    # Excel considers 1900 as a leap year because of lotus 1-2-3 bug also 1900-1-1 is day 1 not zero
    res = get_tdelta(today, days=days_offset)   # excel date is days from 1900-1-1 with +2 days or +1 day for 1900

    return res


def date2excel(date_str=None):
    """Returns days since 1900-1-1 2+ days to fix excel bug

    Args:
        date_str (None | Str): Today if None or format as yyyy-mm-dd
    """
    res = ''
    offset = 2

    today = date.today()
    if date_str:
        date_str = date_str.replace('T', '-')
        date_arr = date_str.split('-')
        year = int( date_arr[0] )
        if year == 1900:
            offset = 1

        month = int( date_arr[1] )
        day = int( date_arr[2] )
        today = date( year, month, day )

    iTrace('today :', today)

    delta = date( 1900, 1, 1 )
    iTrace('delta :', delta )

    # Excel considers 1900 as a leap year because of lotus 1-2-3 bug also 1900-1-1 is day 1 not zero
    res = (today - delta).days + offset  # excel date is days from 1900-1-1 with +2 days or +1 day for 1900

    return res


def get_today():
    """Returns today in yyyy-mm-dd format"""
    return date.today()

def get_todayfmt():
    """Return today date formated as 'dd-mmm-yyyy'"""
    return get_today().strftime("%d-%b-%Y")

def get_tdelta(now_date, **kwargs):
    """Returns isformat new_date of now_date and valid **kwargs for given timedelta

    Usage:
        get_tdelta(now_date, days=1)        # Tommorow 
        get_tdelta(now_date, days=-1)       # Yesterday
        get_tdelta(now_date, hours=24)      # Next 24 hours
        get_tdelta(now_date, hours=-24)     # Past 24 Hours

    Genral Format:
        get_tdelta(now_date 
            [,weeks=int]
            [,days=int]
            [,hours=int]
            [,minutes=int]
            [,seconds=int]
            [,milliseconds=int]
            [,microseconds=int]
        )

    Args:
        weeks         (int): optional
        days          (int): optional
        hours         (int): optional
        minutes       (int): optional
        seconds       (int): optional
        milliseconds  (int): optional
        microseconds  (int): optional
    """

    days = kwargs.get('days', 0)
    seconds = kwargs.get('seconds', 0)
    microseconds = kwargs.get('microseconds', 0)
    milliseconds = kwargs.get('milliseconds', 0)
    minutes = kwargs.get('minutes', 0)
    hours = kwargs.get('hours', 0)
    weeks = kwargs.get('weeks', 0)

    try:
        new_date = datetime.fromisoformat(now_date) + timedelta(
            days=days,                  # type: ignore
            seconds=seconds,            # type: ignore
            microseconds=microseconds,  # type: ignore
            milliseconds=milliseconds,  # type: ignore
            minutes=minutes,            # type: ignore
            hours=hours,                # type: ignore
            weeks=weeks                 # type: ignore
        )
        return new_date.isoformat()
    except Exception as err:
        iError('util.get_tdelta', err)


def date_string(dt):
    """Returns string of given datetime without -T+: charachters"""
    dt = str(dt)
    dtReplace = [' ', '-', 'T', '+', ':']  # Replace these with ''
    for r in dtReplace:
        dt = dt.replace(r, '')

    return dt


def get_dt2ts(dt, decimal=0):
    """Returns timestamp of given isoformat datetime

    Args:
        dt (isoformat datetime): datetime
        decimal (int): decimal point of return timestamp, default 0
    """
    ts = datetime.fromisoformat( dt )
    ts = ts.replace(tzinfo=timezone.utc)
    ts = ts.timestamp()
    ts = ts * 1000
    ts = float(format(ts, f'.{decimal}f'))

    return float(format(ts, f'.{decimal}f')) if decimal != 0 else int(ts)


def get_creds(acc, role='cs/p-engineering', quite=False):
    """Returns AWS credentials

    Args:
        acc (str): 12 digits AWS account id
        role (str): deired role to assume, default cs/p-engineering
    """

    role_arn = f"arn:{awsPartition()}:iam::{acc}:role/{role}"

    sess_name = f'boto3sts@{acc}'
    safe_sess = safe_sess_name(sess_name)
    creds = None

    try:
        sts = boto3.client('sts')
        creds = sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName=safe_sess,
            DurationSeconds=3600)['Credentials']
        iInfo(f'Assuming STS Role {role_arn}')
    except Exception as err:
        # On error try to flip the role 
        if role == 'cs/p-engineering':
            role_arn = f"arn:{awsPartition()}:iam::{acc}:role/cs/p-support"
        if role == 'cs/p-support':
            role_arn = f"arn:{awsPartition()}:iam::{acc}:role/cs/p-engineering"
        try:
            sts = boto3.client('sts')
            creds = sts.assume_role(
                RoleArn=role_arn,
                RoleSessionName=safe_sess,
                DurationSeconds=3600)['Credentials']
            iInfo(f'Assuming STS Role {role_arn}')
        except Exception as err:
            if not quite:
                iWarning(f'AccessDenied Assuming STS Role {role_arn}. Error: {str(err.response)}')  # type: ignore

    return creds


def safe_sess_name(name, size=20):
    """Returns AWS safe session name from given name"""
    res = name
    size -= 1
    # regex: [\w+=,.@-]*
    chars_filter = ' :~`!#$%^&*()_;:"\\|][}{<>?}]"'+"'"
    unsafe_chars = [*chars_filter]
    unsafe_chars.append('---')
    unsafe_chars.append('--')

    for c in unsafe_chars:
        res = res.replace(c, '-')

    iTrace('Session name:', name)
    iTrace('Safe Sess Name', res[0:size])

    return res[0:size]


def get_session(acc, dont_quit=True, role='cs/p-engineering', region_name=None, quite=False):
    """Returns session"""
    session = None
    if acc == '589623221417':  # 589623221417 [geadmin] Corporate CoreTech
        profiles = ['589623221417/p-support', '589623221417/p-engineering', 'geadmin-jump', 'geadmin', 'GEAdmin']
        for profile in profiles:
            try:
                if region_name:
                    session = boto3.session.Session(profile_name=profile, region_name=region_name)  # type: ignore
                else:
                    session = boto3.session.Session(profile_name=profile)  # type: ignore
                iTrace(f"Session established to {acc} [profile]")
                break
            except Exception as err:
                if quite:
                    return session
                if not dont_quit and profile == profiles[-1]:
                    iAbort(f"Session Failed to {acc} [profile]. Error: {str(err)}")
                if dont_quit and profile == profiles[-1]:
                    iWarning(f"Session Failed to {acc} [profile]. Error: {str(err)}")

    if acc == '020202940623':  # 020202940623 [gov-geadmin] Corporate CoreTech
        profiles = ['020202940623/p-support', '020202940623/p-engineering', 'Gov-GeAdmin', 'Gov-GEAdmin']
        for profile in profiles:
            try:
                if region_name:
                    session = boto3.session.Session(profile_name=profile, region_name=region_name)  # type: ignore
                else:
                    session = boto3.session.Session(profile_name=profile)  # type: ignore
                iTrace(f"Session established to {acc} [profile]")
                break
            except Exception as err:
                if quite:
                    return session
                if not dont_quit and profile == profiles[-1]:
                    iAbort(f"Session Failed to {acc} [profile]. Error: {str(err)}")
                if dont_quit and profile == profiles[-1]:
                    iWarning(f"Session Failed to {acc} [profile]. Error: {str(err)}")

        return session

    creds = get_creds(acc, role=role, quite=quite)
    if creds:
        try:
            session = boto3.Session(
                aws_access_key_id=creds['AccessKeyId'],
                aws_secret_access_key=creds['SecretAccessKey'],
                aws_session_token=creds['SessionToken']
            )
            iTrace(f"Session established to {str(acc)} [credentials]")
        except Exception as err:
            if quite:
                pass
            if not dont_quit:
                iAbort(f"Session Failed to {str(acc)} [credentials]. Error: {str(err)}")
            else:
                iWarning(f"Session Failed to {str(acc)} [credentials]. Error: {str(err)}")
    elif not quite:
        if not dont_quit:
            iAbort(f"Session Failed to {str(acc)} [credentials]. Error: creds is {creds}")
        else:
            iWarning(f"Session Failed to {str(acc)} [credentials]. Error: creds is {creds}")

    return session

## File Cache


def cache_file(cName):
    """Returns cache file name for given name which should be filename safe"""
    cPath = os.environ.get('CACHE_PATH', cur_dir()['Path'] + '/__cache__')
    iTrace('utils.cache_file::cPath:', cPath)

    mk_folder(cPath)

    cFile = f'{cPath}/__cache__{cName}.json'
    iTrace('utils.cache_file::cFile:', cFile)

    return cFile


def cache_ttl_fmt(ttl: int):
    """Returns cache ttl format as hh:mm:ss

    Args:
        ttl (float): cache ttl in seconds
    """
    return str(timedelta(seconds=ttl))


def delete_cache(cName):
    """Deletes cache file by its name if exists"""
    cFile = cache_file(cName)

    if os.path.isfile(cFile):
        os.remove(cFile)

    return os.path.isfile(cFile)


def delete_expired_cache():
    """Deletes expired cache files"""
    res = []
    rss = list_cache()

    for rs in rss:
        if rs['Expired']:
            delete_cache(rs['Name'])
            res.append(rs['Name'])

    return res


def get_cache(cName, fullData: bool = False, meta=None):
    """Returns cache by its name, Noe if expired or not exists

    Args:
        cName (str): filename safe cache name
        fullData (bool): returns cache object if True else cache data
    """
    cFile = cache_file(cName)
    if not isFile(cFile):
        return None

    try:
        cData = get_json(cFile)

        if get_ts() > float(cData['Expiration']):
            iWarning('Cache expired!')
            return None

        iTrace(f'utils.get_cache Success. Name: {cName}')
        if not cData['Data']:
            iWarning(f'utils.get_cache empty cache object! Name: {cName}, meta: {meta}')
        return cData if fullData else cData['Data']
    except Exception as err:
        iWarning(f'utils.get_cache Failed! Name: {cName}, meta: {meta}, Error:', err)
        return None


def list_cache(prefix= None, includes: list = [], excludes: list = []):
    """Returns list of cache metadata and their expiration status

    Args:
        prefix (str |  None): filter cache starts with given prefix, default None
        includes (list): include cache that contain one string in this list 
        excludes (list): exclude cache that contain one string in this list 

    Process Order: prefix, includes, excludes
    """
    cKey = '__cache__'
    CACHE_PATH = CACHE_PATH if CACHE_PATH else cur_dir()['Path'] + '/' + cKey
    cPath = CACHE_PATH

    rss = get_dir(cPath, '/*.json')

    res = []
    for cFile in rss['Files']:
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

    return res


def cache_ts2dt(ts):
    """Convert ts expiration to dt"""
    return datetime.fromtimestamp(ts)


def set_cache(cName, cData, ttl: int=CACHE_TTL, meta: dict={}):
    """Sets cache with default 24h TTL

    Args:
        cName (str): cache name
        cData (any): cache data
        ttl (int): time to leave in seconds
    """
    cFile = cache_file(cName)

    cExpire = get_ts() + ttl
    jData = {
        'Name': cName,
        'Created': datetime.now(),
        'Expiration': cExpire,
        'Meta': meta,
        'Type': typeof(cData),
        'Size': len(cData),
        'TTL': ttl,
        'Data': cData
    }

    try:
        put_json(cFile, jData)
        iTrace(f'utils.set_cache Success. name: {cName}')
        return True
    except Exception as err:
        iError(f'utils.set_cache Failed! name: {cName}, error:', err)
        return None


def file_mtime(fPath):
    """Returns file modified time if exists or None"""
    if os.path.isfile(fPath):
        return os.path.getmtime(fPath)
    iWarning('util.file_mtime invalid path', fPath)
    return None


def file_mtime_after(fPath, ts):
    """Returns True if file modified date is after given timestamp"""
    if os.path.isfile(fPath):
        fts = os.path.getmtime(fPath)
        if fts > float(ts):
            return True
        if fts < float(ts):
            return False
    iWarning('util.file_mtime_after invalid path', fPath)
    return False


def file_mtime_before(fPath, ts):
    """Returns True if file modified date is before given timestamp"""
    if os.path.isfile(fPath):
        fts = os.path.getmtime(fPath)
        if fts < float(ts):
            return True
        if fts > float(ts):
            return False
    iWarning('util.file_mtime_before invalid path', fPath)
    return False


def decimal(num, digits=3):
    """Return int with digits decimal points"""
    return float(format(num, f'.{digits}f'))


def get_ts():
    """Returns EPOCH timestamp"""
    return datetime.timestamp(datetime.now())


def ts2dt(ts):
    """Returns datetime of gives timestamp"""
    return datetime.fromtimestamp(ts)


def dt2ts(dt):
    """Returns timestamp of given datetime"""
    return datetime.timestamp(dt)


def fmt_ts(ts, digits=6):
    """Returns n digits decimal points - default microseconds - 6"""
    return float(format(ts, f'.{digits}f'))


def rand(start=1, stop=1, step=1):
    """Returns ranndom number by rand(start) or rand(start, stop[, step])"""
    if stop == 1 and start != 1:
        stop = start
    return random.randrange(start=start, stop=stop, step=step)


def took_ts(ts):
    """Returns duration from input ts with 6 digit percision in seconds
    
    Args:

        ts (float): timestamp which was created earlier by calling get_ts()
    """
    return float(format(get_ts()-ts, '.6f'))


def took_ts_hms(ts):
    """Returns duration from input ts as hh:mm:ss

    Args:
        ts (float): timestamp which was created earlier by calling get_ts()
    """
    return str(timedelta(seconds=get_ts()-ts))


def get_ou_mapping_file(prefix=None):
    """Returns ou mapping fiel name to use same hardcoded filename with optional prefix"""
    res = 'ou-mapping.json' if prefix is None else prefix+'/ou-mapping.json'
    return res.replace('//', '/')


def get_ou_mapping_pair(key, prefix=None):
    """Returns source & target key from move_map

    Args:
        key (str): account|org|root_id|ou_name|ou_id

    Returns:
        source[key], target[key]

    """
    jData = get_json(get_ou_mapping_file(prefix))
    source_key = target_key = ''
    try:
        source_key = jData['source'].get(key)
        target_key = jData['target'].get(key)
        return source_key, target_key
    except Exception as err:
        iWarning(f'Key {key} not found in source or target org!', err)

    return source_key, target_key

## Org Util - Migration


class OrgMap:
    OU_FILE = ''
    OU_OBJ = {}
    OU_MAP = {}

    def __init__(self, ou_file) -> None:
        """Sets OU file
        Args:
            ou_file (str): Org OU Yaml File + ROOT

            **kargs:
                ou_name (str): Source OU Name (Full Path)
                ou_id   (str): Source OU ID
        """
        # OU Processing
        self.OU_FILE = ou_file
        self.OU_OBJ = self._get_yaml(ou_file)
        self.OU_MAP = self._build_ou_map(self.OU_OBJ)

    def get_map(self):
        """Returns ou map"""
        return self.OU_MAP

    def ou_count(self):
        """Returns ou count"""
        return len(self.OU_MAP.items())

    def _get_yaml(self, my_file):
        """Returns yaml file as python object"""
        try:
            with open(my_file, 'r') as file:
                my_data = yaml.safe_load(file)
            return my_data
        except Exception as err:
            iError(err)

    def _build_ou_map(self, ou_obj):
        """Builds ou map"""
        ou_map = { }
        try:
            for ou in ou_obj:
                rs = ou_obj[ou]
                for k in rs.keys():
                    if rs['ou_name'] == 'ROOT':
                        if rs['id'] not in ou_map:
                            ou_map[rs['id']] = rs['ou_name']
                            # print(f"({rs['id']})  '/' ")
                    else:
                        sep = '' if rs['parent_name'] == '/' else '/'  # ROOT already has /
                        key = rs['parent_name'] + sep + rs['ou_name']
                        if rs['id'] not in ou_map:
                            ou_map[rs['id']] = key
                            # print(f"({rs['id']})   {key} ")
        except Exception as err:
            iError(err)
        return ou_map


class OrgUtil:
    SRC_OU_FILE = ''
    SRC_OU_OBJ = {}
    SRC_OU_MAP = {}

    DES_OU_FILE = ''
    DES_OU_OBJ = {}
    DES_OU_MAP = {}

    OU_MAP = {}

    def __init__(self, src_ou_file, des_ou_file, **kwargs) -> None:
        """Sets Source OU & Destionation OU
        Args:
            src_ou_file (str): Source Org OU Yaml File + ROOT
            des_ou_file (str): Destination Org OU Yaml File + ROOT

            **kargs:
                ou_name (str): Source OU Name (Full Path)
                ou_id   (str): Source OU ID
        """
        # Source OU Processing
        # ou files should be names as: ous.org.yaml
        self.SRC_OU_FILE = src_ou_file
        self.SRC_OU_OBJ = self._get_yaml(src_ou_file)
        self.SRC_OU_MAP = self._build_ou_map(self.SRC_OU_OBJ)

        # Destination Data Processing
        self.DES_OU_FILE = des_ou_file
        self.DES_OU_OBJ = self._get_yaml(des_ou_file)
        self.DES_OU_MAP = self._build_ou_map(self.DES_OU_OBJ)

        ou_name = ou_id = ''
        if 'ou_name' in kwargs:
            ou_id = self.get_src_ou_id(kwargs['ou_name'])
            ou_name = kwargs['ou_name']

        if 'ou_id' in kwargs:
            ou_id = kwargs['ou_id']
            ou_name = self.get_src_ou_name(kwargs['ou_id'])

        if not ( 'ou_id' in kwargs or 'ou_name' in kwargs ):
            iAbort('At least one kwargs varibale required. Either "ou_id" or "ou_name" full path for Destination Org')

        src_root_id = self.get_src_ou_id('/')
        source = {
            'org': self._get_org(src_ou_file),
            'root_id': self.get_src_ou_id('/'),
            'root_name': self.get_src_ou_name(src_root_id),
            'ou_name': self.get_src_ou_name(ou_id),
            'ou_id': self.get_src_ou_id(ou_name)
        }

        des_root_id = self.get_des_ou_id('/')
        des_root_name = self.get_des_ou_name(des_root_id)
        des_ou_id = self.get_des_ou_id(ou_name)         # same name as source ou_name
        des_ou_name = self.get_des_ou_name(des_ou_id)  # verify target has the same ou_name

        target = {
            'org': self._get_org(des_ou_file),
            'root_id': des_root_id,
            'root_name': des_root_name,
            'ou_name': des_ou_name,
            'ou_id': des_ou_id
        }

        # Validation
        errors = {}
        for k, v in source.items():
            if not v:
                errors[f'source.{k}'] = v
        for k, v in target.items():
            if not v:
                errors[f'target.{k}'] = v
        if len(errors) == 0:
            resKey = 'move'
            resVal = {
                'from': des_root_id,
                'to': des_ou_id,
                'ou_name': des_ou_name
            }
        else:
            resKey = 'error'
            resVal = errors

        self.OU_MAP = {
            'source': source,
            'target': target,
            resKey : resVal
        }

    def get_map(self):
        """Returns ou map"""
        return self.OU_MAP

    def get_src_ou_id(self, ou_name):
        """Returns Source org OU ID or ROOT ID

        Args:
            ou_name (str):
                name of OU. Input 'ROOT' or '/' for ROOT ID
        """
        return self._get_ou_id(self.SRC_OU_MAP, ou_name)

    def get_des_ou_id(self, ou_name):
        """Returns Destination org OU ID or ROOT ID

        Args:
            ou_name (str): name of OU. Input 'ROOT' or '/' for ROOT ID
        """
        return self._get_ou_id(self.DES_OU_MAP, ou_name)

    def get_src_ou_name(self, ou_id):
        """Returns Source Org OU name"""
        return self._get_ou_name(self.SRC_OU_MAP, ou_id)

    def get_des_ou_name(self, ou_id):
        """Returns Destination Org OU name"""
        return self._get_ou_name(self.DES_OU_MAP, ou_id)

    def _get_org(self, string):
        try:
            return string.split('.')[1]
        except Exception as err:
            iError("OrgUtil / Can't determine Org", err)
            return string

    def _get_yaml(self, my_file):
        try:
            with open(my_file, 'r') as file:
                my_data = yaml.safe_load(file)
            return my_data
        except Exception as err:
            iError("OrgUtil / Unable to read expected yaml file", err)

    def _build_ou_map(self, ou_obj):
        ou_map = { }
        try:
            for ou in ou_obj:
                rs = ou_obj[ou]
                for k in rs.keys():
                    if rs['ou_name'] == 'ROOT':
                        if rs['id'] not in ou_map:
                            ou_map[rs['id']] = rs['ou_name']
                            # print(f"({rs['id']})  '/' ")
                    else:
                        sep = '' if rs['parent_name'] == '/' else '/'  # ROOT already has /
                        key = rs['parent_name'] + sep + rs['ou_name']
                        if rs['id'] not in ou_map:
                            ou_map[rs['id']] = key
                            # print(f"({rs['id']})   {key} ")
        except Exception as err:
            iError("OrgUtil / Unable to build OU Map", err)
        return ou_map

    def _get_ou_name(self, ou_map: dict, ou_id: str):
        if ou_id in ou_map:
            return ou_map[ou_id]
        else:
            return None

    def _get_ou_id(self, ou_map: dict, ou_name: str):
        if ou_name == '/' or ou_name == 'ROOT':
            ou_name = 'ROOT'
        for key, val in ou_map.items():
            if val == ou_name:
                return key
        else:
            return None

## IP Address


def cidr_info(cidr, strict=False):
    """Returns Network Info for given cidr"""
    net = ipaddress.ip_network(cidr, strict=strict)

    res = {
        'CIDR': cidr,
        'Mask': str(net.netmask),
        'FstIp': str(net[0]),
        'LstIp': str(net[-1]),
        'Count': net.num_addresses,
    }

    return res


def in_cidr(ip, cidr, strict=False):
    """Returns True if given ip is in given cidr"""
    iTrace(cidr_info(cidr=cidr))
    return ipaddress.ip_address(ip) in ipaddress.ip_network(cidr)


## Abstract Syntax Tree
class AST:
    """Generates functions, classes, methods and their arguments for a given python filename

    Args:
        filename (str): Python filename
        func_color (str): function and method color, default 'Yellow'
        args_color (str): args and kwargs color, default 'Cyan'
        docs_color (str): docstring color, default 'Green'
        class_color (str): class color, default 'Green'
        brief (bool): show brief docstring, default is True 

    Return:
        None
    """

    def __init__(self,
                 filename: str = os.path.basename(__file__),
                 func_color: str = 'Yellow',
                 args_color: str = 'Cyan',
                 docs_color: str = 'Green',
                 class_color: str = 'Green',
                 brief: bool = True
                 ):
        """Generates functions, classes, methods and their arguments for a given python filename"""

        self.filename = filename
        self.func_color = func_color
        self.args_color = args_color
        self.docs_color = docs_color
        self.class_color = class_color
        self.brief = brief

        self.sfile = filename.replace('\\', '/').split('/')[-1]
        self.node = None

        self.data = {
            'Functions': [],
            'Classes': []
        }

        try:
            with open(filename) as file:
                self.node = ast.parse(file.read())  # type: ignore

            self.functions = [n for n in self.node.body if isinstance(n, ast.FunctionDef)]  # type: ignore
            self.classes = [n for n in self.node.body if isinstance(n, ast.ClassDef)]  # type: ignore

            for function in self.functions:
                iTrace(f'Node: {function}')
                res = self._info(function)
                iTrace(f'res: {res}')

            for class_ in self.classes:
                methods_info = []
                methods = [n for n in class_.body if isinstance(n, ast.FunctionDef)]  # type: ignore

                for method in methods:
                    methods_info.append(self._info(method, isClass=True))

                self.data['Classes'].append({'Class': class_.name, 'Methods': methods_info})  # type: ignore
        except FileNotFoundError as err:
            print(f'FileNotFoundError: {err}')
        except Exception as err:
            print(f'Unexpected Error: {err}')

    def _info(self, node, isClass=False):
        """Returns dict of {function: args}"""
        args = ([arg.arg for arg in node.args.args])

        # args & kwargs
        if isDebug() and node.name in [ 'trace', 'iTrace', 'isDebug', 'iColor' ]:  # just debug for some
            try:
                tmp = ast.dump(ast.parse(node), indent=4)  # type: ignore
                print(tmp)

                print(node.args.args)
                print(node.args.vararg.arg)
                print(node.args.kwarg.arg)
            except Exception as err:
                iWarning(err)

        try:
            args.append( node.args.vararg.arg )
        except Exception as err:
            pass
        try:
            args.append( node.args.kwarg.arg )
        except Exception as err:
            pass

        args_str = ' ' + ', '.join(args) + ' ' if args else ''

        docs = self._docstring(node)
        iTrace(f"{iColor(node.name, self.func_color)}({iColor(args_str, self.args_color)}) {iColor(docs, self.class_color)}")

        res = {
            'Func': node.name,
            'Args': ', '.join(args),
            'Docs': docs
        }

        if not isClass:
            self.data['Functions'].append(res)

        return res

    def _docstring(self, node):
        """Returns docstring of given function node"""
        res = ast.get_docstring(node)  # type: ignore
        if res and self.brief:
            return res.split('\n')[0]

        return res

    def _print_func(self, data, isClass=False):
        """Prints Functions or Method data"""
        num = 2 if isClass else 1

        for i, rs in enumerate(data):
            iTrace('rs:', rs)
            iStr = lspace(i+1, 3)
            args_str = ' ' + rs.get('Args') + ' ' if rs.get('Args') else ''

            print(f"{CFG_IND*num}{iStr}. {iColor(rs['Func'], self.func_color)}({iColor(args_str, self.args_color)})", end=' ')

            if not rs['Docs']:
                print()
                continue

            if self.brief:
                print( iColor(rs['Docs'], self.docs_color) )
                continue

            docs = rs['Docs'].split('\n') if rs['Docs'] else []
            if docs:
                if len(docs) == 1:
                    print( '', iColor(rs['Docs'], self.docs_color) )
                else:
                    print()
                    for doc in docs:
                        print( CFG_IND * (num + 3), iColor(doc, self.docs_color) )
                    print()

        return

    def get_info(self):
        """Returns dict of Functions & Classes lists"""
        return self.data

    def print_info(self):
        """Prints Abstract Syntax Tree of given filename"""
        # remove path from fileneme
        path = cur_dir()['Path']
        filename = self.filename.replace(path, '')

        ast_dir = cur_dir()
        ast_dir['File'] = f'{path}/{filename}'
        ast_dir['FileName'] = filename.replace('/', '')
        ast_dir['LOGLEVEL'] = LOGLEVEL
        blue_green_dict_print(ast_dir, ': ')

        fCount = len(self.data['Functions'])
        cCount = len(self.data['Classes'])

        print()
        ppwide(f'{self.sfile} has {fCount} Functions')
        self._print_func(self.data['Functions'])

        print()
        ppwide(f'{self.sfile} has {cCount} Classes')
        for i, class_ in enumerate(self.data['Classes']):
            if i > 0:
                print()

            iStr = lspace(i+1, 3)
            print(f"{CFG_IND}{iStr}. Class {iColor(class_['Class'], self.class_color)}")
            self._print_func(class_['Methods'], isClass=True)


class Select():
    """Multi-Column slections list like bash

    Args:
        data (list): list of items in selections, required
        title (str): title for selections, default None
        header (str): header for selection, default None
        col (int): suggested columns count, default 8

    Process:
        Trying to fit given data is suggested columns count of 'col' with auto-fit for each column
        if given 'data' list doesn't fit in current terminal width then decrease the 'col' until it fits
    """

    def __init__(self) -> None:
        pass

    def print_selections(self, data: list, title= None, header= None, cols: int = 8):
        """Prints Multi-Column slections & Returns index of selected items in list

        Returns: Selection value or None (if not found) 
        """
        res = None

        data.insert(0, 'Exit')
        exitColor = 'Red'
        term_size = terminal_size()

        sep = 2
        spc = ' ' * sep
        indexLen = len(str(len(data))) + 2  # 2 spaces at left
        rsmaxLen = maxLen(data) + indexLen
        colWidth = rsmaxLen * cols
        sMap = {
            'Constants': '-----',
            'items': len(data),
            'indexLen': indexLen,
            'rsmaxLen': maxLen(data) + indexLen + 1,
            'sep': sep,  # int of how many spaces separator has
            'spc': spc,  # str of separator spaces
            'term_width': terminal_size()['columns'],
            'term_heigth': terminal_size()['lines'],
            'InitialValues': '-----',
            'colCount_ini': cols,
            'rowCount_ini': round_up(len(data)/cols),
            'width_ini': colWidth,
            'CalculatedValues': '-----',
            'colCount': cols,
            'rowCount': round_up(len(data)/cols),
            'width': colWidth,
        }
        while True:
            if colWidth > term_size['columns'] and cols > 1:
                cols -= 1
                colWidth = rsmaxLen * cols
                sMap['colCount'] = cols
                sMap['rowCount'] = round_up(len(data)/cols)
                sMap['width'] = rsmaxLen * cols
            else:
                break

        # Title
        if title is not None:
            ppwide(title, width=sMap['width'])

        # Header
        if header is not None:
            wline('-', sMap['width'])
            print(' '*4, header)
            wline('-', sMap['width'])

        # Create Multi-Col Select Data
        while True:
            lines = []
            curCol = 0
            curRow = 0
            for i, rs in enumerate(data):
                i += 1
                rs_line = f'{str(i-1).rjust(indexLen - 1)}) {rs}'.ljust(sMap['rsmaxLen'])

                # if i == 1: rs_line = iColor(rs_line, exitColor)

                curCol = round_up(i/sMap['rowCount']) - 1
                curRow = i - 1 - curCol * sMap['rowCount']
                iDebug(f'Col X Row: {lspace(curCol, 2)} x {lspace(curRow,2)}')
                if curCol == 0:
                    lines.append(rs_line)
                if curCol > 0:
                    lines[curRow] += rs_line

            # Print multi-col data
            for line in lines:
                print(line)

            # Select Input
            wline('-', sMap['width'])
            inp = input(f"{iColor('  0 or Return to Exit!', exitColor)} Select from {iColor('0', 'Yellow')} to {iColor(len(data)-1, 'Yellow')} ? ")
            if inp == '0' or inp == '':
                break
            if inp.isnumeric():
                inp = int(inp)
                if inp < len(data):
                    print(f'Selected {inp}) {data[inp]}')
                    res = data[inp]
                    break

            iWarning(f'Invalid Entry of {inp}. Enter 0 or Return to Exit!')

        if isDebug():
            blue_green_dict_print(sMap, ' : ')

        return res


def multi_thread(func, arr: list, *args, **kwargs):
    """Returns result of multi-thread exectuin of 
    
    Args:
        func (object): function to run
        arr(list): iterator 
        *args (any): any other arguments
         **kwargs (any): any other keyword arguments

    Returns list
    """
    res = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for rs in arr:
            futures.append(
                executor.submit(
                    func,
                    rs,
                    *args, **kwargs
                ) 
            )

        for future in concurrent.futures.as_completed(futures):
            try:
                data = future.result()
                if isinstance(data, list):
                    [res.append(rs) for rs in data]
                else:
                    res.append(data)

            except Exception as err:
                iWarning(f'Error in multi-thred exection of {func}!', err)

    return res


if __name__ == '__main__':
    UNITTEST = True
    rName = cur_file().title()
    ppwide(f'Utilties Fucntions / {rName}')

    cur_level = LOGLEVEL
    cur_colored = COLORED
    COLORED = True

    printll(f'Utilties Fucntions / {rName} / cur_dir()')
    ppjson(cur_dir())
    file = cur_dir()['File']

    printll(f'Utilties Fucntions / {rName} / Print Colorama Colors')
    for color in colors():
        iFunc = rspace(f'incolor( {color} )', 20)
        print(
            iFunc,
            incolor(f'Unittest {cStyle()[1]}', color, cStyle()[1]),
            incolor(f'{cStyle()[2]}', color, cStyle()[2]),
            incolor(f'{cStyle()[0]}', color, cStyle()[0]),
            incolor(f'for {color}', color, cStyle()[1]),
        )

    LOGLEVEL = cur_level
    printll(f'Utilties Fucntions / {rName} / AST')
    ast = AST(file)
    ast.print_info()

    local = get_dt_local()
    now = iso8601Time()

    next24 = get_tdelta(now, hours=24)
    past24 = get_tdelta(now, hours=-24)

    unaware_tz = iColor(' ' * 6 + 'Unaware Datetime', 'Red')
    aware_tz = iColor('ISO8601 Format & Timezone Aware Datetime', 'Green')

    AWS_REGIONS_NAMES = [
        'Asia Pacific (Hyderabad)',
        'Asia Pacific (Singapore)',
        'Asia Pacific (Sydney)',
        'Asia Pacific (Jakarta)',
        'Asia Pacific (Melbourne)',
        'Canada (Central)',
        'Europe (Frankfurt)',
        'Europe (Zurich)',
        'Europe (Stockholm)',
        'Europe (Milan)',
        'Europe (Spain)',
        'Europe (Ireland)',
        'Europe (London)',
        'Europe (Paris)',
        'Israel (Tel Aviv)',
        'Middle East (UAE)',
        'Middle East (Bahrain)',
        'South America (São Paulo)',
        'US East (N. Virginia)',
        'US East (Ohio)',
        'AWS GovCloud (US-East)',
        'AWS GovCloud (US-West)',
        'US West (N. California)',
        'US West (Oregon)',
    ]

    # print()
    # sel = Select()
    # sel.print_selections( AWS_REGIONS_NAMES, title = 'Multi-Column Selection Demo', header = 'AWS Regions Names', cols=6)

    printll(f'Utilties Fucntions / {rName} / Datetime, ISO8601 Fromat & Timezone')
    wline()
    print('Local      ', local, unaware_tz)
    print('UTC Now    ', now, aware_tz)
    print('UTC Past 24', past24, aware_tz)
    print('UTC Next 24', next24, aware_tz)
