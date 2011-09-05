#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Copyright © 2010 Asidev s.r.l. - www.asidev.com """

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
import logging
import os
import PIL

from aybu.website.models.base import Base

__all__ = ['File', 'Image', 'Banner']

log = logging.getLogger(__name__)


class File(Base):
    """
        Simple class that can be used as an elixir Entity
        that keeps the file on disk.
        This class must be configured prior to use

        >>> from aybu.cms.model.entities import File
        >>> File.set_paths(base="/tmp/testme", private="/tmp")
        ...
    """

    __tablename__ = 'files'
    __table_args__ = ({'mysql_engine': 'InnoDB'})
    discriminator = Column('row_type', Unicode(50))
    __mapper_args__ = {'polymorphic_on': discriminator}

    id = Column(Integer, primary_key=True)
    content_type = Column(Unicode(128))
    name = Column(Unicode(128), nullable=False)
    size = Column(Integer)


class Banner(File):

    __mapper_args__ = {'polymorphic_identity': 'banner'}

    full_size = None
    thumb_sizes = {}

    @classmethod
    def set_sizes(cls, full=None, thumbs={}):
        cls.full_size = full
        cls.thumb_sizes = thumbs

    def save_file(self, handle):
        """ Called when saving source """

        if self.content_type.partition('/')[0] == 'image':

            handle = PIL.Image.open(handle)

            log.debug('Banner size %s', self.full_size)

            if self.full_size:
                log.debug('Resizing Banner to %s', self.full_size)
                handle = handle.resize(self.full_size)

            handle.save(self.path)

    def __repr__(self):
        self.setup_paths()
        return "<Banner %d at %s : %s>" % (self.id, self.path, self.url)


class Image(File):
    """ Simple class that can be used as an elixir Entity
        that keeps the images on disk. It automatically creates thumbnails
        if desired. Since it inherits from FileSystemEntity, it is
        transaction-safe.

        This class must be configured prior to use

        >>> from aybu.cms.model.entities import Image
        >>> Image.set_paths(base="/tmp/testme", private="/tmp")

        or

        >>> Image.base_path = "/tmp/testme"
        >>> Image.private_path = "/tmp"

        Define sizes if you want thumbnails.

        >>> Image.thumb_sizes = dict(small=(120,120), medium=(300, 300))

        Set full_size a a tuple to set the original image max size
        >>> Image.full_size = (600, 600)
    """

    __mapper_args__ = {'polymorphic_identity': 'image'}

    full_size = None
    thumb_sizes = {}

    @classmethod
    def set_sizes(cls, full=None, thumbs={}):
        cls.full_size = full
        cls.thumb_sizes = thumbs

    @property
    def thumbnails(self):
        self.setup_paths()
        res = Storage()
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

    def save_file(self, handle):
        """ Called when saving source """
        if self.full_size:
            handle.thumbnail(self.full_size, PIL.Image.ANTIALIAS)

        handle.save(self.path)

    def __repr__(self):
        self.setup_paths()
        return "<Image %d at %s : %s>" % (self.id, self.path, self.url)


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

    def save(self, handle):
        copy = handle.copy()
        copy.thumbnail((self.width, self.height), PIL.Image.ANTIALIAS)
        copy.save(self.path)

    def __repr__(self):
        return "<Thumbnail '%s' (image: %d) [%sx%s]>" % (self.name,
                                                         self.image.id,
                                                         self.width,
                                                         self.height)
