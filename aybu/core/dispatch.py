import os
import logging
import pyramid.paster
from paste.script.util.logging_config import fileConfig

log = logging.getLogger(__name__)


def get_pylons_app(global_conf):
    pyramid_config = os.path.realpath(global_conf['__file__'])
    dir_, conf = os.path.split(pyramid_config)
    config_file = os.path.join(dir_, "pylons-%s" % (conf))
    logging.debug("Pyramid config from :%s, pylons config: %s",
                  pyramid_config, config_file)

    fileConfig(config_file)
    log.info("Loading application from %s", config_file)
    app = pyramid.paster.get_app(config_file, 'main')
    if not hasattr(app, "__name__"):
        app.__name__ = "Wrapped Pylons app"
    return app


