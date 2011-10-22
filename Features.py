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

class Phoneme:
    """
    A Phoneme is a mapping of features to values. No feature may have more than
    one value; however, a feature may be associated with no value.
    """
    def __init__(self, features={}):
        for f in features:
            if not features[f] in f.values:
                raise StandardError('Illegal value %s' % features[f])
        self.features = dict(features)

    def __eq__(self, other):
        try:
            return other.features == self.features
        except AttributeError:
            return False

    def __hash__(self):
        return hash(tuple(self.features.items()))

    def __getitem__(self, key):
        return self.features[key]
    
    def __repr__(self):
        return 'Phoneme(%s)' % self.features

class Alphabet:
    """
    An Alphabet is a mapping from single-character symbols to phonemes.
    """
    def __init__(self, symbols={}, placeholder='*'):
        self.symbols = dict(symbols)
        self.phonemes = dict([[ph, s] for s, ph in symbols.items()])
        self.placeholder = placeholder

    def __getitem__(self, key):
        return self.symbols[key]

    def __repr__(self):
        return 'Alphabet(%s)' % self.symbols

    def contains_symbol(self, symbol):
        return symbol in self.symbols

    def contains_feature(self, feature):
        return feature in self.symbols.values()

    def update(self, symbol, phoneme):
        self.symbols.update({symbol: phoneme})
        self.phonemes.update({phoneme: symbol})
        return self

    def parse(self, string):
        """
        Convert a string into a list of phonemes by interpreting every
        character in the string as a symbol in this alphabet.

        Arguments:
        string : a string to parse
        """
        features = []
        for char in string:
            if char in self.symbols:
                features.append(self.symbols[char])
            else:
                raise StandardError('The symbol <%s> is not part of this '
                                    'alphabet' % char)
        return features

    def symbolize(self, phonemes):
        """
        Convert a list of phonemes into a string by finding the appropriate
        symbol in this alphabet for each phoneme's value.

        Arguments:
        phonemes : a list of phonemes
        """
        return ''.join(self.phonemes[phm] if phm in self.phonemes else
                       self.placeholder for phm in phonemes)

universal_alphabet = Alphabet()

"""
m = Phoneme({nasal: '+', voice: '+', labial: '+'})
n = Phoneme({nasal: '+', voice: '+', labial: '-'})
ng = Phoneme({nasal: '+', voice: '+', labial: '~'})
b = Phoneme({voice: '+', labial: '+'})
d = Phoneme({voice: '+', labial: '-'})
g = Phoneme({voice: '+', labial: '~'})
p = Phoneme({voice: '-', labial: '+'})
t = Phoneme({voice: '-', labial: '-'})
k = Phoneme({voice: '-', labial: '~'})
gs = Phoneme({voice: '-', labial: '~'})

sampa = Alphabet({'m': m, 'n': n, 'N': ng, 'b': b, 'd': d, 'g': g, 'p': p,
                  't': t, 'k': k, '?': gs})
other = Alphabet({'M': m, 'N': n, '~': ng, 'B': b, 'D': d, 'G': g, 'P': p,
                  'T': t, 'K': k, "'": gs})
"""
