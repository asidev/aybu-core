from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from aybu.core.resources import Root
from aybu.core.model import init_model
from aybu.core.request import AybuRequest


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=Root, settings=settings)
    setup_database(settings)
    config.add_static_view('static', 'aybucore:static')

    return config.make_wsgi_app()


def setup_database(settings):
    engine = engine_from_config(settings, "sqlalchemy.")
    sess, mtd = init_model(engine)
    AybuRequest.dbsession = sess
    AybuRequest.dbmetadata = mtd
    return engine


