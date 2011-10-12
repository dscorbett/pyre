#! usr/bin/python
# -*- coding: cp1252 -*-

import ply.lex as lex
import ply.yacc as yacc
import re
import sys

# Lexing

tokens = ('TO', 'FROM', 'WHEN', 'BETWEEN',
          'NUMBER', 'ID', 'STAR', 'QUESTION', 'COMMA', 'PIPE',
          'LPAREN', 'RPAREN', 'LSQUARE', 'RSQUARE', 'LCURLY', 'RCURLY',
          'PLUS', 'MINUS', 'ALPHA', 'NALPHA',
          'COLON', 'EQUALS', 'IMPLIEDBY', 'EQUIV', 'LPHONEME', 'RPHONEME')
t_ignore = ' \t'
t_TO = r'>'
t_FROM = r'<'
t_WHEN = r'\/'
t_BETWEEN = r'_'
t_ID = r'[a-zA-Z0-9]+'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LSQUARE = r'\['
t_RSQUARE = r'\]'
t_LCURLY = r'\{'
t_RCURLY = r'\}'
t_PLUS = r'\+'
t_MINUS = r'-'
t_ALPHA = r'@'
t_NALPHA = r'-@'
t_STAR = r'\*'
t_QUESTION = r'\?'
t_COMMA = r','
t_PIPE = r'\|'
t_COLON = r':'
t_EQUALS = r'='
t_IMPLIEDBY = r'<='
t_EQUIV = r'=='
t_LPHONEME = r'`'
t_RPHONEME = r"'"

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_newline(t):
    r'(\n|\r|\f)+'
    t.lexer.lineno += len(t.value)

def t_error(t): # TODO: tailor to my needs
    """Print an error when an illegal character is found."""
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Building the lexer

lexer = lex.lex()

# Phonemes and features

symbols = {}

class Phoneme:
    """
    A wrapper class for a dictionary from features to Booleans.

    A phoneme is a set of signed features. A signed feature is a feature (for
    example, voice) paired with a sign (+ or -). Unspecified features (for
    example, the place of articulation of the Japanese moraic n) are specified
    by their absence from the phoneme.

    The purpose of this wrapper class is to maintain the invariants of
    phonemes, which are specified by constraints.
    """

    def __init__(self, features=dict(), plus=set(), minus=set()):
        """
        Create a new phoneme.

        Optional arguments:
        features : a dictionary from features to Booleans
        plus : a set of positive features
        minus : a set of negative features
        """
        self.features = features.copy()
        self.features.update({f: True for f in plus})
        self.features.update({f: False for f in minus})

    def __str__(self):
        """
        Return an informal representation of this phoneme as a string.

        Features are listed in alphabetical order with a '+' or '-' prefix as
        appropriate.
        """
        signed_strings = []
        for key in sorted(self.features.keys()):
            if self[key]: signed_strings.append('+%s' % key)
            else: signed_strings.append('-' + key)
        return '[%s]' % ' '.join(signed_strings)

    def __eq__(self, other):
        """
        Return whether this phoneme's features equal another's.

        Arguments:
        other : the object to test equality against
        """
        if not isinstance(other, Phoneme): return False
        if len(self.features) != len(other.features): return False
        return self <= other

    def __ne__(self, other):
        """
        Return whether this phoneme does not equal an object.

        Arguments:
        other : the object to test inequality against
        """
        return not self == other

    def __le__(self, other):
        # TODO: doc
        return self.issubset(other)

    def __hash__(self): # Is this useful?
        # TODO: doc
        return (hash(tuple(self.features.keys())) ^
                hash(tuple(self.features.values())))

    def contradicts(self, other):
        """
        Return whether this phoneme contradicts another.

        Phonemes contradict each other when any feature of one appears in the
        other with a different sign.

        Arguments:
        other : the phoneme to compare against
        """
        for feature in self.features.keys():
            if (other.features.has_key(feature) and
                self[feature] != other[feature]):
                return True
        return False

    def edit(self, other):
        """
        Add another phoneme's signed features, unless they contradict.

        Return this phoneme.

        Arguments:
        other : the phoneme to get the new signed features from
        """
        if self.contradicts(other):
            sys.stderr.write("Warning: Inconsistent feature update\n")
        else:
            self.update(other)
        return self

    def update(self, other):
        """
        Add another phoneme's signed features, overwriting in case of conflict.

        Return this phoneme.

        Arguments:
        other : the phoneme to get the new signed features from
        """
        self.features.update(other.features)

    def issubset(self, other):
        """
        Return whether this phoneme is a subset of another.

        A phoneme is a subset of another if every feature of the one appears in
        the other with the same sign.

        Arguments:
        other : the phoneme which might be a superset
        """
        for feature in self.features.keys():
            if other.features.has_key(feature):
                if self[feature] != other[feature]:
                    return False
            else:
                return False
        return True

    def copy(self):
        """Return a copy of this phoneme."""
        return Phoneme(self.features)

    def __getitem__(self, key):
        """
        Return the sign of a feature as a Boolean, or None if it is absent.

        Arguments:
        key : the feature whose sign is wanted
        """
        try:
            return self.features[key]
        except KeyError:
            return None

    def follow_implications(self):
        pass #TODO

