#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright 2010-2012 Asidev s.r.l.

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
                        Boolean,
                        Integer)
from sqlalchemy.orm.session import object_session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.declarative import declared_attr

import logging
import os
import shutil
import cStringIO
import wand.image

from aybu.core.models.base import Base
from aybu.core.models.translation import PageInfo
from aybu.core.models.setting import Setting
from aybu.core.exc import ConstraintError, QuotaError
from pufferfish import FileSystemEntity


__all__ = ['File', 'Image', 'Banner', 'Logo']
log = logging.getLogger(__name__)
DEFAULT_BLUR = 0.5


def open_image(source):
    s = cStringIO.StringIO(source.read())
    return wand.image.Image(file=s)


def thumbnail(handle, width, height, filter='triangle', blur=DEFAULT_BLUR):

    x = handle.width
    y = handle.height

    if x > width:
        y = max(y * width / x, 1)
        x = width

    if y > height:
        x = max(x * height / y, 1)
        y = height

    handle.resize(x, y, filter=filter, blur=blur)
    return handle


class File(FileSystemEntity, Base):
    """
        Simple class that keeps the file on disk.
    """
    __tablename__ = 'files'
    __table_args__ = ({'mysql_engine': 'InnoDB'})
    discriminator = Column('row_type', Unicode(50))
    __mapper_args__ = {'polymorphic_on': discriminator}

    @classmethod
    def create_new(cls, newobj, args, kwargs):
        """ This method is called upon user-called constructor invocation
            as it is set by pufferfish as the 'init' instance event callback
            http://www.sqlalchemy.org/docs/orm/events.html
            #sqlalchemy.orm.events.InstanceEvents.init
        """
        try:
            session = kwargs['session']
        except KeyError:
            return

        if cls.__name__.lower() == 'file':
            max_files = Setting.get(session, 'max_files').value
            num_files = File.count(session, (File.discriminator == None))
            type_ = "files"

        else:
            max_files = Setting.get(session, 'max_images').value
            num_files = File.count(session,
                                   (File.discriminator.in_(('image',
                                                            'logo',
                                                            'banner',
                                                            'background'))))
            type_ = 'images/banners/logos'

        log.debug("Current %s objects: %d, max: %d",
                  cls.__name__, num_files, max_files)
        if max_files > 0 and num_files >= max_files:
            raise QuotaError('Maximum number of {} reached'\
                             .format(type_))

        # TODO Check if disk space is reach
        super(File, cls).create_new(newobj, args, kwargs)

    @property
    def pages(self):
        """ Return all translations that have this file in its relation """
        session = object_session(self)
        attr = getattr(PageInfo, "{}s".format(self.__class__.__name__.lower()))
        return session.query(PageInfo).filter(
                attr.any(self.__class__.id == self.id)
        ).all()

    def delete(self):
        if len(self.pages) > 0:
            raise ConstraintError('%s in in use', self)
        super(File, self).delete()

    def to_dict(self, ref_pages=False):
        res = super(File, self).to_dict()
        if ref_pages:
            # FIXME: change key in dict
            res['used_by'] = [page.id for page in self.pages]

        return res

    @classmethod
    def all(cls, session, start=None, limit=None, query_options=()):
        try:
            discriminator = cls.__mapper_args__['polymorphic_identity']
        except KeyError:
            discriminator = None
        filters = (cls.discriminator == discriminator, )
        return cls.search(session, start=start, limit=limit,
                          query_options=query_options, filters=filters)

    def __repr__(self):  # pragma: nocover
        return "<%s %s at %s : %s>" % (self.__class__.__name__,
                                       self.id, self.path, self.url)


class SimpleImageMixin(object):
    full_size = None

    @declared_attr
    def default(self):
        return Column(Boolean, default=False)

    @declared_attr
    def weight(self):
        return Column(Integer, default=0, unique=False)

    @classmethod
    def get_default(cls, session):

        try:
            default = getattr(cls, 'default')
            discriminator = getattr(cls, 'discriminator')
            identity = getattr(cls, '__mapper_args__')['polymorphic_identity']
            return cls.search(session,
                              filters=(default == True,
                                       discriminator == identity),
                              start=0, limit=1)[0]
        except IndexError:
            return None

    @classmethod
    def set_default(cls, obj, value, oldvalue, initiator):
        if value:
            cls.search(object_session(obj),
                       filters=(cls.id != obj.id), return_query=True)\
                            .update({'default': False},
                                    synchronize_session='fetch')

    @classmethod
    def set_sizes(cls, full):
        cls.full_size = tuple(full) if full else None

    def save_file(self, source):
        """ Called when saving source """

        log.debug("Calling save_file in %s. self.full_size=%s",
                  self.__class__.__name__, self.full_size)
        # FIXME support SWF / Videos!
        if self.content_type.partition('/')[0] == 'image':
            # only resize images
            handle = open_image(source)
            log.debug('%s size %s', self.__class__.__name__, self.full_size)

            if self.full_size:
                log.debug('Resizing %s to %s', self.__class__.__name__,
                          self.full_size)
                handle = thumbnail(handle, width=self.full_size[0],
                                   height=self.full_size[1])

            handle.save(filename=self.path)
            handle.close()

        else:
            raise ValueError('Unsupported file format: %' %
                             (self.content_type))

    @property
    def pages(self):
        # Banners/Logos are in relationship with Pages,
        # not translations and the constraint is not enforced
        return []

    def __repr__(self):
        rep = super(SimpleImageMixin, self).__repr__()
        if self.default:
            rep = rep.replace(">", " [default]>")
        return rep

    def to_dict(self):
        d = super(SimpleImageMixin, self).to_dict()
        d['default'] = self.default
        d['weight'] = self.weight
        return d


