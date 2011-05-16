import os
from pyramid.renderers import render_to_response
from pyramid.exceptions import NotFound
from webob import Response
import aybu.core.forms
from . utils import setup_template_context


def dynamic(viewinfo, request):
    templ = setup_template_context(viewinfo, request)
    return render_to_response(templ, {}, request=request)


def contacts(viewinfo, request):
    templ = setup_template_context(viewinfo, request)
    aybu.core.forms.contact(request)
    return render_to_response(templ, {}, request=request)


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

