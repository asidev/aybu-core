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

from aybu.core.models import (File, Image, PageInfo)
from aybu.core.htmlmodifier import (associate_files,
                                    associate_images,
                                    associate_pages)
from test_file import FileTestsBase
from test_file import create_page
from BeautifulSoup import BeautifulSoup
import sqlalchemy.orm
import sqlalchemy.event


class AssociationTests(FileTestsBase):

    def setUp(self):
        super(AssociationTests, self).setUp()
        self.page = create_page(self.session)
        self.session.flush()
        # reinitialize session event
        sqlalchemy.event.listen(sqlalchemy.orm.Session, 'before_flush',
                                PageInfo.before_flush)

    def test_associate_files(self):

        tmpfile = self._create_tmp_file()
        f1 = File(name='first.txt', session=self.session, source=tmpfile)
        f2 = File(name='second.txt', session=self.session, source=tmpfile)
        self.session.flush()

        html = """<a href={file.url}>{file.name}</a>"""
        self.page.content = html.format(file=f1)
        self.session.flush()
        self.assertIn(f1, self.page.files)
        self.assertNotIn(f2, self.page.files)

        self.page.content = html.format(file=f2)
        self.session.flush()
        self.assertIn(f2, self.page.files)
        self.assertNotIn(f1, self.page.files)

    def test_associate_images(self):

        source = self._get_test_file('sample.png')
        i1 = Image(name='first.png', session=self.session, source=source)
        i2 = Image(name='second.png', session=self.session, source=source)
        self.session.flush()

        html = """<img src='{image.url}>'/>"""
        self.page.content = html.format(image=i1)
        self.session.flush()
        self.assertIn(i1, self.page.images)
        self.assertNotIn(i2, self.page.images)

        self.page.content = html.format(image=i2)
        self.session.flush()
        self.assertIn(i2, self.page.images)
        self.assertNotIn(i1, self.page.images)

    def test_associate_pages(self):
        p1 = create_page(self.session, self.page)
        p2 = create_page(self.session, p1)
        self.session.flush()

        html = """<a href='{page.url}'>{page.label}</a>"""
        self.page.content = html.format(page=p1)
        self.session.flush()
        self.assertIn(p1, self.page.links)
        self.assertNotIn(p2, self.page.links)

        self.page.content = html.format(page=p2)
        self.session.flush()
        self.assertIn(p2, self.page.links)
        self.assertNotIn(p1, self.page.links)

    def test_nonmatching_anchors(self):
        html = """
            <a attr="bogus">1</a>
            <a href="http://www.example.com">2</a>
            <a href="/non/existing/url.html">3</a>
            <a href="{files}/1/not_existing.txt">4</a>
            <img src="{images}/2/not_existing.png"/>
            <img src="http://www.example.com/test.png"/>
            <img src="{images}/unmanaged.png"/>
            <img notsrc="{images}/unmanaged.png"/>
        """.format(files=File.url_base, images=Image.url_base)

        soup = BeautifulSoup(html, smartQuotesTo=None)
        soup = associate_files(soup, self.page)
        soup = associate_images(soup, self.page)
        soup = associate_pages(soup, self.page)
        self.assertEqual(len(self.page.files), 0)
        self.assertEqual(len(self.page.links), 0)
        self.assertEqual(len(self.page.images), 0)
