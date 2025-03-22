#!/usr/bin/env python

from DataModels import *
from typing import Any
from util import *

'''
# Below is example of override_outcome('passed') because of retry 'passed' as last-known-good-state
{
    "duration": 12.463006,
    "outcome": "passed",
    "note": "",
    "details": [{
            "task": "move-to-ou",
            "duration": 0.096074,
            "outcome": "failed",
            "note": "Unable to move (794754909836) [add-plat-nonprod] from Root (r-y2v9) to /guardrails/guardrails-standard/aviation-guardrails-standard (ou-y2v9-ncvytsxv)",
            "timestamp": "2023-06-22T13:54:44.213343+00:00"
        }, {
            "task": "move-to-ou",
            "duration": 6.366932,
            "outcome": "passed",
            "note": "Moved to GEAV /guardrails/guardrails-standard/aviation-guardrails-standard",
            "timestamp": "2023-06-22T13:54:50.484218+00:00"
        }
    ],
    "timestamp": "2023-06-22T13:54:44.117231+00:00",
    "move_map": {
        "source": {
            "org": "gecc",
            "root_id": "r-y70b",
            "root_name": "ROOT",
            "ou_name": "/guardrails/guardrails-standard/aviation-guardrails-standard",
            "ou_id": "ou-y70b-vipkr8l7",
            "account_id": "737859062117",
            "account_name": "gecc"
        },
        "target": {
            "org": "geav",
            "root_id": "r-y2v9",
            "root_name": "ROOT",
            "ou_name": "/guardrails/guardrails-standard/aviation-guardrails-standard",
            "ou_id": "ou-y2v9-ncvytsxv",
            "account_id": "538763039462",
            "account_alias": "master-payer-av"
        },
        "move": {
            "from": "r-y2v9",
            "to": "ou-y2v9-ncvytsxv",
            "ou_name": "/guardrails/guardrails-standard/aviation-guardrails-standard"
        }
    }
}

'''

def fmt_outcome(outcome):
    """Return formated outcome in uppercase"""
    width = maxLen([ SKIPPED, FAILURE, SUCCESS, 'UNKNOWN'] )

    if outcome == SKIPPED:
        res = iColor(rspace(SKIPPED.upper(), width), 'iGray')
    elif outcome == FAILURE:
        res = iColor(rspace(FAILURE.upper(), width), 'Red')
    elif outcome == SUCCESS:
        res = iColor(rspace(SUCCESS.upper(), width), 'Green')
    else:
        res = iColor(rspace('UNKNOWN', 'Gray'), width)

    return res

