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

import collections
import logging
import re
from sqlalchemy.orm.session import object_session
from sqlalchemy.orm.exc import NoResultFound


log = logging.getLogger(__name__)
__all__ = ['associate_images', 'associate_files',
           'associate_pages', 'update_img_src']


Tag = collections.namedtuple('Tag', 'name attribute')


def match_pufferfish_urls(value, type_, session):

    if not hasattr(type_, "url_prefix"):
        log.warning("%s has not attribute url_prefix", type_)
        return

    url_base = "/{}/uploads/{}".format(type_.url_prefix, type_.dirname)
    log.error(url_base)
    match = re.search(r"%s/(\d+)/" % (url_base), value)
    if not match:
        log.debug("Tag %s is local to the webserver, "
                    "but did not match %s/\d+/", value, url_base)
        return None
    id_ = match.groups()[0].replace("/", "")
    log.debug("%s matches as pufferfish url with id %s", value, id_)
    return int(id_)


def match_pageinfo_urls(value, type_, session):
    try:
        # Remove '.html' at the end of the URL value before querying.
        if value.endswith('.html'):
            value = value.split('.html')[0]
        rel = type_.get_by_url(session, value)
        key = rel.id
        log.debug('Found %s which matches %s', rel, value)
        return key

    except:
        log.debug('No %s with url %s', type_.__name__, value)
        return None


def associate_to_pageinfo(soup, pginfo, tag, type_, match_callback,
                          attr_name=None):
    if attr_name:
        pginfo_attr = attr_name

    else:
        pginfo_attr = "{}s".format(type_.__name__.lower())

    session = object_session(pginfo)

    # empty the relation first
    setattr(pginfo, pginfo_attr, [])

    tags = soup.findAll(tag.name)
    for t in tags:
        log.debug('Found tag %s', t)
        try:
            attribute = t[tag.attribute]
        except:
            log.debug('Tag %s has not attribute %s', t, tag.attribute)
            continue

        if attribute.startswith('http://'):
            log.debug('Tag %s has %s attribute non-local (%s). Skipping', t,
                      tag.attribute, attribute)
            continue

        try:
            pkey = match_callback(attribute, type_, session)
            if not pkey:
                continue
            log.debug("Found %s in tag %s", type_.__name__, t)
            static_obj = type_.get(session, pkey)

        except NoResultFound as e:
            log.debug("%s", e)

        except Exception:
            log.exception('Error while adding %s to %s', t, pginfo)

        else:
            log.debug("Adding %s to %s.%s relation",
                      static_obj, pginfo, pginfo_attr)
            getattr(pginfo, pginfo_attr).append(static_obj)

    return soup


def associate_files(soup, pageinfo):
    from aybu.core.models import File
    return associate_to_pageinfo(soup, pageinfo,
                                 Tag(name='a', attribute='href'),
                                 File, match_pufferfish_urls)


def associate_images(soup, pageinfo):
    from aybu.core.models import Image
    return associate_to_pageinfo(soup, pageinfo,
                                 Tag(name='img', attribute='src'),
                                 Image,
                                 match_pufferfish_urls)


def associate_pages(soup, pageinfo):
    from aybu.core.models import PageInfo
    return associate_to_pageinfo(soup, pageinfo,
                                 Tag(name='a', attribute='href'),
                                 PageInfo,
                                 match_pageinfo_urls,
                                 "links")


def update_img_src(soup, image):
    """ Parse html and found and replace in src the new image name
    """
    log.debug("Updating links to %s", image)

    imgs = soup.findAll('img')
    for img in imgs:
        log.debug("Found image %s", img)
        # now: we need only "local" images.
        try:
            src = img['src']
        except:
            log.debug("The img %s has not src attribute, skipping src "\
                      "investigation", img)
            continue

        if src.startswith("http://"):
            log.debug("Image %s is not local to this webserver, skipping", src)
            continue

        match = re.search(image.url_dir, src)
        if match is None:
            continue
        else:
            img['src'] = src.replace(image.old_name, image.name)
            log.debug("Updated image src %s", img)

    return soup


def remove_target_attributes(soup, blank_to_rel=True):

    for a in soup.findAll('a'):
        try:
            target = a['target']
            del a['target']
        except:
            target = None

        if not target:
            log.debug("No target attribute found in %s" % (a))
            continue

        log.debug("Removed target attribute from %s" % (a))

        if blank_to_rel and target == '_blank':
            a['rel'] = "external"
            log.debug("Added rel='external' in %s" % (a))

    return soup
