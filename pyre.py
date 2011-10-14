#! /usr/bin/env python
# -*- coding: cp1252 -*-

import ply.lex as lex
import ply.yacc as yacc
import re
import sys

# Lexing

tokens = ('RANG', 'LANG', 'SOL', 'LOWBAR',
          'NUMBER', 'ID', 'AST', 'QUEST', 'COMMA', 'VERT',
          'LPAR', 'RPAR', 'LSQB', 'RSQB', 'LCUB', 'RCUB',
          'PLUS', 'MINUS', 'ALPHA', 'NALPHA',
          'EQUALS', 'COLON', 'RARR', 'LARR', 'EQUIV')
t_ignore = ' \t'
t_RANG = r'>'
t_LANG = r'<'
t_SOL = r'\/'
t_LOWBAR = r'_'
t_ID = r"[a-zA-Z0-9._']+"
t_LPAR = r'\('
t_RPAR = r'\)'
t_LSQB = r'\['
t_RSQB = r'\]'
t_LCUB = r'\{'
t_RCUB = r'\}'
t_ALPHA = r'@'
t_NALPHA = r'-@'
t_AST = r'\*'
t_QUEST = r'\?'
t_COMMA = r','
t_VERT = r'\|'
t_EQUALS = r'='
t_COLON = r':'
t_RARR = r'=>'
t_LARR = r'<='
t_EQUIV = r'=='

def t_PLUS(t):
    r'\+'
    t.value = True
    return t

