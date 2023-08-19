import logging as lg

from c2ng.service.base import HandlerBase


class DashboardHandler(HandlerBase):
    def get(self):

        try:
            sessions = self.statsman.list_sessions()
            self.render('templates/dashboard.html', sessions=sessions)

        except Exception as e:
            lg.error(f'Failed to list sessions: {e}')
            self.render('templates/error.html')