class Validator:
    """Generate Validation Outcome of stage & one or more tasks
    
    Usage:
        # Init
        VAL = Validator('Test Task')

        # Add records
        VAL.put(task='Task 1', outcome='skipped', note='Task 1 Notes')
        sleep(.23)
        VAL.put(task='Task 2', outcome='skipped', note='Task 2 Notes')
        sleep(.03)
        VAL.put(task='Task 3', outcome='skipped', note='Task 3 Notes')

        # Reports
        validator_data = VAL.put_file('/tmp/test-task.json')

        # Prints
        VAL.list_failures()
        VAL.print_outcome()

    """
    def __init__(self, task: str='', note: str='') -> None:
        
        self.ts_map = []
        self.ts_map.append(get_ts())

        self.outcomes = [ SKIPPED, SUCCESS, FAILURE ]
        self.data = {
            'task': task,
            'duration': 0,
            'outcome': 'unknown',
            'note': note,
            'details': [],
            'datetime':  get_dt(),
            'timestamp': get_ts(),
        }

    def _calulate_durations(self):
        """Private method to handle parallel processing overlapped timings"""
        sorted_data = sort_list_dict_by_key(self.data['details'], 'timestamp')
        list_timestamps = []
        for rs in sorted_data:
            list_timestamps.append(rs['timestamp'])

        total_duration = 0
        for i, rs in enumerate(sorted_data):
            delta = rs['timestamp'] - sorted_data[i-1]['timestamp'] if i else 0
            total_duration += delta
            sorted_data[i]['duration'] = delta

        self.data['duration'] = total_duration
        self.data['details'] = sorted_data

    def _float_fmt(self, n, digits: int=3):
        """Private method to format given n to given digits floating point percision"""
        return float(format(n, f'.{digits}f')) if digits != 0 else n

    def _set_outcome(self, outcome: str):
        """Private method to calculate final outcome on each entry/put
        
        Args:
            outcome (str): one of 'skipped', 'passed', 'failed'

        Returns (str) of final outcomes
        """
        if outcome not in self.outcomes:
            iAbort('Invalid outcome:', outcome)

        final_outcome = self.data['outcome']
        if final_outcome == 'failed':
            pass 
        
        elif final_outcome == SKIPPED:
            self.data['outcome'] = outcome

        elif final_outcome == SUCCESS and outcome == SUCCESS:
            self.data['outcome'] = outcome

        elif final_outcome == 'unknown':
            self.data['outcome'] = outcome

        return self.data['outcome']

    def get_outcome(self):
        """Returns final outcome"""
        for detail in self.data['details']:
            if detail.get('outcome', '') == FAILURE:
                self.data['outcome'] = FAILURE

        self._calulate_durations()

        return self.data['outcome']
    
    def list_failures(self, limit: int=0):
        """Prints faliures if any up to given limit if given or all
        
        Args:
            limit (int): limit output count, default 0 no lomit
        """
        self._calulate_durations()

        rs = []
        duration = 0
        i = 0
        for detail in self.data['details']:
            if detail.get('outcome') == FAILURE:
                i += 1
                duration += detail.get('duration', 0)
                if limit and limit >= i:
                    continue

                rs.append({
                    'Duration': self._float_fmt(detail.get('duration', 0)),
                    'Outcome': detail.get('outcome', '').upper(),
                    'Note': detail.get('note', ''),
                    })

        self._calulate_durations() 
    
        dm = DataModel()
        dm.print_table(data=rs)

        print('Overall Duration:', self._float_fmt(self.data['duration']))
        print('Overall Outcome :', self.data['outcome'].upper())
        print('Overall Note    :', self.data['note'])
        print('Failure Duration:', self._float_fmt(duration))

    def print_outcome(self):
        """Prints outcomes"""
        self._calulate_durations()

        data = []
        for rs in self.data['details']:
            duration = rs.get('duration', 0)
            duration = self._float_fmt(duration)

            data.append({
                'Task': rs.get('task'),
                'Outcome': rs.get('outcome'),
                'Duration': duration,
                'Note': rs.get('note'),
            })

        self._calulate_durations()

        colors_map = {
            'Outcome': {
               f'{FAILURE}': 'iRed',
               f'{SUCCESS}': 'iGreen',
               f'{SKIPPED}': 'iGray',
               f'unknown': 'bRed', 
            }
        }    
        dm = DataModel()
        dm.print_table(data=data, colors_map=colors_map)

        print('Overall Duration:', self._float_fmt(self.data['duration']))
        print('Overall Outcome :', self.data['outcome'].upper())
        print('Overall Note    :', self.data['note'])

    def override_outcome(self, outcome: str):
        """Returns override outcome

        Purpose: in-case of retry previous failure should be considered as skipped and final outcome
            would be last-known state so we need to override the final outcome
        
        Args:
            outcome (str): one of 'skipped', 'passed', 'failed'

        Returns (str) of final outcomes
        """
        self.data['outcome'] = outcome if outcome in [ 'skipped', 'passed', 'failed' ] else 'unknown'

        return self.data['outcome']

    def put(self, task: str, outcome: str, note:str='', meta_data=None) -> dict:
        """Returns dict of given inputs
        
        Args:
            task (str): given task of current 
            outcome (str): outcome of task, one of 'skipped', 'passed', 'failed' 
            note (str): note for this task, default ''
            meta_data (Any): any other meta-data
        """

        res = {
            "task": task,
            "duration": 0,
            "outcome": outcome,
            "note": note,
            "datetime": get_dt(),
            "timestamp": get_ts(),
        }

        if meta_data:
            res['meta_data'] = meta_data

        self._set_outcome(outcome)
        self.data['details'].append(res)

        return res     

    def put_file(self, output:str) -> str:
        """Stores data in the given file
        
        Args:
            output (str): json file name 

        Returns filename
        """
        types = [ 'bak', 'dat', 'out', 'pre', 'pst', 'sum' ]
        self._calulate_durations()
        
        return self.data if put_json(output, self.data) else {}

    def validation_map(self,  path: str):
        """Returns validation map for Current Project"""
        path = path + '/out-*.json'
        res = get_dir(path)['Files']

        return res

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






