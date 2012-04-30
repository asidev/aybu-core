
from logging import getLogger
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm.properties import RelationshipProperty
from sqlalchemy.orm import object_mapper
import aybu.core.models as models
import os
import os.path

_log = getLogger(__name__)
entities = ['Language',
            'SettingType',
            'View',
            'File',  # Image, Banner, Logo
            'User',
            'Group',
            'Theme',
            'Setting',
            'ViewDescription',
            # UserGroup
            'Node',  # Menu, Section, Page, ExternalLink, InternalLink,
                     # MediaPage, MediaCollectionPage, MediaItemPage
            'NodeInfo'  # MenuInfo, SectionInfo, PageInfo,
                        # ExternalLinkInfo, InternalLinkInfo
                        # MediaCollectionPageInfo, MediaItemPageInfo
            # PageFile,
            # PageImage,
            # PageBanner,
            ]


def export(session, classes=entities):
    dicts = []
    for cls in classes:
        cls = getattr(models, cls)
        for obj in session.query(cls).all():
            dict_ = dictify(obj)
            if isinstance(obj, models.File):
                if not os.path.exists(obj.path):
                    log.critical('File %s does not exists.', obj.path)
                    continue
                dict_['source'] = obj.path
                #open(obj.path, 'r').read().encode('base64')
            dicts.append(dict_)
    return dicts


def dictify(obj):
    """ Convert persistent object 'obj' in a dict.
        Dict keys are the columns names.
        Dict values are the columns values.
        NOTE:
            - FKs are included (ManyToOne),
            - No OneToMany, ManyToMany, OneToOne (FKs side).
            - ManyToMany secondary tables must be mapped to objects.
    """
    dict_ = {p.key: getattr(obj, p.key)
             for p in object_mapper(obj).iterate_properties
             if isinstance(p, ColumnProperty)}
    dict_['__class__'] = obj.__class__.__name__
    return dict_


def import_(session, data, flush=False):
    """ Create a persistent object using information stored in 'data'.
        'data' must be a list of dicts:
            [ {'__class__': 'MyClass', 'attr1': value1, ...}, ...]
    """
    objs = []
    for values in data:
        cls = values.pop('__class__')
        cls = getattr(models, cls)
        if issubclass(cls, models.Setting):
            type_ = session.query(models.SettingType).get(values['type_name'])
            values['type'] = type_

        obj = cls(**values)
        obj = session.merge(obj)
        objs.append(obj)
        if flush:
            session.flush()

    return objs
