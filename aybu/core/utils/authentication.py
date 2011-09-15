#!/usr/bin/env python
# -*- coding: utf-8 -*

from paste.deploy.converters import asbool
from paste.deploy.converters import asint
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authentication import AuthTktCookieHelper
from pyramid.security import Everyone
import pyramid.security


class AuthenticationPolicy(AuthTktAuthenticationPolicy):

    def __init__(self, settings):
        self.cookie = AuthTktCookieHelper(
            settings.get('auth.secret'),
            cookie_name=settings.get('auth.token'),
            secure=asbool(settings.get('auth.secure')),
            timeout=asint(settings.get('auth.timeout')),
            reissue_time=asint(settings.get('auth.reissue_time')),
            max_age=asint(settings.get('auth.max_age')),
            path=settings.get('auth.path'))

    def authenticated_userid(self, request):
        return request.user.username if request.user else None

    def effective_principals(self, request):

        principals = [Everyone]

        if request.user:
            principals += [Authenticated, 'user:%s' % request.user.username]
            principals += ['group:%s' % g.name for g in request.user.groups]

        return principals


class Authenticated(object):

    __acl__ = [(pyramid.security.Allow,
                pyramid.security.Authenticated,
                pyramid.security.ALL_PERMISSIONS),
                pyramid.security.DENY_ALL]

    def __init__(self, request):
        pass
