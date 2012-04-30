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

from logging import getLogger
from aybu.core.models.base import Base
from aybu.core.models.file import (Banner,
                                   File,
                                   Image,
                                   Logo)
from aybu.core.models.language import Language
from aybu.core.models.node import (ExternalLink,
                                   InternalLink,
                                   Menu,
                                   Node,
                                   Page,
                                   Section,
                                   PageBanner)
from aybu.core.models.translation import (MenuInfo,
                                          NodeInfo,
                                          CommonInfo,
                                          PageInfo,
                                          SectionInfo,
                                          ExternalLinkInfo,
                                          InternalLinkInfo)
from aybu.core.models.setting import (Setting,
                                      SettingType)
from aybu.core.models.theme import Theme
from aybu.core.models.user import (User,
                                   RemoteUser,
                                   Group)
from aybu.core.models.view import (View,
                                   ViewDescription)
from aybu.core.models.media import (MediaPage,
                                    MediaCollectionPage,
                                    MediaItemPage,
                                    MediaCollectionPageInfo,
                                    MediaItemPageInfo)
from aybu.core.utils import get_object_from_python_path
from aybu.core.exc import ValidationError
from pufferfish import FileSystemEntity
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm import Session
import sqlalchemy.orm
import sqlalchemy.event
from sqlalchemy.util.langhelpers import symbol
import os

log = getLogger(__name__)


__all__ = ['add_default_data', 'Base', 'Banner', 'Image', 'File',
           'Language', 'ExternalLink', 'InternalLink', 'Menu', 'Node', 'Page',
           'Section', 'MenuInfo', 'NodeInfo', 'PageInfo', 'SectionInfo',
           'ExternalLinkInfo', 'InternalLinkInfo', 'Setting', 'SettingType',
           'Theme', 'User', 'Group', 'View', 'ViewDescription',
           'MediaPage', 'MediaCollectionPage', 'MediaItemPage',
           'MediaCollectionPageInfo', 'MediaItemPageInfo', 'RemoteUser', 'export',
           'PageBanner']

__entities__ = [Theme,
                SettingType,
                Setting,
                Language,
                View,
                ViewDescription,
                File,
                Banner,
                Logo,
                Image,
                Node,
                NodeInfo]


@sqlalchemy.event.listens_for(sqlalchemy.orm.mapper, 'mapper_configured')
def init_attrs_events(mapper, class_):
    """
    Since Mixins are used, and mixins are not mapped classes, their attributes
    are normal Column objects, not InstrumentedAttribute instances that accept
    the 'set' event. We then set the "mapper_configured"  event, and, after
    the mapping phase, all events are set.
    """

    if class_ is Banner or class_ is Logo:
        sqlalchemy.event.listen(class_.default, 'set', class_.set_default)

    elif class_ is Image:
        sqlalchemy.event.listen(Image.name, 'set', Image.on_name_update)

    elif class_ in (SectionInfo,
                    PageInfo, MediaCollectionPageInfo, MediaItemPageInfo):
        sqlalchemy.event.listen(class_.url_part,
                                'set',
                                Base.on_attr_update)
        sqlalchemy.event.listen(class_.node,
                                'set',
                                Base.on_attr_update)
        if class_ in (PageInfo, MediaCollectionPageInfo, MediaItemPageInfo):
            sqlalchemy.event.listen(class_.content,
                                    'set',
                                    Base.on_attr_update)

    elif class_ in (Section,
                    Page, MediaPage, MediaCollectionPage, MediaItemPage):
        sqlalchemy.event.listen(class_.parent_id, 'set', Base.on_attr_update)


def init_session_events(session=Session):
    sqlalchemy.event.listen(session, 'before_flush', before_flush)