def p_line_feature(p):
    'line : feature COLON new_symbols'
    # None : Phoneme Constant List(String)
    for symbol in list(p[3]):
        if not symbol in symbols: symbols[symbol] = Phoneme()
        symbols[symbol].update(p[1])
        print('%s = %s' % (symbol, symbols[symbol]))

def p_line_symbol(p):
    'line : ID EQUALS features'
    # None : String Constant Phoneme
    if not p[1] in symbols: symbols[p[1]] = p[3]
    else: symbols[p[1]].edit(p[3])
    print('%s = %s' % (p[1], symbols[p[1]]))

def p_new_symbols_base(p):
    'new_symbols : ID'
    # List(String) : String
    p[0] = set([p[1]])

def p_new_symbols_recursive(p):
    'new_symbols : new_symbols ID'
    # List(String) : List(String) String
    p[1].add(p[2])
    p[0] = p[1]

def p_features_base(p):
    'features : feature_or_phoneme'
    # Phoneme : Phoneme
    p[0] = p[1]

def p_features_recursive(p):
    'features : features feature_or_phoneme'
    # Phoneme : Phoneme Phoneme
    p[1].update(p[2])
    p[0] = p[1]

def p_feature_or_phoneme(p): # TODO: get rid of this silly token
    '''
    feature_or_phoneme : phoneme
                       | feature
    '''
    # Phoneme : Phoneme
    p[0] = p[1]

def p_feature_plus(p):
    'feature : PLUS ID'
    # Phoneme : Constant String
    p[0] = Phoneme(plus=set([p[2]]))

def p_feature_minus(p):
    'feature : MINUS ID'
    # Phoneme : Constant String
    p[0] = Phoneme(minus=set([p[2]]))

def p_feature(p):
    'feature : ID'
    # Phoneme : String
    p[0] = Phoneme(plus=set([p[1]]))

def p_phoneme(p):
    'phoneme : LPHONEME valid_symbol RPHONEME'
    # Phoneme : Constant Phoneme Constant
    p[0] = p[2]

def p_valid_symbol(p):
    'valid_symbol : ID'
    # Phoneme : String
    if not p[1] in symbols:
        sys.stderr.write('Error: No such phoneme %s%s%s\n' %
                         (t_LPHONEME, p[1], t_RPHONEME))
        raise SyntaxError
    p[0] = symbols[p[1]].copy()

# Constraints

constraints = {}

def add_constraint(key, value):
    """
    Add a new key-value pair to the dictionary of constraints.

    A constraint is only added if it is self-consistent, it is not redundant
    with any previous constraints, and it does not contradict any previous
    constraints. If any previous constraint is found to be redundant with it,
    the previous one is replaced.

    Arguments:
    key : the antecedent phoneme
    value : the consequent phoneme
    """
    if not key.contradicts(value):
        worthwhile = True
        for antecedent in constraints.copy():
            consequent = constraints[antecedent]
            if antecedent <= key and value.contradicts(consequent):
                worthwhile = False
                break
            if antecedent <= key and value <= consequent:
                worthwhile = False
                break
            if key <= antecedent and consequent <= value:
                del constraints[antecedent]
        if worthwhile: constraints[key] = value

# Running the program

parser = yacc.yacc()
while True:
   try:
       s = raw_input('Babel > ')
   except EOFError:
       break
   if not s: continue
   result = parser.parse(s)
   print(result)
