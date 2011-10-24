#! /usr/bin/env python

from FeatureGeometry import FeatureGeometry
from FeatureGeometry import features as fg

class Segment:
    """
    A Segment is a mapping of features to values. No feature may have more than
    one value; however, a feature may be unspecified.
    """
    def __init__(self, geometry, features={}, segments=[]):
        self.geometry = geometry
        self.features = {}
        self.segments = []
        for f in features:
            self.add_feature(f, features[f])
        for s in segments:
            self.add_segment(s, len(self.segments))

    def __eq__(self, other):
        try:
            return (other.features == self.features and
                    other.segments == self.segments and
                    other.geometry == self.geometry)
        except AttributeError:
            return False

    def __hash__(self):
        return hash(tuple(self.features.items()))

    def __getitem__(self, key):
        try:
            return self.features[key]
        except:
            return self.segments[key]

    def __str__(self, indent=0):
        s = []
        for f in self.features:
            s.append('%s[%s %s]' % (' ' * indent, f, self.features[f]))
        s = '\n'.join(s)
        i = 0
        for seg in self.segments:
            s += '\n%sSegment %s:' % (' ' * indent, i)
            s += '\n%s' % seg.__str__(indent + 1)
            i += 1
        return s

    def add_feature(self, feature, value):
        if not feature in self.geometry:
            raise StandardError('Illegal feature [%s]' % feature)
        if not value in self.geometry[feature].values:
            raise StandardError("Illegal value '%s'" % value)
        self.features.update({feature: value})

    def add_segment(self, segment, index):
        self.segments[index:index] = [segment]

    def add(self, features={}, segments=[], index=None):
        """
        Add a new segment to this word at the given index. If no index is
        provided, it appends the new segment to the end.

        Arguments:
        features : a mapping from features to values (strings)
        Optional arguments:
        index : the numerical index, starting at 0, of the new segment
        """
        segment = Segment(self.geometry, features, segments)
        if segment.geometry != self.geometry:
            raise StandardError('Different geometries are incompatible')
        if index is None: index = len(self.segments)
        self.add_segment(segment, index)

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
