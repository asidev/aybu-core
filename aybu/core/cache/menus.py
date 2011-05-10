from collections import deque
from sqlalchemy.orm.exc import DetachedInstanceError
from makako.containers import Storage

from aybu.cms.model.entities import Menu
from aybu.cms.model.meta import dbsession

from proxy import KeyValueCacheProxy, CacheProxy
from exc import IntegrityError
from proxies import LanguagesCacheProxy


class MenusProxy(KeyValueCacheProxy):

    def __new__(cls, prefix="menus"):
        return super(MenusProxy, cls).__new__(cls, prefix)

    def _get_all_keys(self):
        return [unicode(m[0]) for m in
                dbsession.query(Menu.weight).distinct().all()]

    def _get_from_database(self, w):
        return Menu.query.filter(Menu.weight == int(w)).one()

    def _set_value(self, key, value):
        raise IntegrityError("Cannot change menus")

    def __setitem__(self, key, value):
        raise IntegrityError("Cannot change menus")

    def __getitem__(self, key):
        key = unicode(key)
        node = super(MenusProxy, self).__getitem__(key)
        return NodeProxy(node, self)

    def __iter__(self):
        return (self[k] for k in self._keys)

    def clear(self, recurse=True):
        if recurse:
            self.log.debug("Clearing cache for all menus")
            for m in self:
                m.clear()
        super(MenusProxy, self).clear()


class NodeProxy(CacheProxy):
    region_name = "nodes"

    def __new__(cls, node, root=None):

        def add_attrs(obj):
            obj.__node = node
            obj.lang_proxy = LanguagesCacheProxy()
            obj.root = root
            return obj

        obj = super(NodeProxy, cls).__new__(cls, cls.region_name)
        return add_attrs(obj)

    def __getitem__(self, lang):
        lang = self.lang_proxy[lang]
        for ni in self.translations:
            if ni.lang == lang:
                return ni
        raise KeyError(lang)

    def _get_from_database(self, key):
        try:
            self.log.debug("[%s] original key was '%s'", self, key)
            key = key.split("::")[0]
            if key == 'children':
                return self.__node.children
            if key == 'parent':
                return self.__node.parent
            if key == 'path':
                return self.__node.path
            if key == 'translations':
                return list(self.__node.translations)
            if key == 'linked_by':
                return list(self.__node.linked_by)
            if key == 'view':
                return self.__node.view
            if key == 'linked_to':
                return self.__node.linked_to
        except DetachedInstanceError:
            self.log.info("%s readding __node to session", self)
            self.__node = dbsession.merge(self.__node, load=True)
            return self._get_from_database(key)

        self.log.critical("In %s._get_from_database: no key %s", self, key)
        raise ValueError(key)

    def _back_from_cache(self, obj):
        if isinstance(obj, list):
            obj = [super(NodeProxy, self)._back_from_cache(o) for o in obj]
        else:
            obj = super(NodeProxy, self)._back_from_cache(obj)
        return obj

    def _get_from_cache(self, key):
        key = "%s::%d" % (key, self.__node.id)
        return super(NodeProxy, self)._get_from_cache(key)

    def __eq__(self, other):
        if other:
            return self.id == other.id
        return False

    @property
    def linked_by(self):
        return [NodeProxy(c, self.root)
                for c in self._get_from_cache('linked_by')]

    @property
    def type(self):
        return self.__node.type

    @property
    def path(self):
        return [NodeProxy(c, self.root) for c in self._get_from_cache('path')]

    @property
    def id(self):
        return self.__node.id

    @property
    def enabled(self):
        return self.__node.enabled

    @property
    def sitemap_priority(self):
        return self.__node.sitemap_priority

    @property
    def weight(self):
        return self.__node.weight

    @property
    def children(self):
        return [NodeProxy(c, self.root)
                 for c in self._get_from_cache('children')]

    @property
    def parent(self):
        parent = self._get_from_cache('parent')
        if parent is not None:
            return NodeProxy(self._get_from_cache('parent'), self.root)
        return None

    @property
    def translations(self):
        return [NodeInfoProxy(i, self)
                for i in self._get_from_cache('translations')]

    @property
    def view(self):
        return Storage(self._get_from_cache('view').to_dict())

    @property
    def url(self):
        return self.__node.url

    @property
    def linked_to(self):
        return NodeProxy(self._get_from_cache('linked_to'), self.root)

    def __repr__(self):
        v = repr(self.__node)
        return v.replace("Node", "NodeProxy")

    def crawl(self, callback=None):
        queue = deque([self])
        visited = deque()
        while queue:
            parent = queue.popleft()
            if parent in visited:
                continue
            yield parent
            if callback:
                callback(parent)
            visited.append(parent)
            queue.extend(parent.children)

    @property
    def pages(self):
        # we cannot use Page.__class__.__name__ here
        # as it returns EntityMeta :(
        return [p for p in self.crawl() if p.type == "Page"]

    @classmethod
    def clear(cls):
        cls.cachemgr.get_cache(cls.region_name).clear()


