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

from sqlalchemy import (Column,
                        Unicode,
                        Boolean)
from sqlalchemy.orm.session import object_session
import logging
import os
import shutil
import PIL.Image

from aybu.core.models.base import Base
from aybu.core.models.translation import PageInfo
from aybu.core.exc import ConstraintError
from pufferfish import FileSystemEntity


__all__ = ['File', 'Image', 'Banner']
log = logging.getLogger(__name__)


class File(FileSystemEntity, Base):
    """
        Simple class that keeps the file on disk.
    """

    __tablename__ = 'files'
    __table_args__ = ({'mysql_engine': 'InnoDB'})
    discriminator = Column('row_type', Unicode(50))
    __mapper_args__ = {'polymorphic_on': discriminator}

    def get_ref_pages(self, session=None):
        """ Return all translations that have this file in its relation """
        if session is None:
            session = object_session(self)
        attr = getattr(PageInfo, "{}s".format(self.__class__.__name__.lower()))
        return session.query(PageInfo).filter(
                attr.any(self.__class__.id == self.id)
        ).all()

    def delete(self, session=None):
        if len(self.get_ref_pages(session)) > 0:
            raise ConstraintError('%s in in use', self)
        super(File, self).delete(session)

    def to_dict(self, ref_pages=False):
        res = super(File, self).to_dict()
        if ref_pages:
            # FIXME: change key in dict
            res['used_by'] = [page.id for page in self.get_ref_pages()]

        return res

    def __repr__(self):  # pragma: nocover
        return "<%s %s at %s : %s>" % (self.__class__.__name,
                                       self.id, self.path, self.url)


class SimpleImageMixin(object):
    full_size = None

    @classmethod
    def set_sizes(cls, full):
        cls.full_size = tuple(full) if full else None

    def save_file(self, source):
        """ Called when saving source """

        log.debug("Calling save_file in %s. self.full_size=",
                  self.__class__.__name__, self.full_size)
        if self.content_type.partition('/')[0] == 'image':
            # only resize images
            handle = PIL.Image.open(source)
            log.debug('%s size %s', self.__class__.__name__, self.full_size)

            if self.full_size:
                log.debug('Resizing %s to %s', self.__class__.__name__,
                          self.full_size)
                handle = handle.resize(self.full_size)

            handle.save(self.path)

        else:
            raise ValueError('Unsupported file format: %' %
                             (self.content_type))

    def get_ref_pages(self, session):
        # Banners are in relationship with Pages, not translations
        # the constraint is not enforced
        return []


class Banner(SimpleImageMixin, File):
    default = Column(Boolean, default=False)
    __mapper_args__ = {'polymorphic_identity': 'banner'}


class Logo(SimpleImageMixin, File):
    __mapper_args__ = {'polymorphic_identity': 'logo'}


class Image(File):
    """ Simple class that keeps the images on disk.
        It automatically creates thumbnails if desired.
        Since it inherits from FileSystemEntity, it is
        transaction-safe.

        This class must be configured prior to use

        >>> from aybu.core.models.file import Image
        >>> Image.initialize(session, base="/tmp/testme", private="/tmp")

        Define sizes if you want thumbnails (width,height)
        >>> Image.thumb_sizes = dict(small=(120,120), medium=(300, 300))

        Set full_size to a tuple to set the original image max size (w, h)
        >>> Image.full_size = (600, 600)
    """

    __mapper_args__ = {'polymorphic_identity': 'image'}

    full_size = None
    thumb_sizes = {}

    @classmethod
    def set_sizes(cls, full=None, thumbs={}):
        cls.full_size = tuple(full) if full else None
        cls.thumb_sizes = dict(thumbs)

    @property
    def thumbnails(self):
        res = {}
        for tname in self.thumb_sizes:
            res[tname] = Thumbnail(self, tname, self.thumb_sizes[tname])
        return res

    def create_thumbnail(self, source):
        """ Called when saving image, both on create and on update.
        """
        handle = PIL.Image.open(source)
        for thumb in self.thumbnails.values():
            thumb.save(handle)
        return handle

    def rename_thumbnail(self, old_image_name, new_image_name):
        for thumb in self.thumbnails.values():
            thumb.rename(old_image_name, new_image_name)

    def save_file(self, handle):
        """ Called when saving source """
        if self.full_size:
            handle.thumbnail(self.full_size, PIL.Image.ANTIALIAS)

        handle.save(self.path)

    def to_dict(self, ref_pages=False):
        res = super(Image, self).to_dict(ref_pages)

        for k, t in self.thumbnails.iteritems():
            res['{}_url'.format(k)] = t.url
            res['{}_path'.format(k)] = t.path
            res['{}_width'.format(k)] = t.width
            res['{}_height'.format(k)] = t.height

        return res


class Thumbnail(object):
    """ Utility class to model thumbnails for a given Image entity """

    def __init__(self, image, name, size):
        self.image = image
        self.name = name
        self.width = size[0]
        self.height = size[1]

    @property
    def path(self):
        return os.path.join(self.image.dir, "%s_%s%s" % (self.image.plain_name,
                                                         self.name,
                                                         self.image.extension))

    @property
    def url(self):
        return str(self.path.replace(self.image.private_path, ""))

    def rename(self, old_image_name, new_image_name):
        old_path = os.path.join(self.image.dir, "%s_%s%s" %
                                (old_image_name, self.name,
                                 self.image.extension))
        new_path = os.path.join(self.image.dir, "%s_%s%s" %
                                (new_image_name, self.name,
                                 self.image.extension))
        shutil.move(old_path, new_path)

    def save(self, handle):
        copy = handle.copy()
        copy.thumbnail((self.width, self.height), PIL.Image.ANTIALIAS)
        copy.save(self.path)

    def __repr__(self):  # pragma: nocover
        return "<Thumbnail '%s' (image: %d) [%sx%s]>" % (self.name,
                                                         self.image.id,
                                                         self.width,
                                                         self.height)
