import logging
from aybu.core.resources import ViewInfo, ContactsViewInfo
import aybu.core.lib.helpers

log = logging.getLogger(__name__)


def add_renderer_globals(system):
    """ Add c and tmpl_context for compatibility with pylons 1.0 templates """
    log.debug("Adding context to template global namespace")
    r = system['request']
    return dict(
        c=r.tmpl_context,
        tmpl_context=r.tmpl_context,
        h=aybu.core.lib.helpers,
        helpers=aybu.core.lib.helpers,
        url=aybu.core.lib.helpers.url,
        _=r.translate,
        localizer=r.localizer
    )


def add_views(config):
    log.info("Adding views")
    config.add_view(context=ViewInfo, view='aybu.core.views.page.dynamic')
    config.add_view(context=ContactsViewInfo, view='aybu.core.views.page.contacts')


