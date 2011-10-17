#! /usr/bin/env python

class Feature:
    """
    A Feature represents a distinctive feature, such as [voice] or [sonorant].
    A Feature can have any number of possible values. For example, [POA] (i.e.
    [place of articulation]) could have values 'labial', 'coronal', 'dorsal',
    and 'radical'.
    """
    def __init__(self, values=set()):
        self._values = set(values)

    def __eq__(self, other):
        return isinstance(other, Feature) and self._values == other._values
    
    def __hash__(self):
        return hash(frozenset(self._values))

    def __repr__(self):
        return 'Feature(%s)' % self._values

    def add(self, value):
        self._values.add(value)
        return self

    def update(self, values):
        self._values.update(values)
        return self

    def contains(self, value):
        return value in self._values

    def discard(self, value):
        self._values.discard(value)
        return self

    def clear(self):
        self._values.clear()
        return self

class Phoneme:
    """
    A Phoneme is a mapping of features to values. No feature may have more than
    one value; however, a feature may be associated with no value.
    """
    def __init__(self, features={}):
        for f in features:
            if not f.contains(features[f]):
                raise StandardError('Illegal value %s' % features[f])
        self._features = dict(features)

    def __eq__(self, other):
        return isinstance(other, Phoneme) and other._features == self._features

    def __hash__(self):
        return hash(tuple(self._features.items()))

    def __getitem__(self, key):
        return self._features[key]
    
    def __repr__(self):
        return 'Phoneme(%s)' % self._features

    def contains(self, feature):
        return feature in self._features

    def update(self, key, value):
        self._features.update({key: value})
        return self

    def remove(self, key):
        del self._features[key]
        return self

class Alphabet:
    """
    An Alphabet is a mapping from single-character symbols to phonemes.
    """
    def __init__(self, symbols={}, placeholder='*'):
        self._symbols = dict(symbols)
        self._phonemes = dict([[ph, s] for s, ph in symbols.items()])
        self.placeholder = placeholder

    def __getitem__(self, key):
        return self._symbols[key]

    def __repr__(self):
        return 'Alphabet(%s)' % self._symbols

    def contains_symbol(self, symbol):
        return symbol in self._symbols

    def contains_feature(self, feature):
        return feature in self._symbols.values()

    def update(self, symbol, phoneme):
        self._symbols.update({symbol: phoneme})
        self._phonemes.update({phoneme: symbol})
        return self

    def delete(self, symbol):
        del self._symbols[symbol]
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
            if char in self._symbols:
                features.append(self._symbols[char])
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
        return ''.join(self._phonemes[phm] if phm in self._phonemes else
                       self.placeholder for phm in phonemes)

universal_alphabet = Alphabet()

# Testing

nasal = Feature('+')
voice = Feature('+-')
poa = Feature(['lab', 'cor', 'dors', 'rad'])

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
