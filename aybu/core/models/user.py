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

import ast
from aybu.core.models.base import Base
import collections
import crypt
import re
import requests
import urllib
import json
from logging import getLogger
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Unicode
from sqlalchemy import Table
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (relationship,
                            object_session,
                            joinedload)
from sqlalchemy.orm.exc import NoResultFound


__all__ = []
log = getLogger(__name__)
RemoteGroup = collections.namedtuple('Group', ['name'])


class RemoteUser(object):
    """ This class is used in place of the User class when
        remote API login management is used in place of local
        database """

    def __init__(self, url, username, crypted_password, cleartext_password,
                 remote, groups, verify_ssl):
        self.url = url
        self.username = username
        self.crypted_password = crypted_password
        self.cleartext_password = cleartext_password
        self._groups = groups
        self.remote = remote
        self.verify_ssl = verify_ssl

    @property
    def groups(self):
        return [RemoteGroup(name=g) for g in self._groups]

    @property
    def password(self):
        return self.crypted_password

    @password.setter
    def password(self, password):
        url = "{}/{}".format(self.remote, self.username)
        try:
            response = requests.put(
                    url,
                    auth=(self.username, self.cleartext_password),
                    data=dict(password=password),
                    verify=self.verify_ssl
            )
            response.raise_for_status()
            content = json.loads(response.content)

        except requests.exceptions.RequestException as e:
            log.critical("Error connection to API: {} - {}"\
                                                .format(type(e).__name__, e))
            raise ValueError('Cannot connect to API')

        except Exception:
            log.exception('Invalid login: %s', response.status_code)
            raise ValueError('Invalid login, upstream returned {}'\
                            .format(response.status_code))

        else:
            log.info("Updated password for %s", self.username)
            self.crypted_password = content['crypted_password']
            self.cleartext_password = password

    @classmethod
    def check(cls, request, username, password):
        remote = request.registry.settings.get('remote_login_url')
        verify_ssl = ast.literal_eval(
                        request.registry.settings.get('remote_login_ssl'))
        url = "{}/{}".format(remote, username)
        params = dict(
            domain=request.host,
            action="login"
        )
        try:
            query = "?{}".format(urllib.urlencode(params))
            query = "{}{}".format(url, query)
            log.debug("GET %s", query)
            response = requests.get(query, auth=(username, password),
                                     verify=verify_ssl)
            response.raise_for_status()
            log.debug("Response: %s", response)
            content = json.loads(response.content)

        except requests.exceptions.RequestException as e:
            log.critical("Error connection to API: {} - {}"\
                                                .format(type(e).__name__, e))
            raise ValueError('Cannot connect to API')

        except ValueError:
            log.exception("Cannot decode JSON")
            raise

        except Exception:
            log.error('Invalid login: %s', response.status_code)
            raise ValueError('Invalid login, upstream return %s',
                             response.status_code)

        else:
            return RemoteUser(url=url, username=username,
                              crypted_password=content['crypted_password'],
                              cleartext_password=password,
                              groups=content['groups'],
                              remote=remote, verify_ssl=verify_ssl)

    def has_permission(self, perm):
        return bool(set((perm, 'admin')) & set(self._groups))

    def check_password(self, password):
        if not self.cleartext_password == password:
            raise ValueError('Invalid username or password')

    def __repr__(self):
        return "<RemoteUser {}>".format(self.username)


users_groups = Table('users_groups',
                     Base.metadata,
                     Column('users_username',
                            Unicode(255),
                            ForeignKey('users.username',
                                       onupdate="cascade",
                                       ondelete="cascade")),
                     Column('groups_name',
                            Unicode(32),
                            ForeignKey('groups.name',
                                       onupdate="cascade",
                                       ondelete="cascade")),
                     mysql_engine='InnoDB')


class User(Base):

    __tablename__ = 'users'
    __table_args__ = ({'mysql_engine': 'InnoDB'})

    hash_re = re.compile(r'(\$[1,5-6]\$|\$2a\$)')
    salt = "$6$"

    username = Column(Unicode(255), primary_key=True)
    crypted_password = Column("password", Unicode(128), nullable=False)

    groups = relationship('Group', secondary=users_groups, backref='users')

    @classmethod
    def get(cls, session, pkey):
        # FIXME this should raise NoResultFound if query returns None!
        user = session.query(cls).options(joinedload('groups')).get(pkey)
        if user is None:
            raise NoResultFound("No obj with key {} in class {}"\
                                .format(pkey, cls.__name__))
        return user

    @classmethod
    def check(cls, session, username, password):
        try:
            user = cls.get(session, username)
            length = len(cls.hash_re.match(user.password).group())
            enc_password = crypt.crypt(password, user.password[0:length])
            assert user.password == enc_password

        except (AssertionError, NoResultFound):
            log.warn('Invalid login for %s', username)
            raise ValueError('invalid username or password')

        else:
            return user

    @hybrid_property
    def password(self):
        return self.crypted_password

    @password.setter
    def password(self, value):
        self.crypted_password = crypt.crypt(value, self.salt)

    def check_password(self, password):
        return self.__class__.check(object_session(self), self.username,
                                    password)

    def has_permission(self, perm):
        return bool(set((perm, 'admin')) & set(g.name for g in self.groups))

    def __repr__(self):
        return "<User {}>".format(self.username)


class Group(Base):

    __tablename__ = 'groups'
    __table_args__ = ({'mysql_engine': 'InnoDB'})

    name = Column(Unicode(32), primary_key=True)

    def __repr__(self):
        return "<Group {}>".format(self.name)
