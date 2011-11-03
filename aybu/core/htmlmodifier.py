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

import re
import logging
from BeautifulSoup import BeautifulSoup


log = logging.getLogger(__name__)
__all__ = ['associate_images', 'associate_files',
           'associate_pages', 'update_img_src',
           'change_href']


def associate_files(obj, soup):
    raise NotImplementedError
    from aybu.core.models import File
    """ Parse html and associate found anchor with file link
        associations are wipe-out and the reconstructed with files found
        in the html
    """
    log.debug("Updating obj %s association with files" % (type(obj)))
    # copy old_images list if debugging
    old_files = list(obj.files)
    log.debug("Obj %d has files = %s", obj.id, [file.id for file in old_files])
    # first, empty the list of the obj-associated images
    obj.files = []

    anchors = soup.findAll('a')
    for a in anchors:
        log.debug("Found anchor %s", a)
        try:
            src = a['href']
        except:
            log.debug("The anchor %s has not href, "
                      "skipping url investigation", a)
            continue

        # now: we need only "local" link.
        if src.startswith("http://"):
            log.debug("Image %s is not local to this webserver, skipping", src)
            continue
        match = re.search("/\d+/", src)
        if match is None:
            log.debug("File %s is local but id was not found in the url", src)
            continue
        else:
            log.debug("File %s is local and id was not found in the url", src)

        try:
            log.debug("Match %s", match.group().replace("/", ""))
            id = int(match.group().replace("/", ""))
            file = File.get_by(id=id)
            log.debug("Adding file %d to obj %d", file.id, obj.id)
            obj.files.append(file)
        except Exception as e:
            log.debug("Error associating file to translation %s", e)

    log.debug("%s %d has obj.files = %s", type(obj), obj.id,
              [file.id for file in obj.files])
    log.debug("Files %s are no more associated with obj %d",
              [file.id for file in old_files if file not in obj.files],
              obj.id)
    return soup


def associate_images(obj, soup):
    """ Parse html and associate found images with obj.
        associations are wipe-out and the reconstructed with images found
        in the html
    """
    raise NotImplementedError
    from aybu.core.models import Image
    log.debug("Updating obj %s association with images" % (type(obj)))
    # copy old_images list if debugging
    old_images = list(obj.images)
    log.debug("Obj %d has images = %s", obj.id, [img.id for img in old_images])
    # first, empty the list of the obj-associated images
    obj.images = []

    imgs = soup.findAll('img')
    for img in imgs:
        log.debug("Found image %s", img)
        # now: we need only "local" images.
        try:
            src = img['src']
        except:
            log.debug("The img %s has not src, skipping src investigation",
                      img)
            continue

        if src.startswith("http://"):
            log.debug("Image %s is not local to this webserver, skipping", src)
            continue
        match = re.search("\d+", src)
        if match is None:
            log.debug("Image %s is local but id was not found in the url", src)
            continue
        id = int(match.group())
        image = Image.get_by(id=id)
        log.debug("Adding image %s to obj %d", image.id, obj.id)
        obj.images.append(image)

    log.debug("%s %d has obj.images = %s", type(obj), obj.id,
              [img.id for img in obj.images])
    log.debug("Images %s are no more associated with obj %d",
              [img.id for img in old_images if img not in obj.images],
              obj.id)
    return soup


def associate_pages(obj, soup):
    """ Parse html and associate found images with obj.
        associations are wipe-out and the reconstructed with images found
        in the html
    """
    raise NotImplementedError
    log.debug("Updating %s links" % (obj))
    old_pages = list(obj.links)
    log.debug("%s had links to %s", obj, [page for page in old_pages])
    # first, empty the list of the obj-associated pages
    obj.links = []

    mapper = config['routes.map']

    anchors = soup.findAll('a')
    for a in anchors:
        log.debug("Found anchor %s", a)
        # now: we need only "local" pages.

        try:
            href = a['href']
        except:
            log.debug("The anchor %s has not href, skipping url investigation",
                      a)
            continue

        if href.startswith("http://"):
            log.debug("Page %s is not local to this webserver, skipping", href)
            continue

        match = mapper.match(href)

        try:
            id = match['nodeinfo_id']
            ni = NodeInfo.get_by(id=id)

            log.debug("Adding %s to %s", ni, obj)
            obj.links.append(ni)
        except:
            log.debug("Link is local (%s) but is not referenced to a "\
                      "dynamic page", href)
            continue

    log.debug("%s has links to %s", obj, [p for p in obj.links])
    log.debug("%s are no more associated to %s",
              [p for p in old_pages if p not in obj.links], obj)

    return soup


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

        match = re.search(image.url, src)
        if match is None:
            log.debug("Image %s is local but is th one to modify", src)
            continue
        else:
            img['src'] = src.replace(image.old_name, image.name)
            log.debug("Updated image src %s", img)

    return soup


def change_href(nodeinfo, old_urls):

    raise NotImplementedError

    soup = BeautifulSoup(nodeinfo.content, smartQuotesTo=None)
    anchors = soup.findAll('a')

    # first, empty the list of the obj-associated pages
    nodeinfo.links = []
    mapper = config['routes.map']

    for a in anchors:
        log.debug("Found anchor %s", a)

        try:
            href = a['href']
        except:
            log.debug("The anchor %s has not href, skipping url investigation",
                      a)
            continue

        if href.startswith("http://"):
            log.debug("Page %s is not local to this webserver, skipping", href)
            continue

        if href in old_urls:

            ni = old_urls[href]
            if ni:

                new_url = ni.url

                log.debug('Found anchor referenced to %s, will be referenced '\
                          'to %s', href, new_url)
                a['href'] = new_url
                nodeinfo.links.append(ni)
            else:
                log.debug('The anchor referenced to %s will be removed due '\
                          'to page deletion', href)

                contents = a.contents
                parent = a.parent

                index = parent.contents.index(a)
                a.extract()
                for c in contents:
                    parent.insert(index, c)
                    index = index + 1

        else:

            try:
                match = mapper.match(href)
                id = match['nodeinfo_id']
                ni = NodeInfo.get_by(id=id)

                log.debug("Adding %s to %s", ni, nodeinfo)
                nodeinfo.links.append(ni)
            except Exception as e:
                log.debug("Link is local (%s) but is not referenced to a "\
                          "dynamic page", href)
                continue

    log.debug("Updating content on db")
    nodeinfo.content = unicode(soup)
    dbsession.flush()


def remove_target_attributes(soup, blank_to_rel=True):

    for a in soup.findAll('a'):

        target = a.pop('target', None)

        if not target:
            log.debug("No target attribute found in %s" % (a))
            continue

        log.debug("Removed target attribute from %s" % (a))

        if blank_to_rel and target == '_blank':
            a['rel'] = "external"
            log.debug("Added rel='external' in %s" % (a))

    return soup
