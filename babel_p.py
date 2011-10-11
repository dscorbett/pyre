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
          'COLON', 'EQUALS', 'LPHONEME', 'RPHONEME')
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

    def add(self, plus):
        if self.minus.intersection(plus):
            sys.stderr.write("Warning: Inconsistent feature update")
        else:
            self.plus.update(plus)
        return self

    def subtract(self, minus):
        if self.plus.intersection(minus):
            sys.stderr.write("Warning: Inconsistent feature update")
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

# Parsing rules

def p_line_feature_minus(p):
    'line : MINUS ID COLON symbols'
    for symbol in list(p[4]):
        if not symbol in symbols: symbols[symbol] = Symbol()
        symbols[symbol].subtract(set([p[2]]))
        print('%s = %s' % (symbol, symbols[symbol]))

def p_line_feature_plus(p):
    'line : PLUS ID COLON symbols'
    for symbol in list(p[4]):
        if not symbol in symbols: symbols[symbol] = Symbol()
        symbols[symbol].add(set([p[2]]))
        print('%s = %s' % (symbol, symbols[symbol]))

def p_line_feature(p):
    'line : ID COLON symbols'
    for symbol in list(p[3]):
        if not symbol in symbols: symbols[symbol] = Symbol()
        symbols[symbol].add(set([p[1]]))
        print('%s = %s' % (symbol, symbols[symbol]))

def p_symbols_base(p):
    'symbols : ID'
    p[0] = set([p[1]])

def p_symbols_recursive(p):
    'symbols : symbols ID'
    p[1].add(p[2])
    p[0] = p[1]

def p_line_symbol(p):
    'line : ID EQUALS features'
    if not p[1] in symbols: symbols[p[1]] = p[3]
    else: symbols[p[1]].add(p[3].plus).subtract(p[3].minus)
    print('%s = %s' % (p[1], symbols[p[1]]))

def p_features_base(p):
    'features : feature'
    p[0] = p[1]

def p_features_recursive(p):
    'features : features feature'
    p[1].add_ow(p[2].plus).subtract_ow(p[2].minus)
    p[0] = p[1]

def p_feature(p):
    'feature : ID'
    p[0] = Symbol()
    p[0].add_ow(set([p[1]]))

def p_feature_plus(p):
    'feature : PLUS ID'
    p[0] = Symbol()
    p[0].add_ow(set([p[2]]))

def p_feature_minus(p):
    'feature : MINUS ID'
    p[0] = Symbol()
    p[0].subtract_ow(set([p[2]]))

def p_feature_phoneme(p):
    'feature : LPHONEME symbol RPHONEME'
    p[0] = p[2]

def p_symbol(p):
    'symbol : ID'
    if not p[1] in symbols:
        sys.stderr.write('Error: No such phoneme %s%s%s' %
                         (t_LPHONEME, p[1], t_RPHONEME))
        raise SyntaxError
    p[0] = Symbol()
    p[0].add_ow(symbols[p[1]].plus).subtract_ow(symbols[p[1]].minus)

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
