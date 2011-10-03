#!/usr/bin/env python
# -*- coding: utf-8 -*-

import PIL.Image
import os
import random
import shutil
import string
import tempfile
from logging import getLogger

from aybu.core.models.file import Banner, Image
from test_base import BaseTests


class FileTests(BaseTests):

    def _create_tmp_file(self, content=None, **kwargs):
        """ Create a temporary file and return its name """
        filename = tempfile.mkstemp(dir=self.tempdir, **kwargs)[1]
        if not content is None:
            with open(filename, "w") as f:
                f.write(content)
        return filename

    def _generate_rand_string(self, length=12):
        return ''.join(random.choice(string.letters) for i in xrange(length))

    def _get_test_file(self, name):
        return os.path.join(self.datadir, name)

    def setUp(self):
        super(FileTests, self).setUp()
        self.tempdir = tempfile.mkdtemp()
        self.datadir = os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                  "data"))
        Banner.initialize(self.session, base=self.tempdir)
        Image.initialize(self.session, base=self.tempdir)
        self.log = getLogger(__name__)

    def tearDown(self):
        super(FileTests, self).tearDown()
        shutil.rmtree(self.tempdir)
        Banner.tmp_objects = dict(added=[], removed=[], updated={}, failed=[])
        Image.tmp_objects = dict(added=[], removed=[], updated={}, failed=[])


class BannerTests(FileTests):

    def test_set_size(self):
        size = (600, 300)
        Banner.set_sizes(full=size)
        self.assertEqual(Banner.full_size, size)

    def test_wrong_content(self):
        content = self._generate_rand_string()
        tmpfile = self._create_tmp_file(content=content)
        with self.assertRaises(ValueError):
            Banner(source=tmpfile)

    def test_no_resize(self):
        test_file = self._get_test_file('sample.png')
        Banner.set_sizes(full=None)
        source_size = PIL.Image.open(test_file).size
        b = Banner(source=test_file)
        banner_size = PIL.Image.open(b.path).size
        self.assertEqual(banner_size, source_size)
        self.session.rollback()

    def test_resize(self):
        size = (300,400)
        test_file = self._get_test_file('sample.png')
        Banner.set_sizes(full=size)
        b = Banner(source=test_file)
        banner_size = PIL.Image.open(b.path).size
        self.assertEqual(banner_size, size)
        self.session.rollback()


class ImageTests(FileTests):

    def test_set_full_size(self):
        size = (600, 300)
        Image.set_sizes(full=size)
        self.assertEqual(Image.full_size, size)

    def test_set_thumb_sizes(self):
        thumbs = dict(first=(300,300), second=(600,300))
        Image.set_sizes(thumbs=thumbs)
        self.assertEqual(thumbs, Image.thumb_sizes)

    def test_create(self):
        thumbs = dict(small=(100,100), medium=(300,300))
        full_size = (600, 400)
        handle = PIL.Image.open(self._get_test_file('sample.png'))
        big_handle = handle.resize(full_size)
        big_image = self._create_tmp_file(suffix=".png")
        big_handle.save(big_image)
        Image.set_sizes(thumbs=thumbs, full=full_size)
        Image.private_path = self.tempdir
        i = Image(source=big_image)
        # no need to commit, session is being flushed by pufferfish

        self.assertEqual(len(i.thumbnails), len(thumbs))
        self.assertEqual(i.thumbnails.keys(), thumbs.keys())

        for tname, size in thumbs.iteritems():
            thumb = i.thumbnails[tname]
            r_size = PIL.Image.open(thumb.path).size
            self.assertEqual(size[0], r_size[0])
            self.assertEqual(thumb.url, thumb.path.replace(self.tempdir, ""))

        f_size = PIL.Image.open(i.path).size
        self.assertEqual(f_size, full_size)

        self.session.rollback()

    def test_rename(self):
        source = self._get_test_file('sample.png')
        thumbs = dict(small=(100,100))
        Image.set_sizes(thumbs=thumbs)
        image = Image(source=source, name="original.png")
        self.session.commit()

        image.name = 'updated.png'
        self.assertIn('updated.png', image.path)
        self.assertIn('updated_small.png', image.thumbnails['small'].path)
