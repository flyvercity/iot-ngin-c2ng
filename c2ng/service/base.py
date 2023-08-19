from tornado import web

from c2ng.service.backend.uss import UssInterface  # noqa
from c2ng.service.backend.mongo import Mongo  # noqa
from c2ng.service.backend.sliceman import SliceMan  # noqa
from c2ng.service.backend.secman import SecMan  # noqa
from c2ng.service.backend.influx import Influx  # noqa
from c2ng.service.backend.sessman import SessMan  # noqa
from c2ng.service.backend.statsman import StatsMan  # noqa


class HandlerBase(web.RequestHandler):
    '''Helper for accessing backend subservices.'''

    def prepare(self):
        '''Creates shortcuts to subservices.'''
        self.uss = self.settings['uss']  # type: UssInterface
        self.mongo = self.settings['mongo']  # type: Mongo
        self.sliceman = self.settings['sliceman']  # type: SliceMan
        self.secman = self.settings['secman']  # type: SecMan
        self.influx = self.settings['influx']  # type: Influx
        self.sessman = self.settings['sessman']  # type: SessMan
        self.statsman = self.settings['statsman']  # type: StatsMan
