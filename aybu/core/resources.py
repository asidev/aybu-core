import logging
from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound


__all__ = ['Root', 'Capthcha', 'ViewInfo', 'ContactsViewInfo', 'add_view_info']


class Root(object):
    def __init__(self, request):
        from aybu.core.model.entities import Language, Menu
        self.request = request
        self.log = logging.getLogger("%s.%s" % (self.__class__.__module__,
                                                self.__class__.__name__))
        self.log.debug("Starting Traversal for %s", request.path_info)
        self.languages = {l.lang: l
                          for l in Language.query.\
                                   filter(Language.enabled == True).all()}
        self.menus = Menu.query.all()

    def __getitem__(self, part):
        try:
            # we need to use first as 'lang' attribute alone can be not unique
            self.log.debug("Searching for lang '%s'", part)
            lang = self.languages[part]
            self.request.lang = lang
            return NodeTraverser(self.request, lang=lang, parents=self.menus)

        except (KeyError, TypeError):
            self.log.debug("No language '%s' found.", part)
            if part == 'captcha':
                self.log.debug("Found Captcha() for %s", part)
                return Captcha()
            if part == 'admin':
                self.log.debug("Offloading admin to pylons")
                return Admin()
            self.log.debug('Raising keyerror')
            raise


class Captcha(object):
    pass


class Admin(object):
    def __getitem__(self, part):
        # FIXME: this hack is done to make fallback view match every view name
        return self


class NodeTraverser(object):

    def __init__(self, request, lang, parents):
        self.request = request
        self.lang = lang
        self.parents = parents
        self.parents_id = {p.id for p in parents}
        self.log = logging.getLogger("%s.%s" % (self.__class__.__module__,
                                                self.__class__.__name__))

    def __getitem__(self, part):
        from aybu.core.model.entities import Node, NodeInfo
        self.log.debug("Next url part: %s", part)
        url_part = part.replace(".html", "")
        try:
            next_node_q = Node.query.filter(
                                Node.translations.any(
                                    and_(NodeInfo.url_part == url_part,
                                         NodeInfo.lang == self.lang)
                                )
                            ).filter(Node.parent_id.in_(self.parents_id))

            if url_part != part:
                self.log.debug("Url is a leaf, searching a nodeinfo")
                # this is a leaf, so it must be one!
                node = next_node_q.one()
                self.log.debug("Found %s", node[self.lang])
                return ViewInfo(node, self.lang)

            else:
                self.log.debug("Not a leaf: searching for parents")
                parents = next_node_q.all()
                if not parents:
                    raise NoResultFound()
                self.log.debug("Found parents: '%s'", parents)
                return NodeTraverser(self.request, lang=self.lang,
                                     parents=parents)

        except NoResultFound:
            self.log.debug("No Result found for '%s'", part)
            raise KeyError(part)


def add_view_info(cls):
    """ Add cls to available ViewInfo objects """
    ViewInfo._classes[cls.__name__] = cls


class ViewInfo(object):
    """ Represent a match on a NodeInfo, and
        acts as a Factory for specialized classes"""
    _classes = dict()

    def __new__(cls, node, lang):
        classname = "{0}ViewInfo".format(node.view.name.lower().title())
        try:
            kls = cls._classes[classname]
            return super(type(kls), kls).__new__(kls, node, lang)

        except KeyError:
            return super(ViewInfo, cls).__new__(cls, node, lang)

    def __init__(self, node, lang):
        self.node = node
        self.nodeinfo = self.node[lang]
        self.view = self.node.view
        self.lang = lang
        self.log = logging.getLogger("%s.%s" % (self.__class__.__module__,
                                                self.__class__.__name__))
        self.log.debug("Created object for %s (%s) (%s)", self.node,
                                                          self.nodeinfo,
                                                          self.view.name)


class ContactsViewInfo(ViewInfo):
    """ Represent a match for those NodeInfo whose view name is CONTACTS """
    pass


add_view_info(ContactsViewInfo)
