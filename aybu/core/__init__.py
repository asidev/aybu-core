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

    # configure views
    config.include(add_views)

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

def add_views(config):
    config.add_static_view('static/pyramid', "aybu.core:static")

