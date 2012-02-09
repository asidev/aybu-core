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
from pyramid.authentication import SessionAuthenticationPolicy
import pyramid.security


class AuthenticationPolicy(SessionAuthenticationPolicy):
    prefix = 'auth.'

    def __init__(self):
        super(AuthenticationPolicy, self).__init__(prefix=self.prefix,
                                                   callback=self.get_groups)

    @classmethod
    def get_groups(cls, userid, request):
        return [group.name for group in request.user.groups]

    def remember(self, request, principal, **kw):
        super(AuthenticationPolicy, self).remember(request, principal, **kw)
        request.session.save()

    def forget(self, request):
        super(AuthenticationPolicy, self).forget(request)
        request.session.delete()


class Authenticated(object):

    __acl__ = [(pyramid.security.Allow,
                pyramid.security.Authenticated,
                pyramid.security.ALL_PERMISSIONS),
               pyramid.security.DENY_ALL]

    def __init__(self, request):
        pass
