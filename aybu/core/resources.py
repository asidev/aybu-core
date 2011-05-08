import logging
from sqlalchemy import and_
from sqlalchemy.orm.exc import NoResultFound


class Root(object):
    def __init__(self, request):
        from aybu.core.model.entities import Language, Menu
        self.request = request
        self.log = logging.getLogger("%s.%s" % (self.__class__.__module__,
                                                self.__class__.__name__))
        self.log.debug("Starting Traversal for %s", request.path_info)
        self.languages = { l.lang: l
                            for l in Language.query.\
                                      filter(Language.enabled == True).all() }
        self.menus = Menu.query.all()

    def __getitem__(self, part):
        try:
            # we need to use first as 'lang' attribute alone can be not unique
            self.log.debug("Searching for lang '%s'", part)
            lang = self.languages[part]
            self.request.lang = lang
            return NodeTraverser(self.request, lang=lang, parents=self.menus)

        except NoResultFound:
            return KeyError(part)


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
                nodeinfo = next_node_q.one()[self.lang]
                self.log.debug("Found %s", nodeinfo)
                return nodeinfo

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