def before_flush(session, *args):
    """ Set 'parent_url' and update it when 'url_part' was changed.
    """

    nones = (symbol('NO_VALUE'), symbol('NEVER_SET'), None)

    # NOTE: cannot know objects order in session.new and session.dirty,
    #       for that reason multiple 'for' cicles are needed.

    # Handle 'CommonInfo.parent_url' for 'new' objects.
    for obj in session.new:

        if not isinstance(obj, CommonInfo):
            continue

        if obj.node is None and obj.node_id is None:
            msg = '{} object must belong to a Node.'
            msg = msg.format(obj.__class__.__name__)
            raise ValueError(msg)

        elif obj.node is None:
            obj.node = Node.get(session, obj.node_id)

        #log.info("Update 'parent_url' of %s", obj.label)
        obj.update_parent_url()

    # Handle 'PageInfo.content' for 'new' objects.
    for obj in session.new:

        if not isinstance(obj, PageInfo):
            continue

        #log.info("Update associations of %s", obj.label)
        obj.update_associations()

    # Handle 'PageInfo.content' for 'new' objects.
    for obj in session.dirty:

        if not isinstance(obj, PageInfo) or \
           not hasattr(obj, '_attrs_updates') or \
           'content' not in obj._attrs_updates:
            continue

        #log.info("Update associations of %s", obj.label)
        obj.update_associations()

    # First phase.
    # Handle 'node' changes in CommonInfo objects:
    # replace olds CommonInfo.parent_url with new ones.
    for obj in session.dirty:

        if not isinstance(obj, CommonInfo) or \
           not hasattr(obj, '_attrs_updates') or \
           'node' not in obj._attrs_updates:
            continue

        #log.info("Update parent_url of %s", obj.label)
        obj.update_parent_url()

    # Second phase: handle Page|Section objects changes.
    # Handle 'parent_id' changes in Page and Section objects:
    # replace olds CommonInfo.parent_url with new ones.
    for obj in session.dirty:

        if not isinstance(obj, (Page, Section)) or \
           not hasattr(obj, '_attrs_updates') or \
           'parent_id' not in obj._attrs_updates:
            continue

        #log.debug('Update translations of %s', obj.id)

        for translation in obj.translations:
            #log.info('Update translation: %s', translation.label)
            translation.update_parent_url()

    # Third phase: handle CommonInfo.url_part changes.
    # Handle 'url_part' changes in CommonInfo objects:
    # replace olds CommonInfo.parent_url with new ones.
    for obj in session.dirty:

        if not isinstance(obj, CommonInfo) or \
           not hasattr(obj, '_attrs_updates') or \
           'url_part' not in obj._attrs_updates:
            continue

        old = obj._attrs_updates['url_part']['old']
        new = obj._attrs_updates['url_part']['new']

        if old in nones or old == new:
            continue

        #log.info("Update children of %s", obj.label)
        obj.update_children_parent_url()


def add_default_data(session, data):

    seq_classes = {}
    for params in data:

        cls = 'aybu.core.models.%s' % params.pop('cls_')
        cls = get_object_from_python_path(cls)
        mapper = class_mapper(cls)

        if hasattr(cls, "id_seq") and not cls.__name__ in seq_classes:
            seq_classes[cls.__name__] = cls

        for key, value in params.iteritems():

            if not value is None:

                try:
                    property_ = mapper.get_property(key)
                except:
                    continue

                if not hasattr(property_, 'argument'):
                    continue

                try:
                    class_ = property_.argument.class_

                except AttributeError:
                    class_ = property_.argument()

                query = session.query(class_)
                if not property_.uselist and len(mapper.primary_key) == 1:
                    params[key] = query.get(value)
                    continue

        obj = cls(**params)
        obj = session.merge(obj)

    for cls in seq_classes.values():
        """ This works (and is needed) only on postrgresql to fix
            autoincrement
        """
        tablename = cls.__tablename__
        log.debug("Fixing sequence for cls %s (%s)", cls, tablename)
        seqname = "{}_id_seq".format(tablename)
        try:
            session.execute(
                "SELECT setval('{}', max(id)) FROM {};".format(seqname,
                                                               tablename)
            )
        except sqlalchemy.exc.OperationalError:
            # raised by MySQLdb
            pass
        except sqlalchemy.exc.ProgrammingError:
            # raised by oursql
            pass


