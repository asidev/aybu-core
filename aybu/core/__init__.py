import logging
import pkg_resources
from pyramid.config import Configurator
from pyramid.exceptions import NotFound
from pyramid.wsgi import wsgiapp
from pyramid_beaker import session_factory_from_settings
from pyramid.settings import asbool

from sqlalchemy import engine_from_config
from sqlalchemy.ext.sqlsoup import SqlSoup

#from aybu.core.model import init_model

from aybu.core.request import AybuRequest
from aybu.core.resources import Root
from aybu.core.dispatch import get_pylons_app
from captchalib.pyramid import CaptchaView

log = logging.getLogger(__name__)

try:
    import uwsgi
except ImportError:
    log.info("AYBU Starting")
    uwsgi = None
else:
    log.info("AYBU Starting behind uWSGI")


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    log.info("Starting application")
    config = Configurator(root_factory=Root,
                          request_factory=AybuRequest,
                          settings=settings)
    config.begin()
    # Configure beaker session
    session_factory = session_factory_from_settings(settings)
    config.set_session_factory(session_factory)

    # Add fallback to old pylons application
    pylons = get_pylons_app(global_config)
    fallback_view = wsgiapp(pylons)

    # Configure caching
    if not "disable_cache" in settings or \
       not asbool(settings['disable_cache']):
        from aybu.core.cache.proxy import CacheProxy
        CacheProxy.cache_settings = {k.replace("cache.", ""): settings[k]
                                              for k in settings
                                              if k.startswith("cache.")}
    else:
        log.warn("Disabling cache globally")

    # Fallback on 404
    config.add_view(fallback_view, context=NotFound)
    # Fallback on "normal" pages in admin mode
    config.add_view(context='aybu.core.resources.ViewInfo',
                    view=fallback_view,
                    request_param='admin')
    config.add_view(context='aybu.core.resources.ContactsViewInfo',
                    view=fallback_view,
                    request_param='admin')
    config.add_view(context='aybu.core.resources.Admin',
                    view=fallback_view)

    # initialize babel
    config.add_translation_dirs('aybu.core:locale')

    setup_database(settings)
    config.include(setup_assets)
    config.include(add_subscribers)
    config.include(add_views)
    config.end()

    return config.make_wsgi_app()


def setup_database(settings):
    log.info("Setting up models")
    # FIXME: skip engine mapping as it's already been done by
    # the legacy pylons app
    #engine = engine_from_config(settings, "sqlalchemy.")
    #sess, mtd = init_model(engine)

    def _setup_model():
        from aybu.cms.model.meta import dbsession, metadata
        AybuRequest.dbsession = dbsession
        AybuRequest.dbmetadata = metadata

    if uwsgi and uwsgi.numproc > 1:
        # FIXME: when removing the fallback pylons app, we need to install the
        # postfork hook here
        #uwsgi.post_fork_hook = _setup_model
        _setup_model()
    else:
        _setup_model()


def add_subscribers(config):
    config.set_renderer_globals_factory('aybu.core.views.add_renderer_globals')


def add_views(config):
    log.info("Adding views")
    config.add_view(context='aybu.core.resources.ViewInfo',
                    view='aybu.core.views.page.dynamic')
    config.add_view(context='aybu.core.resources.ContactsViewInfo',
                    view='aybu.core.views.page.contacts')

    # Configure Captchalib
    CaptchaView.text_length = 6
    CaptchaView.text_color = None
    CaptchaView.background_color = None
    CaptchaView.background_ext_list = None
    config.add_view(context='aybu.core.resources.Captcha', name='show',
                    view=CaptchaView)


def setup_assets(config):
    """ Setup search paths for static files and for templates """

    # Use SqlSoup to access database to avoid requiring the entities to be
    # mapped, which is not the case when we are in a multiprocess environment.
    engine = engine_from_config(config.registry.settings, "sqlalchemy.")
    db = SqlSoup(engine)
    tname = db.settings.filter(db.settings.name == u'theme_name').one().value
    theme = db.theme.filter(db.theme.name == tname).one()

    log.info("Adding static view for aybu")
    config.add_static_view('static', 'aybu.core:static')

    log.info("Preparing static search path for %s", theme)

    themes_inheritance_chain = []
    themes_paths = [pkg_resources.resource_filename('aybu.core', 'templates')]
    while theme:
        themes_inheritance_chain.insert(0, theme)
        if theme.parent_name:
            theme = db.theme.filter(db.theme.name == theme.parent_name).one()
        else:
            theme = None

    for theme in themes_inheritance_chain:
        theme_static_spec = 'aybu.themes:%s/public/' % theme.name
        log.info("Adding '%s' as override for static files", theme_static_spec)
        config.override_asset(
            to_override='aybu.core:static/',
            override_with=theme_static_spec
        )
        theme_templates_spec = 'aybu.themes:%s/templates/' % theme.name
        log.info("Adding '%s' as override for templates", theme_templates_spec)
        config.override_asset(
            to_override='aybu.core:templates/',
            override_with=theme_templates_spec
        )
        theme_path = pkg_resources.\
                resource_filename('aybu.themes',
                                  '%s/templates' % (theme.name))

        log.info("Adding '%s' to mako directories", theme_path)
        themes_paths.insert(0, theme_path)

    # TODO: add instance-data!
    config.add_settings({
        'mako.directories': themes_paths,
        'mako.strict_undefined': 'true',
#        'mako.imports': 'from webhelpers.html import escape'
#        'mako.default_filters': 'escape',
    })
