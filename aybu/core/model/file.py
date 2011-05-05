#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright © 2010 Asidev s.r.l. - www.asidev.com
"""

import logging
import os
import PIL

from elixir import using_options, using_options_defaults, options_defaults
from makako.containers import Storage
from pufferfish import FileSystemEntity
from pufferfish import add_session_hooks

log = logging.getLogger(__name__)

using_options_defaults(table_options=dict(mysql_engine="InnoDB"))
options_defaults.update(dict(table_options=dict(mysql_engine="InnoDB")))

__all__ = ['File', 'Image']


class File(FileSystemEntity):
    """
        Simple class that can be used as an elixir Entity
        that keeps the file on disk.
        This class must be configured prior to use

        >>> from aybu.core.model.entities import File
        >>> File.set_paths(base="/tmp/testme", private="/tmp")
        ...
    """

    add_session_hooks()
    using_options(tablename="files")

    def to_dict(self):
        d = Storage(super(File, self).to_dict())
        d.id = self.id
        #d.type = self.table.c.row_type
        return d


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

    def __str__(self):
        return "<Thumbnail '%s' (image: %d) [%sx%s]>" % (self.name,
                                                         self.image.id,
                                                         self.width,
                                                         self.height)

    def __repr__(self):
        return self.__str__()


class Image(File):
    """ Simple class that can be used as an elixir Entity
        that keeps the images on disk. It automatically creates thumbnails
        if desired. Since it inherits from FileSystemEntity, it is
        transaction-safe.

        This class must be configured prior to use

        >>> from aybu.core.model.entities import Image
        >>> Image.set_paths(base="/tmp/testme", private="/tmp")

        or

        >>> Image.base_path = "/tmp/testme"
        >>> Image.private_path = "/tmp"

        Define sizes if you want thumbnails.

        >>> Image.thumb_sizes = dict(small=(120,120), medium=(300, 300))

        Set full_size a a tuple to set the original image max size
        >>> Image.full_size = (600, 600)
    """

    full_size = None
    thumb_sizes = {}

    using_options(tablename="images", inheritance='single')

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

    def __str__(self):
        self.setup_paths()
        return "<Image %d at %s : %s>" % (self.id, self.path, self.url)

    def __repr__(self):
        self.setup_paths()
        return self.__str__()
