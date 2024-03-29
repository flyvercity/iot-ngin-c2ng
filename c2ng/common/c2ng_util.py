# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''CLI Utility Functions.'''
import json
import logging as lg
import queue

from pygments import highlight
from pygments.lexers.jsonnet import JsonnetLexer
from pygments.formatters import TerminalFormatter


def pprint(data):
    '''Pretty print json with colors.

    Args:
        data: json data to print
    '''
    json_str = json.dumps(data, indent=4, sort_keys=True)
    print(highlight(json_str, JsonnetLexer(), TerminalFormatter()), flush=True)


def setup_logging(verbose=False):
    '''Setup realtime logging parameters.

    Args:
        verbose: enable verbose logging
    '''

    # Setup realtime logging
    log_que = queue.Queue(-1)
    queue_handler = lg.handlers.QueueHandler(log_que)
    log_handler = lg.StreamHandler()
    queue_listener = lg.handlers.QueueListener(log_que, log_handler)
    queue_listener.start()

    lg.basicConfig(
        level=lg.DEBUG if verbose else lg.INFO,
        format="%(asctime)s  %(message)s", handlers=[queue_handler]
    )
