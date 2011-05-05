import logging
from pyramid.request import Request


class AybuRequest(Request):
    dbsession = None
    dbmetadata = None

    def __init__(self, *args, **kwargs):
        super(AybuRequest, self).__init__(*args, **kwargs)
        self._log = logging.getLogger(__name__)
        self._log.debug("Created new request")
        self.add_finished_callback(self.finished_callback)

    def finished_callback(self, request):
        # clear the database session
        self._log.debug('Finished request')
        self.dbsession.remove()
