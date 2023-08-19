# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module implements Dashboard GUI page handler.'''

import logging as lg
import traceback

from c2ng.service.base import HandlerBase


EXCELLENT_SIGNAL = -80
'''Excellent signal strength in dBm.'''

GOOD_SIGNAL = -90
'''Good signal strength in dBm.'''

FAIR_SIGNAL = -100
'''Fair signal strength in dBm.'''

POOR_SIGNAL = -110
'''Poor signal strength in dBm.'''


EXCELLENT_RTT = 40
'''Excellent RTT in milliseconds.'''

GOOD_RTT = 100
'''Good RTT in milliseconds.'''

FAIR_RTT = 200
'''Fair RTT in milliseconds.'''


def get_signal_class(signal: int) -> str:
    '''Get signal class.

    Args:
        signal: signal strength in dBm.

    Returns:
        Signal class.
    '''

    if signal >= EXCELLENT_SIGNAL:
        return 'excellent'
    elif signal >= GOOD_SIGNAL:
        return 'good'
    elif signal >= FAIR_SIGNAL:
        return 'fair'
    elif signal >= POOR_SIGNAL:
        return 'poor'
    else:
        return 'none'


def get_rtt_class(rtt: int) -> str:
    '''Get RTT class.

    Args:
        rtt: RTT in milliseconds.

    Returns:
        RTT class.
    '''

    if rtt <= EXCELLENT_RTT:
        return 'excellent'
    elif rtt <= GOOD_RTT:
        return 'good'
    elif rtt <= FAIR_RTT:
        return 'fair'
    else:
        return 'none'


class DashboardHandler(HandlerBase):
    '''Dashboard (main) GUI page handler.'''

    def get(self):
        '''GET handler.

        Renders dashboard page HTML.
        '''

        try:
            sessions = self.statsman.list_sessions()

            for session in sessions:
                if not session['AvgSignal']:
                    session['SignalClass'] = 'none'
                    session['AvgSignal'] = 'N/A'
                else:
                    session['SignalClass'] = get_signal_class(session['AvgSignal'])
                    session['AvgSignal'] = str(round(session['AvgSignal']))

                if not session['AvgRTT']:
                    session['RTTClass'] = 'none'
                    session['AvgRTT'] = 'N/A'
                else:
                    session['RTTClass'] = get_rtt_class(session['AvgRTT'])
                    session['AvgRTT'] = str(round(session['AvgRTT'], 2))

            self.render('templates/dashboard.html', sessions=sessions)

        except Exception as e:
            lg.error(f'Failed to list sessions: {e}')
            traceback.print_exc()
            self.render('templates/error.html')
