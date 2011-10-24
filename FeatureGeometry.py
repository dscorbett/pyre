#! /usr/bin/env python

class FeatureGeometry:
    def __init__(self):
        self._geometry = {}

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self._geometry)

    def __getitem__(self, key):
        return self._geometry[key]

    def __contains__(self, key):
        return key in self._geometry

    def add(self, name, values='+', parent=None, children=[]):
        """
        Add a new feature to this feature geometry.

        Arguments:
        name : the name of the feature
        Optional arguments:
        values : the set of legal values of the feature, as strings
        parent : the name of the parent feature, if it already exist
        children : the set of the feature's children, if they already exist
        """
        if name in self._geometry:
            self._geometry[name].values = set(values)
        else:
            self._geometry.update({name: _Feature(values)})
        self.add_parent(name, parent)
        self.add_children(name, children)

    def add_parent(self, node, parent):
        if not node in self._geometry: return False
        if not parent in self._geometry or self.is_ancestor(node, parent):
           return False
        self._geometry[node].parent = self._geometry[parent]
        self._geometry[parent].children.add(self._geometry[node])
        return True

    def add_children(self, node, children):
        if not node in self._geometry: return False
        for child in children:
            if not child in self._geometry or self.is_ancestor(child, node):
                return False
        for child in children:
            self._geometry[child].parent = self._geometry[node]
            self._geometry[node].children.add(self._geometry[child])
        return True

    def parent(self, node):
        return self._geometry[node].parent

    def children(self, node):
        return self._geometry[node].children

    def is_ancestor(self, a, b):
        a = self._geometry[a]
        b = self._geometry[b]
        while not b.parent is None:
            if b.parent == a: return True
            b = b.parent
        return False

class _Feature:
    """
    A Feature represents a distinctive feature, such as [voice] or [sonorant].
    A Feature can have any number of possible values. For example, [POA] (i.e.
    [place of articulation]) might have values 'labial', 'coronal', 'dorsal',
    and 'radical'.
    """
    def __init__(self, values=[]):
        self.values = set(values)
        self.parent = None
        self.children = set()

    def __str__(self):
        return '%s#%s#' % (self.values, self.parent)

    def __repr__(self):
        return str(self)

# Testing

features = FeatureGeometry()
features.add('root')

features.add('laryngeal', parent='root')
features.add('supralaryngeal', parent='root')

features.add('voice', '+-', 'laryngeal')
features.add('manner', parent='supralaryngeal')
features.add('place', ['lab', 'cor', 'dors', 'phar'], parent='supralaryngeal')

features.add('nasal', parent='manner')
