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

import PIL.Image
import os
import random
import shutil
import string
import tempfile
from logging import getLogger

from aybu.core.exc import ConstraintError
from aybu.core.models import (Banner,
                              Image,
                              File,
                              Setting,
                              SettingType,
                              Language,
                              Page,
                              PageInfo)
from aybu.core.exc import QuotaError

from aybu.core.testing import TransactionalTestsBase


def create_page(session, copy_from=None):
    if not copy_from:
        lang = Language(lang='it', country='IT')
        session.add(lang)
        page = Page(weight=1)
        session.add(page)
    else:
        lang = copy_from.lang
        page = Page(weight=copy_from.node.weight + 1)
        session.add(page)

    pageinfo = PageInfo(node=page, lang=lang, label=unicode(page.weight),
                        url_part=unicode(page.weight), content='')
    session.add(pageinfo)
    return pageinfo


class FileTestsBase(TransactionalTestsBase):

    def _create_tmp_file(self, content='__random__', **kwargs):
        """ Create a temporary file and return its name """
        filename = tempfile.mkstemp(dir=self.tempdir, **kwargs)[1]
        if content is '__random__':
            content = self._generate_rand_string()
            kwargs['suffix'] = 'txt'
        if content:
            with open(filename, "w") as f:
                f.write(content)
        return filename

    def _generate_rand_string(self, length=12):
        return ''.join(random.choice(string.letters) for i in xrange(length))

    def _get_test_file(self, name):
        return os.path.join(self.datadir, name)

    def setUp(self):
        super(FileTestsBase, self).setUp()
        self.tempdir = tempfile.mkdtemp()
        self.static = os.path.join(self.tempdir, 'static')
        os.mkdir(self.static)
        self.datadir = os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                  "data"))
        Banner.initialize(base=os.path.join(self.static, 'banners'),
                          private=self.tempdir)
        File.initialize(base=os.path.join(self.static, 'files'),
                          private=self.tempdir)
        Image.initialize(base=os.path.join(self.static, 'images'),
                          private=self.tempdir)

        self.log = getLogger(__name__)

    def tearDown(self):
        super(FileTestsBase, self).tearDown()
        shutil.rmtree(self.tempdir)
        Banner.tmp_objects = dict(added=[], removed=[], updated={}, failed=[])
        Image.tmp_objects = dict(added=[], removed=[], updated={}, failed=[])


class FileTests(FileTestsBase):

    def test_referred(self):
        tmpfile = self._create_tmp_file()
        newfile = File(name='testfile.txt', source=tmpfile,
                       session=self.session)
        self.session.commit()
        source = self._get_test_file('sample.png')
        newimage = Image(source=source, name="original.png",
                         session=self.session)
        self.session.commit()

        page = create_page(self.session)
        content = '<a href={f.url}>{f.name}</a><img src={img.url}/>'
        page.content = content.format(f=newfile, img=newimage)
        # Statements aren't needed: append will be performed by after_flush.
        #page.files.append(newfile)
        #page.images.append(newimage)
        self.session.commit()
        self.assertIn(page, newfile.pages)
        self.assertIn(page, newimage.pages)

        with self.assertRaises(ConstraintError):
            newfile.delete()

        with self.assertRaises(ConstraintError):
            newimage.delete()

        self.assertIn(page, newfile.pages)
        self.assertIn(page, newimage.pages)

        d = newfile.to_dict()
        self.assertNotIn('used_by', d)
        d = newfile.to_dict(ref_pages=True)
        self.assertIn('used_by', d)

    def test_delete(self):
        tmpfile = self._create_tmp_file()

        f = File(name='testfile.txt', source=tmpfile, session=self.session)
        self.session.commit()
        f.delete()
        self.session.commit()
        self.assertEqual(len(File.all(self.session)), 0)

    def test_max_files(self):
        tmpfile = self._create_tmp_file()
        s = Setting(name='max_files', value=1,
                    type=SettingType(name='integer', raw_type='int'))
        self.session.add(s)

        with self.assertRaises(QuotaError):
            File(name='testfile.txt', source=tmpfile, session=self.session)
            File(name="testfile2.txt", source=tmpfile, session=self.session)
        self.session.rollback()


class BannerTests(FileTestsBase):

    def test_set_size(self):
        size = (600, 300)
        Banner.set_sizes(full=size)
        self.assertEqual(Banner.full_size, size)

    def test_wrong_content(self):
        tmpfile = self._create_tmp_file()
        with self.assertRaises(ValueError):
            Banner(source=tmpfile, session=self.session)

    def test_no_resize(self):
        test_file = self._get_test_file('sample.png')
        Banner.set_sizes(full=None)
        source_size = PIL.Image.open(test_file).size
        b = Banner(source=test_file, session=self.session)
        banner_size = PIL.Image.open(b.path).size
        self.assertEqual(banner_size, source_size)
        self.session.rollback()

    def test_resize(self):
        """ Banners are not streched anymore """
        full_size = (300, 400)
        real_size = (1, 1)
        test_file = self._get_test_file('sample.png')
        Banner.set_sizes(full=full_size)
        b = Banner(source=test_file, session=self.session)
        banner_size = PIL.Image.open(b.path).size
        self.assertEqual(banner_size, real_size)
        self.session.rollback()

    def test_default(self):
        self.assertEqual(None, Banner.get_default(self.session))
        b1 = Banner(source=self._get_test_file('sample.png'),
               name='banner.png', session=self.session)
        self.assertEqual(None, Banner.get_default(self.session))
        b2 = Banner(source=self._get_test_file('sample.png'),
               name='banner.png', session=self.session,
               default=True
        )
        self.assertTrue(b2.default)
        self.assertIs(b2, Banner.get_default(self.session))

        b1.default = True
        self.assertIs(b1, Banner.get_default(self.session))
        self.assertFalse(b2.default)

        self.session.rollback()


class ImageTests(FileTestsBase):

    def test_set_full_size(self):
        size = (600, 300)
        Image.set_sizes(full=size)
        self.assertEqual(Image.full_size, size)

    def test_set_thumb_sizes(self):
        thumbs = dict(first=(300, 300), second=(600, 300))
        Image.set_sizes(thumbs=thumbs)
        self.assertEqual(thumbs, Image.thumb_sizes)

    def test_create(self):
        thumbs = dict(small=(100, 100), medium=(300, 300))
        full_size = (600, 400)
        handle = PIL.Image.open(self._get_test_file('sample.png'))
        big_handle = handle.resize(full_size)
        big_image = self._create_tmp_file(content=None, suffix=".png")
        big_handle.save(big_image)
        Image.set_sizes(thumbs=thumbs, full=full_size)
        i = Image(source=big_image, session=self.session)
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
        thumbs = dict(small=(100, 100))
        Image.set_sizes(thumbs=thumbs)
        image = Image(source=source, name="original.png", session=self.session)
        self.session.commit()

        image.name = 'updated.png'
        self.assertIn('updated.png', image.path)
        self.assertIn('updated_small.png', image.thumbnails['small'].path)

    def test_to_dict(self):
        source = self._get_test_file('sample.png')
        thumbs = dict(small=(100, 100))
        Image.set_sizes(thumbs=thumbs)
        image = Image(source=source, name="original.png", session=self.session)
        self.session.commit()

        d = image.to_dict()
        self.assertIn('small_url', d)
        self.assertIn('small_width', d)
        self.assertIn('width', d)
        self.assertIn('height', d)
        self.assertIn('small_height', d)

        d1 = image.to_dict(paths=True)
        self.assertIn('path', d1)
        self.assertIn('small_path', d1)
