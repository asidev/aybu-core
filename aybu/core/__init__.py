import logging
from pyramid.config import Configurator
#from sqlalchemy import engine_from_config

from aybu.core.resources import Root
#from aybu.core.model import init_model
from aybu.core.request import AybuRequest
from aybu.core.dispatch import get_pylons_app, add_fallback_to

log = logging.getLogger(__name__)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    log.info("Starting application")
    config = Configurator(root_factory=Root,
                          request_factory=AybuRequest,
                          settings=settings)
    # Add fallback to old pylons application
    pylons = get_pylons_app(global_config)
    add_fallback_to(config, pylons)

    setup_database(settings)
    config.include(setup_assets)

    return config.make_wsgi_app()


def setup_database(settings):
    log.info("Setting up models")
    # FIXME: skip engine mapping as it's already been done by
    # the legacy pylons app
    #engine = engine_from_config(settings, "sqlalchemy.")
    #sess, mtd = init_model(engine)
    from aybu.cms.model.meta import dbsession, metadata
    AybuRequest.dbsession = dbsession
    AybuRequest.dbmetadata = metadata


def setup_assets(config):
    """ Setup search paths for static files and for templates """
    from aybu.core.model.entities import Theme, Setting
    from aybu.cms.model.meta import dbsession

    theme_name = dbsession.query(Setting.value).\
            filter(Setting.name == 'theme_name').subquery()
    theme = Theme.query.filter(Theme.name.in_(theme_name)).one()

    log.info("Adding static view for aybu")
    config.add_static_view('static', 'aybu.core:static')

    log.info("Preparing static search path for %s", theme)

    themes_path = []
    while theme:
        themes_path.insert(0, theme)
        theme = theme.parent

    for theme in themes_path:
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

    # TODO: add instance-data!


