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
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Building the lexer

lexer = lex.lex()

# Phonemes and features

symbols = {}

class Phoneme:
    def __init__(self, plus=set(), minus=set(), ow=True, copy=None):
        self.plus = set()
        self.minus = set()
        if copy is None:
            plus = plus.copy()
            minus = minus.copy()
        else:
            plus = copy.plus.copy()
            minus = copy.minus.copy()
        if ow:
            self.add_ow(plus)
            self.subtract_ow(minus)
        else:
            self.add_ud(plus)
            self.subtract_ud(minus)

    def __repr__(self):
        pluses = ' '.join([('+%s' % plus) for plus in self.plus])
        minuses = ' '.join([('-%s' % minus) for minus in self.minus])
        space = ''
        if len(pluses) and len(minuses):
            space = ' '
        return '[%s%s%s]' % (pluses, space, minuses)

    def add_ud(self, plus):
        if self.minus.intersection(plus):
            sys.stderr.write("Warning: Inconsistent feature update\n")
        else:
            self.plus.update(plus)
        return self

    def subtract_ud(self, minus):
        if self.plus.intersection(minus):
            sys.stderr.write("Warning: Inconsistent feature update\n")
        else:
            self.minus.update(minus)
        return self

    def add_ow(self, plus):
        self.minus.difference_update(plus)
        self.plus.update(plus)
        return self

    def subtract_ow(self, minus):
        self.plus.difference_update(minus)
        self.minus.update(minus)
        return self

    def contradicts(self, other):
        # TODO: This can easily be optimized if necessary.
        return (self.plus.intersection(other.minus) or
                self.minus.intersection(other.plus))

    def matches(self, other):
        return (not (self.plus.symmetric_difference(other.plus) or
                     self.minus.symmetric_difference(other.minus)))

def p_line_feature(p):
    'line : feature COLON new_symbols'
    # None : Phoneme Constant List(String)
    for symbol in list(p[3]):
        if not symbol in symbols: symbols[symbol] = Phoneme()
        symbols[symbol].add_ud(p[1].plus).subtract_ud(p[1].minus)
        print('%s = %s' % (symbol, symbols[symbol]))

def p_line_symbol(p):
    'line : ID EQUALS features'
    # None : String Constant Phoneme
    if not p[1] in symbols: symbols[p[1]] = p[3]
    else: symbols[p[1]].add_ud(p[3].plus).subtract_ud(p[3].minus)
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
    p[1].add_ow(p[2].plus).subtract_ow(p[2].minus)
    p[0] = p[1]

def p_feature_or_phoneme(p):
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
    p[0] = Phoneme(copy=symbols[p[1]])

# Constraints

class Constraint:
    def __init__(self, antecedent, consequent):
        error = False
        if antecedent.contradicts(consequent): error = True
        else:
            for constraint in constraints:
                error = (antecedent.contradicts(constraint.consequent) or
                         consequent.contradicts(constraint.antecedent))
                if error: break
        if error:
            sys.stderr.write('Error: Contradiction of constraints\n')
            self.antecedent = None
            self.consequent = None
        else:
            self.antecedent = Phoneme(copy=antecedent)
            self.consequent = Phoneme(copy=consequent)

    def __repr__(self):
        return '%s %s %s' % (self.antecedent, t_IMPLIEDBY, self.consequent)

def p_line_converse_implication(p):
    'line : feature IMPLIEDBY features'
    print '%s %s %s' % (p[1], t_IMPLIEDBY, p[3])
    #c = add_constraint(p[1], p[3])
    #print(c)

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
