from aybu.core.cache.proxies import SettingsCacheProxy,\
                                       MenusProxy,\
                                       LanguagesCacheProxy
import aybu.core.forms
from pyramid.renderers import render_to_response


def setup_template_context(viewinfo, request, rendering_type='dynamic'):
    nodeinfo = viewinfo.nodeinfo

    c = request.tmpl_context
    c.rendering_type = rendering_type
    c.node = viewinfo.node
    c.translation = nodeinfo
    c.lang = viewinfo.lang
    c.languages = LanguagesCacheProxy().enabled
    c.settings = SettingsCacheProxy()
    c.menus = MenusProxy()
    c.user = False

    # TODO: remove as static pages support will go away
    c.section = None
    c.page = None
    c.subsection = None

    templ = "aybu.core:templates%s" % (viewinfo.view.fs_view_path)
    return templ


def dynamic(viewinfo, request):

    templ = setup_template_context(viewinfo, request)
    return render_to_response(templ, {}, request=request)


def contacts(viewinfo, request):
    templ = setup_template_context(viewinfo, request)
    aybu.core.forms.contact(request)
    return render_to_response(templ, {}, request=request)




