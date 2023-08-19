import logging as lg

from c2ng.service.base import HandlerBase


class DashboardHandler(HandlerBase):
    def get(self):

        try:
            sessions = self.statsman.list_sessions()

            for session in sessions:
                if not session['AvgSignal']:
                    session['AvgSignal'] = 'N/A'
                else:
                    session['AvgSignal'] = str(round(session['AvgSignal']))

                if not session['AvgRTT']:
                    session['AvgRTT'] = 'N/A'
                else:
                    session['AvgRTT'] = str(round(session['AvgRTT'], 2))

            self.render('templates/dashboard.html', sessions=sessions)

        except Exception as e:
            lg.error(f'Failed to list sessions: {e}')
            self.render('templates/error.html')