class NodeInfoProxy(CacheProxy):
    region_name = 'nodesinfo'

    def __new__(cls, nodeinfo, node):

        def add_attrs(obj):
            obj.lang_proxy = LanguagesCacheProxy()
            obj.node = node
            obj.__nodeinfo = nodeinfo
            for attr in ('label', 'title', 'id', 'url_part', 'meta_description',
                         'head_content', 'content'):
                setattr(obj, attr, getattr(nodeinfo, attr))
            return obj

        obj =  super(NodeInfoProxy, cls).__new__(cls, cls.region_name)
        return add_attrs(obj)

    @classmethod
    def clear(cls):
        NodeProxy.clear()
        cls.cachemgr.get_cache(cls.region_name).clear()

    def _get_from_database(self, key):
        self.log.debug("[%s] Original key was '%s'", self, key)
        key = key.split("::")[0]
        try:
            if key in ('lang', 'keywords', 'files', 'images', 'links', 'url'):
                return getattr(self.__nodeinfo, key)
        except DetachedInstanceError:
            self.__nodeinfo = dbsession.merge(self.__nodeinfo, load=True)
            return getattr(self.__nodeinfo, key)
        raise KeyError(key)

    def _back_from_cache(self, obj):
        if isinstance(obj, list):
            obj = [Storage(
                   super(NodeInfoProxy, self)._back_from_cache(o).to_dict()
                ) for o in obj]
        elif isinstance(obj, basestring) or obj is None:
            return obj
        else:
            obj = Storage(
                super(NodeInfoProxy, self)._back_from_cache(obj).to_dict()
            )
        return obj

    def _get_from_cache(self, key):
        key = "%s::%d" % (key, self.__nodeinfo.id)
        return super(NodeInfoProxy, self)._get_from_cache(key)

    def __getattr__(self, attr):
        try:
            if attr in ('keywords', 'files', 'images', 'links'):
                return self._get_from_cache(attr)
            if attr == "url":
                url = self._get_from_cache(attr)
                #if url and "user" in session \
                #   and "reloading" not in session \
                #   and self.node.type != "ExternalLink":
                #    url = "%s?admin" % url
                return url
            if attr == "lang":
                return self.lang_proxy[self.__nodeinfo.lang]
            if hasattr(self.__nodeinfo, attr):
                return getattr(self.__nodeinfo, attr)
        except DetachedInstanceError:
            self.log.info("%s: Nodeinfo instance is detached: merging back",
                         self)
            self.__nodeinfo = dbsession.merge(self.__nodeinfo, load=True)
            return getattr(self, attr)

        raise AttributeError(attr)

    def __repr__(self):
        v = repr(self.__nodeinfo)
        return v.replace("NodeInfo", "NodeInfoProxy")
