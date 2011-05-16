from aybu.core.cache.proxies import SettingsCacheProxy,\
                                       MenusProxy,\
                                       LanguagesCacheProxy
import aybu.core.forms
from pyramid.renderers import render_to_response
from pyramid.exceptions import NotFound
import os
from webob import Response


def setup_template_context(viewinfo, request, rendering_type='dynamic'):

    c = request.tmpl_context
    c.languages = LanguagesCacheProxy().enabled
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


def dynamic(viewinfo, request):
    templ = setup_template_context(viewinfo, request)
    return render_to_response(templ, {}, request=request)


def contacts(viewinfo, request):
    templ = setup_template_context(viewinfo, request)
    aybu.core.forms.contact(request)
    return render_to_response(templ, {}, request=request)


def default_redirect(context, request):
    raise NotImplementedError


def sitemap(context, request):
    def add_content_type(request, response):
        response.content_type='text/xml'

    request.add_response_callback(add_content_type)
    setup_template_context(None, request)
    return {}


def robots(context, request):
    def add_content_type(request, response):
        response.content_type='text/plain'

    request.add_response_callback(add_content_type)
    return {}


def favicon(context, request):
    favicon = os.path.join(request.registry.settings['instance_uploads_dir'],
                           'favicon.ico')
    try:
        icon = open(favicon)
        return Response(content_type='image/x-icon', app_iter=icon)
    except IOError:
        raise NotFound()

