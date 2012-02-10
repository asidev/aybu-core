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

from aybu.core.models.base import Base
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


class RemoteUser(object):
    """ This class is used in place of the User class when
        remote API login management is used in place of local
        database """

    def __init__(self, url, username, crypted_password, groups=[]):
        self.url = url
        self.username = username
        self.crypted_password = crypted_password
        self.groups = groups

    @classmethod
    def get(cls, request, username):
        return cls(url=None, username=username, crypted_password=None,
                   groups=[])

    @property
    def password(self):
        return self.crypted_password

    @password.setter
    def password(self, password):
        raise NotImplementedError()

    @classmethod
    def check(cls, request, username, password):
        url = "{}/{}".format(
            request.registry.settings.get('remote_login_url'),
            username
        )
        params = dict(
            domain=request.host,
            action="login"
        )
        try:
            #query = "?"
            #for k, v in params.iteritems():
            #    query = "{}&{}={}".format(query, k, v)
            query = "?{}".format(urllib.urlencode(params))
            query = "{}{}".format(url, query)
            log.debug("GET %s", query)
            response = requests.get(query, auth=(username, password))
            response.raise_for_status()
            content = json.loads(response.content)

        except requests.exceptions.RequestException as e:
            log.critical("Error connection to API: {} - {}"\
                                                .format(type(e).__name__, e))
            raise ValueError('Cannot connect to API')

        except Exception:
            log.error('Invalid login: %s', response.status_code)
            raise ValueError('Invalid login, upstream return %s',
                             response.status_code)

        except ValueError:
            log.exception("Cannot decode JSON")
            raise

        else:
            return RemoteUser(url=url, username=username,
                              crypted_password=password,
                              groups=content['groups'])

    def has_permission(self, perm):
        return bool(set((perm, 'admin')) & set(self.groups))

    def check_password(self, password):
        return self.__class__.check(None, self.username, password)

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
            return True

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
