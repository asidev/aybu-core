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