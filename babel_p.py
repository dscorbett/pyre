#! usr/bin/python
# -*- coding: cp1252 -*-

import ply.lex as lex
import ply.yacc as yacc
import re

# Lexing

tokens = ('TO', 'FROM', 'WHEN', 'BETWEEN',
          'NUMBER', 'ID',
          'LPAREN', 'RPAREN', 'LSQUARE', 'RSQUARE', 'LCURLY', 'RCURLY',
          'PLUS', 'MINUS', 'ALPHA', 'NALPHA',
          'STAR', 'QUESTION', 'COMMA', 'PIPE', 'COLON', 'EQUALS')
t_ignore = ' \t'
t_TO = r'>'
t_FROM = r'<'
t_WHEN = r'/'
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

lexer = lex.lex(debug=1)

# Parsing classes and global variables

symbols = {}

class Symbol:
    def __init__(self):
        self.plus = set()
        self.minus = set()

    def __repr__(self):
        pluses = ' '.join([('+%s' % plus) for plus in self.plus])
        minuses = ' '.join([('-%s' % minus) for minus in self.minus])
        space = ''
        if len(pluses) and len(minuses):
            space = ' '
        return '[%s%s%s]' % (pluses, space, minuses)

    def update(self, plus, minus):
        if self.plus.union(plus).intersection(self.minus.union(minus)):
            print "WARNING: Inconsistent feature update"
        else:
            self.plus.update(plus)
            self.plus.update(minus)

    def add(self, plus):
        if self.minus.intersection(plus):
            print "WARNING: Inconsistent feature update"
        else:
            self.plus.update(plus)

    def subtract(self, minus):
        if self.plus.intersection(minus):
            print "WARNING: Inconsistent feature update"
        else:
            self.minus.update(minus)

# Parsing rules

def p_line_feature_minus(p):
    'line : MINUS ID COLON symbols'
    for symbol in list(p[4]):
        if not symbol in symbols: symbols[symbol] = Symbol()
        symbols[symbol].subtract(set([p[2]]))
        print '%s = %s' % (symbol, symbols[symbol])

def p_line_feature_plus(p):
    'line : PLUS ID COLON symbols'
    for symbol in list(p[4]):
        if not symbol in symbols: symbols[symbol] = Symbol()
        symbols[symbol].add(set([p[2]]))
        print '%s = %s' % (symbol, symbols[symbol])

def p_line_feature(p):
    'line : ID COLON symbols'
    for symbol in list(p[3]):
        if not symbol in symbols: symbols[symbol] = Symbol()
        symbols[symbol].add(set([p[1]]))
        print '%s = %s' % (symbol, symbols[symbol])

def p_symbols_base(p):
    'symbols : ID'
    p[0] = set([p[1]])

def p_symbols_recursive(p):
    'symbols : symbols ID'
    p[1].add(p[2])
    p[0] = p[1]

def p_line_symbol(p):
    'line : ID EQUALS features'
    if not p[1] in symbols: symbols[p[1]] = Symbol()
    (plus, minus) = p[3]
    for feature in plus: symbols[p[1]].add(set([feature]))
    for feature in minus: symbols[p[1]].subtract(set([feature]))
    print '%s = %s' % (p[1], symbols[p[1]])

def p_features_base_minus(p):
    'features : MINUS ID'
    p[0] = ([], [p[2]])

def p_features_base_plus(p):
    'features : PLUS ID'
    p[0] = ([p[2]], [])

def p_features_base(p):
    'features : ID'
    p[0] = ([p[1]], [])

def p_features_recursive(p):
    'features : features ID'
    p[1][0].append(p[2])
    p[0] = p[1]

def p_features_recursive_signed(p):
    'features : features MINUS ID'
    p[1][1].append(p[3])
    p[0] = p[1]

def p_features_recursive_plus(p):
    'features : features PLUS ID'
    p[1][0].append(p[3])
    p[0] = p[1]

# Running the program

parser = yacc.yacc()
while True:
   try:
       s = raw_input('What wouldstow lear me? ')
   except EOFError:
       break
   if not s: continue
   result = parser.parse(s)
   print result