def t_MINUS(t):
    r'-'
    t.value = False
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_newline(t):
    r'(\n|\r|\f)+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    """Print an error when an illegal character is found."""
    sys.stderr.write("Warning: Illegal character '%s'\n" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex(debug=True)

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

    def __repr__(self):
        """Return a formal representation of this phoneme as a string."""
        return 'Phoneme(%s)' % self.features
    
    def __str__(self):
        """
        Return an informal representation of this phoneme as a string.

        Features are listed in alphabetical order with a '+' or '-' prefix as
        appropriate.
        """
        signed_strings = []
        for key in sorted(self.features.keys()):
            if self[key]: signed_strings.append('+%s' % key)
            else: signed_strings.append('-%s' % key)
        return '[%s]' % ' '.join(signed_strings)

    def __hash__(self):
        """Return a hash code for this phoneme."""
        return (hash(tuple(self.features.keys())) ^
                hash(tuple(self.features.values())))

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
        """
        Return whether this phoneme is a subset of another phoneme.

        A phoneme is a subset of another if every feature of the one appears in
        the other with the same sign.

        Arguments:
        other : the phoneme which might be a superset
        """
        if not isinstance(other, Phoneme):
            raise TypeError('can only compare to a Phoneme')
        for feature in self.features.keys():
            if feature in other.features:
                if self[feature] != other[feature]:
                    return False
            else:
                return False
        return True

    def __lt__(self, other):
        return self <= other and len(self.features) != len(other.features)

    def __ge__(self, other):
        return other <= self

    def __gt__(self, other):
        return other <= self and len(self.features) != len(other.features)

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

    def contradicts(self, other):
        """
        Return whether this phoneme contradicts another.

        Phonemes contradict each other when any feature of one appears in the
        other with a different sign.

        Arguments:
        other : the phoneme to compare against
        """
        return self.contradictsi(other.features)

    def contradictsi(self, features):
        """
        Return whether this phoneme contradicts a set of signed features.

        A phoneme contradicts a set of signed features when any feature of the
        phoneme appears in the set with a different sign.

        Arguments:
        features : the dictionary of signed features
        """
        for feature in self.features.keys():
            if feature in features and self[feature] != features[feature]:
                return True
        return False

    def edit(self, other):
        """
        Add another phoneme's signed features, unless any contradict.

        Return this phoneme.

        Arguments:
        other : the phoneme to get the new signed features from
        """
        return self.editi(other.features)

    def editi(self, features):
        """
        Add some signed features, unless any contradict.

        Return this phoneme.

        Arguments:
        features : the dictionary of signed features
        """
        if self.contradictsi(features):
            sys.stderr.write("Warning: Inconsistent feature update\n")
        else:
            self.updatei(features)
        return self

    def update(self, other):
        """
        Add another phoneme's signed features, overwriting in case of conflict.

        Return this phoneme.

        Arguments:
        other : the phoneme to get the new signed features from
        """
        return self.updatei(other.features)

    def updatei(self, features):
        """
        Add some signed features, overwriting in case of conflict.

        Return this phoneme.

        Arguments:
        features : the dictionary of signed features
        """
        new = self.copy()
        new.features.update(features)
        if new.follows_constraints(): self.features = new.features
        return self

    def copy(self):
        """Return a copy of this phoneme."""
        return Phoneme(self.features)

    def follows_constraints(self):
        """
        Return whether this phoneme's features do not violate any constraints.

        As a side effect, update this phoneme with any features implied by
        constraints.
        """
        for constraint in constraints:
            if constraint <= self:
                if self.contradicts(constraints[constraint]):
                    sys.stderr.write('Error: the phoneme %s violates that '
                                     'constraint!\n' % self)
                    return False
                else:
                    for feature in constraints[constraint].features:
                        self.features.update(
                            {feature: constraints[constraint][feature]})
        return True

def p_error(p):
    """Fail, and go to the next line."""
    try:
        sys.stderr.write('Syntax error on line %d on token %s\n' %
                         (p.lexer.lineno, p.type))
    except AttributeError:
        sys.stderr.write('Unexpected EOL\n')
    while True:
        tok = yacc.token()
        if not tok: break
    yacc.restart()

def p_line_new_features_ambiguous(p):
    'line : new_symbols COLON new_symbols'
    # None : Set(String) Constant Set(String)
    features = {f: True for f in p[1]}
    for symbol in p[3]:
        if not symbol in symbols: symbols[symbol] = Phoneme()
        symbols[symbol].editi(features)
        print('%s = %s' % (symbol, symbols[symbol]))

def p_line_new_features(p):
    'line : features COLON new_symbols'
    # None : Phoneme Constant Set(String)
    for symbol in p[3]:
        if not symbol in symbols: symbols[symbol] = Phoneme()
        symbols[symbol].edit(p[1])
        print('%s = %s' % (symbol, symbols[symbol]))

def p_line_new_phonemes_ambiguous(p):
    'line : new_symbols EQUALS new_symbols'
    # None : Set(String) Constant Set(String)
    features = {f: True for f in p[3]}
    for symbol in p[1]:
        if not symbol in symbols: symbols[symbol] = Phoneme()
        symbols[symbol].editi(features)
        print('%s = %s' % (symbol, symbols[symbol]))

def p_line_new_phonemes(p):
    'line : new_symbols EQUALS features'
    # None : Set(String) Constant Phoneme
    for symbol in p[1]:
        if not symbol in symbols: symbols[symbol] = Phoneme()
        symbols[symbol].edit(p[3])
        print('%s = %s' % (symbol, symbols[symbol]))

def p_new_symbols_base(p):
    'new_symbols : ID'
    # Set(String) : String
    p[0] = set([p[1]])

def p_new_symbols_recursive(p):
    'new_symbols : new_symbols ID'
    # List(String) : Set(String) String
    p[1].add(p[2])
    p[0] = p[1]

def p_features_base(p):
    '''
    features : phoneme
             | feature
    '''
    # Phoneme : Phoneme
    p[0] = p[1]

def p_features_recursive(p):
    '''
    features : features phoneme
             | features feature
    '''
    # Phoneme : Phoneme Phoneme
    p[1].update(p[2])
    p[0] = p[1]

def p_features_recursive_ambiguous(p):
    '''
    features : new_symbols feature
             | new_symbols phoneme
    '''
    # Phoneme : Set(String) Phoneme
    p[2].updatei({f: True for f in p[1]})
    p[0] = p[2]

def p_features_recursive_ambiguous(p):
    'features : features ID'
    # Phoneme : Phoneme String
    p[1].updatei({p[2]: True})
    p[0] = p[1]

def p_feature(p):
    '''
    feature : PLUS ID
            | MINUS ID
    '''
    # Phoneme : Boolean String
    p[0] = Phoneme({p[2]: p[1]})

def p_phoneme(p):
    'phoneme : SOL valid_phoneme SOL'
    # Phoneme : Constant Phoneme Constant
    p[0] = p[2]

def p_valid_symbol(p):
    'valid_phoneme : ID'
    # Phoneme : String
    if not p[1] in symbols:
        sys.stderr.write('Error: No such phoneme /%s/\n' % p[1])
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
            #if antecedent <= key and value.contradicts(consequent):
            #   sys.stderr.write('%s <= %s and %s.contradicts(%s)\n' %
            #                    (antecedent, key, value, consequent))
            #   worthwhile = False
            #   break
            if antecedent <= key and value <= consequent:
                #print('%s <= %s and %s <= %s' %
                #      (antecedent, key, value, consequent))
                worthwhile = False
                break
            if key <= antecedent and consequent <= value:
                #print('%s <= %s and %s <= %s' %
                #      (key, antecedent, consequent, value))
                del constraints[antecedent]
        if worthwhile:
            if key in constraints: constraints[key].edit(value)
            else: constraints[key] = value

def p_implication_ambiguous_lr(p):
    'line : new_symbols RARR new_symbols'
    # None : Set(String) Constant Set(String)
    add_constraint(Phoneme({f: True for f in p[1]}),
                   Phoneme({f: True for f in p[3]}))
    print(constraints)

def p_implication_ambiguous_l(p):
    'line : new_symbols RARR features'
    # None : Set(String) Constant Phoneme
    add_constraint(Phoneme({f: True for f in p[1]}), p[3])
    print(constraints)

def p_implication_ambiguous_r(p):
    'line : features RARR new_symbols'
    # None : Phoneme Constant Set(String)
    add_constraint(p[1], Phoneme({f: True for f in p[3]}))
    print(constraints)

def p_implication(p):
    'line : features RARR features'
    # None : Phoneme Constant Phoneme
    add_constraint(p[1], p[3])
    print(constraints)

def p_converse_implication_ambiguous_lr(p):
    'line : new_symbols LARR new_symbols'
    # None : Set(String) Constant Set(String)
    add_constraint(Phoneme({f: True for f in p[3]}),
                   Phoneme({f: True for f in p[1]}))
    print(constraints)

def p_converse_implication_ambiguous_l(p):
    'line : new_symbols LARR features'
    # None : Set(String) Constant Phoneme
    add_constraint(p[3], Phoneme({f: True for f in p[1]}))
    print(constraints)

def p_converse_implication_ambiguous_r(p):
    'line : features LARR new_symbols'
    # None : Phoneme Constant Set(String)
    add_constraint(Phoneme({f: True for f in p[3]}), p[1])
    print(constraints)

def p_converse_implication(p):
    'line : features LARR features'
    # None : Phoneme Constant Phoneme
    add_constraint(p[3], p[1])
    print(constraints)

# Running the program

parser = yacc.yacc(start='line')
while True:
    try: s = raw_input('> ')
    except EOFError: break
    if not s: continue
    result = parser.parse(s)
    print(result)