def import_(engine_uri, session, data, sources, private):

    entities = {}
    seq_classes = []
    for entity in __entities__:

        entities[entity.__name__] = []

        if hasattr(entity, "id_seq") and not entity in seq_classes:
            seq_classes.append(entity)

        if entity.__name__ not in data or not data[entity.__name__]:
            print 'No data for %s' % entity.__name__
            continue

        entity_name = entity.__name__

        for item in data[entity_name]:

            if entity_name == 'Node':
                import node
                entity = getattr(node, item.pop('__class__'))
                if entity.__name__ not in entities:
                    entities[entity.__name__] = []
            elif entity_name == 'NodeInfo':
                import translation
                entity = getattr(translation, item.pop('__class__'))
                if entity.__name__ not in entities:
                    entities[entity.__name__] = []

            try:
                create_entity(session,
                              entities, entity, item, sources, private)

            except ValidationError:
                log.exception('ValidationError during first create.')
                raise

        session.flush()

    visited = set()
    for cls in seq_classes:
        """ This works (and is needed) only on postrgresql to fix
            autoincrement
        """
        tablename = cls.__tablename__

        if issubclass(cls, FileSystemEntity):
            seqname = "pufferfish_id_seq"
        else:
            seqname = "{}_id_seq".format(tablename)

        if seqname in visited:
            continue

        try:
            visited.add(seqname)
            log.debug("Fixing sequence %s", seqname)
            session.execute(
                "SELECT setval('{}', max(id)) FROM {};".format(seqname,
                                                               tablename)
            )

        except sqlalchemy.exc.OperationalError:
            # raised by MySQLdb
            pass

        except sqlalchemy.exc.ProgrammingError:
            # raised by oursql
            pass

        except:
            log.exception('Cannot fix sequence for cls %s', cls)
            raise


def create_entity(session, entities, entity, item, sources, private):

    if issubclass(entity, Image):
        base = os.path.join(private,
                            'uploads',
                            'images')
        if not os.path.exists(base):
            os.makedirs(base)
        Image.initialize(base=base,
                         private=private,
                         url_prefix='static')
        size = session.query(Setting).get('image_full_size').value
        Image.set_sizes(full=(size, size * 3),
                        thumbs=dict(thumb=(120, 120)))
        path = os.path.join(sources, item.pop('path'))
        if not os.path.exists(path):
            log.warn("Path does not exists %s: %s", sources, path)
            return

        item['source'] = path
        item['session'] = session

    elif issubclass(entity, Logo):
        base = os.path.join(private,
                            'uploads',
                            'logo')
        if not os.path.exists(base):
            os.makedirs(base)
        Logo.initialize(base=base,
                        private=private,
                        url_prefix='static')
        logo_width = session.query(Setting).get('logo_width').value
        logo_height = session.query(Setting).get('logo_height').value
        Logo.set_sizes(full=(logo_width, logo_height))
        path = os.path.join(sources, item.pop('path'))
        if not os.path.exists(path):
            log.warn("Path does not exists %s: %s", sources, path)
            return

        item['source'] = path
        item['session'] = session

    elif issubclass(entity, Banner):
        log.debug("Importging banner %s", item)
        base = os.path.join(private,
                            'uploads',
                            'banners')
        if not os.path.exists(base):
            os.makedirs(base)
        Banner.initialize(base=base,
                          private=private,
                          url_prefix='static')
        banner_width = session.query(Setting).get('banner_width').value
        banner_height = session.query(Setting).get('banner_height').value
        Banner.set_sizes(full=(banner_width, banner_height))
        path = os.path.join(sources, item.pop('path'))
        if not os.path.exists(path):
            log.warn("Path does not exists %s: %s", sources, path)
            return

        item['source'] = path
        item['session'] = session

    elif issubclass(entity, File):
        base = os.path.join(private,
                            'uploads',
                            'files')
        if not os.path.exists(base):
            os.makedirs(base)
        File.initialize(base=base,
                        private=private,
                        url_prefix='static')
        path = os.path.join(sources, item.pop('path'))
        if not os.path.exists(path):
            log.warn("Path does not exists %s: %s", sources, path)
            return

        item['source'] = path
        item['session'] = session

    elif issubclass(entity, Setting):
        # Add the key 'type' with SettingType object.
        for obj in entities['SettingType']:
            if obj.name == item['type_name']:
                item['type'] = obj

    elif issubclass(entity, NodeInfo):
        item['lang'] = session.query(Language).get(item['lang_id'])
        item['node'] = session.query(Node).get(item['node_id'])

    elif issubclass(entity, Page):
        banners = item.pop('banners')

    obj = entity(**item)
    session.add(obj)

    if issubclass(entity, Page):
        for banner in banners:
            obj.banners.append(Banner.get(session, banner['id']))

    entities[entity.__name__].append(obj)
