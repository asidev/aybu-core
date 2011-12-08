#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2010 Asidev s.r.l.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from aybu.core.models import Setting
import logging

__all__ = [ 'Proxy' ]


class Proxy(object):
    """ Factory class that returns the real proxy """

    def __new__(cls, request):
        if not Setting.get(request.db_session, 'proxy_enabled').value:
            return DummyProxy(request)

        return HttpCachePurgerProxy(request)


class BaseProxy(object):

    def __init__(self, request):
        session = request.db_session
        self._log = logging.getLogger("{}.{}".format(__name__,
                                                    self.__class__.__name__))
        self.hostname = request.host.split(":")[0]
        self.address = Setting.get(session, 'proxy_address')
        self.port = Setting.get(session, 'proxy_port')
        self.timeout = Setting.get(session, 'proxy_purge_timeout')

    def ban(self, paths):
        raise NotImplementedError

    def purge(self, paths):
        raise NotImplementedError

    def invalidate_static(self, subdir=None, extension=None):
        path = '^/static/'
        if subdir:
            path = "{}{}/".format(path, subdir)
        path = '{}.*'.format(path)
        if extension:
            path = '{}.{}'.format(path, extension)
        self.ban(path)

    def invalidate(self, url=None, language=None, pages=None):
        if not any((url, language, pages)):
            raise ValueError('No target for invalidate')

        if url:
            self.purge(url)
        elif language:
            if not isinstance(language, basestring):
                language = language.lang
            self.ban(r'^/{}/.*.html'.format(language))
        elif pages:
            self.ban(r'^/[a-z]{2}/.*.html')



class DummyProxy(BaseProxy):
    """ A do-nothing-proxy """

    def __init__(self, request):
        self._log = logging.getLogger("{}.{}".format(__name__,
                                                    self.__class__.__name__))

    def ban(self, paths):
        self._log.debug("Banning %s (noop)", paths)
        return

    def purge(self, paths):
        self._log.debug("Purging %s (noop)", paths)
        return


class HttpCachePurgerProxy(BaseProxy):
    """ A real-world proxy that uses httpcachepurger to
        purge urls from proxy """

    @property
    def _purger(self):
        from httpcachepurger import HTTPCachePurger
        return HTTPCachePurger(self.hostname, self.address, self.port,
                               strict=True, timeout=self.timeout)

    def ban(self, paths):
        if isinstance(paths, basestring):
            paths = [paths]
        self._purger.purge(paths)

    def purge(self, paths=None):
        self._log.warning('{}.purge is currently implemented as a ban'\
                         .format(self.__class__.name__))
        return self.ban(paths)
