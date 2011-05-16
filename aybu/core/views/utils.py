import logging
import aybu.core.lib.helpers
from aybu.core.cache.proxies import SettingsCacheProxy,\
                                       MenusProxy,\
                                       LanguagesCacheProxy


log = logging.getLogger(__name__)

def setup_template_context(viewinfo, request, rendering_type='dynamic'):

    c = request.tmpl_context
    c.languages_proxy = LanguagesCacheProxy()
    c.languages = c.languages_proxy.enabled
    c.settings = SettingsCacheProxy()
    c.menus = MenusProxy()
    c.user = False

    # TODO: remove as static pages support will go away
    c.section = None
    c.page = None
    c.subsection = None
    c.rendering_type = rendering_type

    if viewinfo:
        nodeinfo = viewinfo.nodeinfo
        c.node = viewinfo.node
        c.translation = nodeinfo
        c.lang = viewinfo.lang
        templ = "aybu.core:templates%s" % (viewinfo.view.fs_view_path)
        return templ

    return None


def add_renderer_globals(system):
    """ Add c and tmpl_context for compatibility with pylons 1.0 templates """
    log.debug("Adding context to template global namespace")
    r = system['request']
    # set the locale
    if r.lang:
        r._LOCALE_ = r.lang.lang

    return dict(
        c=r.tmpl_context,
        tmpl_context=r.tmpl_context,
        h=aybu.core.lib.helpers,
        helpers=aybu.core.lib.helpers,
        url=aybu.core.lib.helpers.url,
        _=r.translate,
        localizer=r.localizer
    )

