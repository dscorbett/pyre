#! /usr/bin/env python

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
