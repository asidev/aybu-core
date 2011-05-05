import os
import logging
from paste.deploy import loadapp
from paste.script.util.logging_config import fileConfig
from pyramid.wsgi import wsgiapp
from pyramid.exceptions import NotFound

log = logging.getLogger(__name__)


def get_pylons_app(global_conf):
    pyramid_config = os.path.realpath(global_conf['__file__'])
    dir_, conf = os.path.split(pyramid_config)
    config_file = os.path.join(dir_, "pylons-%s" % (conf))
    logging.debug("Pyramid config from :%s, pylons config: %s",
                  pyramid_config, config_file)

    fileConfig(config_file)
    log.info("Loading application from %s", config_file)
    app = loadapp("config:%s" % (config_file))
    if not hasattr(app, "__name__"):
        app.__name__ = "Wrapped Pylons app"
    return app


def add_fallback_to(config, app):
    notfound_view = wsgiapp(app)
    config.add_view(notfound_view, context=NotFound)

