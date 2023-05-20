# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''CLI Utility Functions.'''
import json
from pygments import highlight
from pygments.lexers.jsonnet import JsonnetLexer
from pygments.formatters import TerminalFormatter


def pprint(data):
    '''Pretty print json with colors'''
    json_str = json.dumps(data, indent=4, sort_keys=True)
    print(highlight(json_str, JsonnetLexer(), TerminalFormatter()))
