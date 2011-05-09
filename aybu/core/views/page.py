from aybu.cms.lib.cache.proxies import SettingsCacheProxy,\
                                       MenusProxy,\
                                       LanguagesCacheProxy

from pyramid.renderers import render_to_response


def dynamic(viewinfo, request):

    nodeinfo = viewinfo.nodeinfo

    c = request.tmpl_context
    c.rendering_type = 'dynamic'
    c.node = viewinfo.node
    c.translation = nodeinfo
    c.lang = viewinfo.lang
    c.languages = LanguagesCacheProxy().enabled
    c.settings = SettingsCacheProxy()
    c.section = None
    c.page = None
    c.subsection = None
    c.menus = MenusProxy()
    c.user = False

    templ = "aybu.core:templates%s" % (viewinfo.view.fs_view_path)
    return render_to_response(templ, {}, request=request)


def static(context, request):
    raise NotImplementedError


def contacts(context, request):
    raise NotImplementedError

