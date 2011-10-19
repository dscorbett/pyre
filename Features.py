#! /usr/bin/env python

class Node:
    def __init__(self):
        self._hierarchy = {}

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '#%s#' % str(self._hierarchy)

    def __getitem__(self, key):
        return self._hierarchy[key]

    def add(self, child):
        if child in self._hierarchy:
            raise StandardError('The child is already present in the '
                                'hierarchy.')
        self._hierarchy.update({child: self})
        try:
            self._hierarchy.update(child._hierarchy)
        except AttributeError:
            pass

class Feature(Node):
    """
    A Feature represents a distinctive feature, such as [voice] or [sonorant].
    A Feature can have any number of possible values. For example, [POA] (i.e.
    [place of articulation]) could have values 'labial', 'coronal', 'dorsal',
    and 'radical'.
    """
    def __init__(self, values=set()):
        self.values = set(values)

    def __repr__(self):
        return 'Feature(%s)' % self.values

class Phoneme:
    """
    A Phoneme is a mapping of features to values. No feature may have more than
    one value; however, a feature may be associated with no value.
    """
    def __init__(self, features={}):
        for f in features:
            if not f.contains(features[f]):
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

# Testing

root = Node()
laryngeal = Node()
supralaryngeal = Node()
manner = Node()
place = Node()

nasal = Feature('+')
voice = Feature('+-')
coronal = Feature('+-~') # [~coronal] is just for testing.

root.add(laryngeal)
root.add(supralaryngeal)
laryngeal.add(voice)
supralaryngeal.add(manner)
supralaryngeal.add(place)
manner.add(nasal)
place.add(coronal)
"""
m = Phoneme({nasal: '+', voice: '+', poa: 'lab'})
n = Phoneme({nasal: '+', voice: '+', poa: 'cor'})
ng = Phoneme({nasal: '+', voice: '+', poa: 'dors'})
b = Phoneme({voice: '+', poa: 'lab'})
d = Phoneme({voice: '+', poa: 'cor'})
g = Phoneme({voice: '+', poa: 'dors'})
p = Phoneme({voice: '-', poa: 'lab'})
t = Phoneme({voice: '-', poa: 'cor'})
k = Phoneme({voice: '-', poa: 'dors'})
gs = Phoneme({voice: '-', poa: 'rad'})

sampa = Alphabet({'m': m, 'n': n, 'N': ng, 'b': b, 'd': d, 'g': g, 'p': p,
                  't': t, 'k': k, '?': gs})
other = Alphabet({'M': m, 'N': n, '~': ng, 'B': b, 'D': d, 'G': g, 'P': p,
                  'T': t, 'K': k, "'": gs})
"""
