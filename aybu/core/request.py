import logging
from pyramid.request import Request
from pyramid.i18n import get_localizer, TranslationStringFactory


class AybuRequest(Request):
    dbsession = None
    dbmetadata = None

    def __init__(self, *args, **kwargs):
        super(AybuRequest, self).__init__(*args, **kwargs)
        self._log = logging.getLogger(__name__)
        self.lang = None
        self.add_finished_callback(self.finished_callback)

        # i18n support
        # http://docs.pylonsproject.org/projects/pyramid_cookbook/dev/i18n.html
        self.localizer = get_localizer(self)
        self.translation_factory = TranslationStringFactory('aybu-core')

    def translate(self, string):
        """ This function will be exported to templates as '_' """
        return self.localizer.translate(self.translation_factory(string))

    def finished_callback(self, request):
        # clear the database session
        self.dbsession.remove()