class Banner(SimpleImageMixin, File):
    __mapper_args__ = {'polymorphic_identity': 'banner'}


class Logo(Banner):
    __mapper_args__ = {'polymorphic_identity': 'logo'}


class Background(Banner):
    __mapper_args__ = {'polymorphic_identity': 'background'}

    @classmethod
    def all(cls, session, start=None, limit=None, query_options=()):
        return cls.search(session,
                          start=start,
                          limit=limit,
                          query_options=query_options,
                          sort_by='weight')


class Image(File):
    """ Simple class that keeps the images on disk.
        It automatically creates thumbnails if desired.
        Since it inherits from FileSystemEntity, it is
        transaction-safe.

        This class must be configured prior to use

        >>> from aybu.core.models.file import Image
        >>> Image.initialize(session, base="/tmp/testme", private="/tmp")

        Define sizes if you want thumbnails (width, height)
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

    @property
    def width(self):
        with wand.image.Image(file=self.source) as img:
            return img.width

    @property
    def height(self):
        with wand.image.Image(file=self.source) as img:
            return img.height

    def create_thumbnail(self, source):
        """ Called when saving image, both on create and on update.
        """
        handle = open_image(source)
        for thumb in self.thumbnails.values():
            thumb.save(handle)
        return handle

    def rename_thumbnail(self, old_image_name, old_extension, new_image_name):
        for thumb in self.thumbnails.values():
            thumb.rename(old_image_name, old_extension, new_image_name)

    def save_file(self, handle):
        """ Called when saving source """
        if self.full_size:
            handle = thumbnail(handle, width=self.full_size[0],
                               height=self.full_size[1])

        handle.save(filename=self.path)
        handle.close()

    def to_dict(self, ref_pages=False, paths=False):
        res = super(Image, self).to_dict(ref_pages)
        res['width'] = self.width
        res['height'] = self.height

        if paths:
            res['path'] = self.path

        for k, t in self.thumbnails.iteritems():
            res['{}_url'.format(k)] = t.url
            res['{}_width'.format(k)] = t.width
            res['{}_height'.format(k)] = t.height
            if paths:
                res['{}_path'.format(k)] = t.path

        return res

    @classmethod
    def on_name_update(cls, obj, value, oldvalue, initiator):
        try:
            if oldvalue.name == "NO_VALUE":
                # When constructing object, sqlalchemy calls this event
                # using NO VALUE symbol as old value
                return

        except AttributeError:
            pass

        if oldvalue == cls.temporary_name or value == oldvalue:
            # No need to update links when name was temporary
            # or when it does not change
            return

        obj.old_name = oldvalue

        for page in obj.pages:
            page.update_img_src(obj)

        del obj.old_name


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
        return "{0}/{1}_{2}{3}".format(self.image.url_dir,
                                       self.image.plain_name,
                                       self.name,
                                       self.image.extension)

    def rename(self, old_image_name, old_extension, new_image_name):
        old_path = os.path.join(self.image.dir, "%s_%s%s" %
                                (old_image_name, self.name,
                                 old_extension))
        new_path = os.path.join(self.image.dir, "%s_%s%s" %
                                (new_image_name, self.name,
                                 self.image.extension))
        shutil.move(old_path, new_path)

    def save(self, handle):
        with handle.clone() as copy:
            copy = thumbnail(copy, self.width, self.height)
            log.debug('Saving thumbnail to %s', self.path)
            copy.save(filename=self.path)

    def __repr__(self):  # pragma: nocover
        return "<Thumbnail '%s' (image: %d) [%sx%s]>" % (self.name,
                                                         self.image.id,
                                                         self.width,
                                                         self.height)
