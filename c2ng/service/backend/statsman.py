# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

''' This module implements Statistics Manager.

Statistics Manager is a component of the Service, which collects and aggregates statistics from session, security and and signal data collection backends.
'''

import logging as lg

from c2ng.service.backend.sessman import SessMan
from c2ng.service.backend.influx import Influx


class StatsMan:
    '''Signal and Session Statistics Manager.'''

    def __init__(self, influx: Influx, sessman: SessMan):
        '''Constructor.

        Args:
            influx: Influx client helper.
            sessman: Session Manager.
        '''

        self._influx = influx
        self._sessman = sessman

    def get_signal_stats(self, uasid: str):
        '''Get signal statistics for a given UAS.

        Args:
            uasid: UAS identifier.

        Returns:
            List of signal statistics
        '''

        return self._influx.read(uasid, 'RSRP', 30)

    def list_sessions(self):
        '''List all sessions.

        Returns:
            JSON object::

                [
                    {
                       "UasID": "string(uasid)",
                       "AvgSignal": "float(avg_signal)",
                       "AvgRTT": "float(avg_rtt)>"
                    }
                ]
        '''

        sessions = self._sessman.list_sessions()

        for session in sessions:
            session['AvgSignal'] = self._influx.read(session['UasID'], 'RSRP', 30) or 'No Data'
            session['AvgRTT'] = self._influx.read(session['UasID'], 'RTT', 30) or 'No Data'

        return sessions
