from pyramid.config import Configurator
from aybu.core.resources import Root

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=Root, settings=settings)
    config.add_static_view('static', 'aybucore:static')
    return config.make_wsgi_app()

