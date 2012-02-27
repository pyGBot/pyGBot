##
##    pyGBot - Versatile IRC Bot
##    Copyright (C) 2008 Morgan Lokhorst-Blight, Alex Soborov
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##
import collections, math, operator, re, string
from random import randint
from sys import exc_info
from pyGBot.Plugins.system.Commands import BaseCommand
from pyGBot.Plugins.system.Auth import AuthLevels as AL

VALID_ID = re.compile('[a-zA-Z$_][a-zA-Z0-9$_]*$')

BASIC_TOKENS = [
    (2, ['**']),
    (1, ['+', '-', '*', '/', '%', 'd', '^', '(', ')', ',']),
]

class Token(object):
    def __init__(self, kind, value):
        self.value = value
        self.kind = kind

    @property
    def is_unary(self):
        return self.kind in ['-']
    
    @property
    def is_roll(self):
        return self.kind in ['d']

    @property
    def is_exponential(self):
        return self.kind in ['**', '^']

    @property
    def is_multiplicative(self):
        return self.kind in ['*', '/', '%']

    @property
    def is_additive(self):
        return self.kind in ['+', '-']

BinOp = collections.namedtuple('BinOp', ('op', 'lhs', 'rhs'))
UnaryOp = collections.namedtuple('UnaryOp', ('op', 'rhs'))
FunctionCall = collections.namedtuple('FunctionCall', ('name', 'args'))
Constant = collections.namedtuple('Constant', 'name')

class Lexer(object):
    def __init__(self, stream):
        self.current = 0
        self.stream = stream

    def chew(self, ignore_whitespace=True):
        v = self.stream[self.current]
        self.current += 1

        while ignore_whitespace and v in ' \r\n\t':
            v = self.stream[self.current]
            self.current += 1

        return v

    def unchew(self):
        self.current -= 1

    def peek(self):
        return self.stream[self.current]

    def peek_string(self, amount=1, first_char_chewed=True):
        offset = -1 if first_char_chewed else 0
        return self.stream[self.current+offset:self.current+offset+amount]

    def identifier(self, start):
        cache = start
        while True:
            try:
                char = self.chew()
            except IndexError:
                return cache

            cache += char

            if not VALID_ID.match(cache):
                # put back the last token that didn't match
                # and strip it from the results
                self.unchew()
                return cache[:-1]

    def numexp(self, start):
        val = start
        sign = True
        while True:
            try:
                char = self.chew()
            except IndexError:
                return val

            if char in string.digits:
                val += char
            elif sign and char in '+-':
                val += char
            else:
                # put the token back
                self.unchew()
                return val
            sign = False
        return float(val)

    def numdec(self, start):
        val = start
        while True:
            try:
                char = self.chew()
            except IndexError:
                return val

            if char in string.digits:
                val += char
            elif char in 'eE':
                val += char
            else:
                # put the token back
                self.unchew()
                return val
        return val

    def number(self, start):
        val = start
        while True:
            try:
                char = self.chew()
            except IndexError:
                return int(val, 10)

            if char in string.digits:
                val += char
            elif char == '.':
                return float(self.numdec(val + char))
            elif char in 'eE':
                return float(self.numexp(val + char))
            else:
                self.unchew()
                return int(val, 10)

    def __iter__(self):
        return self

    def next(self):
        while True:
            try:
                char = self.chew()
            except IndexError:
                raise StopIteration

            if char in string.digits:
                return Token('number', self.number(char))

            for length, tokens in BASIC_TOKENS:
                lexeme = self.peek_string(length)
                if lexeme in tokens:
                    self.current += length - 1
                    return Token(lexeme, lexeme)

            return Token('identifier', self.identifier(char))

class Parser(object):
    def __init__(self, tokens):
        self.current = 0
        self.tokens = tokens

    def has_next(self):
        return self.current < len(self.tokens)

    def peek(self):
        try:
            return self.tokens[self.current]
        except IndexError:
            return Token('eos', None)

    def chew(self):
        v = self.peek()
        self.current += 1
        return v

    def unchew(self):
        self.current -= 1
    

    def expects_any(self, kinds):
        got = self.chew()
        if got.kind not in kinds:
            raise SyntaxError("Wanted a kind in %r, got %r" % (kinds, got.kind))
        return got

    def expects(self, kind):
        return self.expects_any((kind,))

    def hd(self):
        return self.peek().kind

    def atom(self):
        tok = self.chew()
        if tok.kind == 'number':
            return tok
        elif tok.kind == '(':
            return self.paren_expression()
        elif tok.kind == 'identifier':
            if self.hd() == '(':
                return self.function_call(tok)
            else:
                return Constant(tok)
        raise SyntaxError

    def paren_expression(self):
        # lparen chewed
        expr = self.toplevel()
        self.expects(')')
        return expr

    def arglist(self):
        arglist = []
        while self.hd() != ')':
            arglist.append(self.toplevel())
            if self.hd() != ',':
                break

        return arglist

    def function_call(self, tok):
        self.expects('(')
        arglist = self.arglist()
        self.expects(')')
        return FunctionCall(tok, arglist)

    def unary_expression(self):
        if self.peek().is_unary:
            tok = self.chew()
            return UnaryOp(tok, self.unary_expression())
        else:
            return self.atom()
        
    def roll_expression(self):
        expr = self.unary_expression()
        while self.peek().is_roll:
            tok = self.chew()
            expr = BinOp(tok, expr, self.unary_expression())
        return expr

    def exponential_expression(self):
        expr = self.roll_expression()
        while self.peek().is_exponential:
            tok = self.chew()
            expr = BinOp(tok, expr, self.roll_expression())
        return expr

    def multiplicative_expression(self):
        expr = self.exponential_expression()
        while self.peek().is_multiplicative:
            tok = self.chew()
            expr = BinOp(tok, expr, self.exponential_expression())
        return expr

    def additive_expression(self):
        expr = self.multiplicative_expression()
        while self.peek().is_additive:
            tok = self.chew()
            expr = BinOp(tok, expr, self.multiplicative_expression())
        return expr

    def toplevel(self):
        return self.additive_expression()

class Calc(BaseCommand):
    level = AL.User
    def __init__(self, bot, channel, user, args):
        self.BINARY_OPERATORS = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '%': operator.mod,
            '**': operator.pow,
            '^': operator.pow,
            'd': self.roll,
        }
        
        self.UNARY_OPERATORS = {
            '-': operator.neg,
        }
        
        self.CONSTANTS = {
            'pi': math.pi, 
            'e': math.e, 
            'F': -1 # Fudge dice
        }
        
        self.FUNCTIONS = {
            # Selected Python functions
            'abs': abs,
            'round': round,
            # Math functions
            'ceil': math.ceil,
            'copysign': math.copysign,
            'fabs': math.fabs,
            'factorial': math.factorial,
            'floor': math.floor,
            'fmod': math.fmod,
            'frexp': math.frexp,
            'fsum': math.fsum,
            #'isfinite': math.isfinite, # requires Python 3.2
            'isinf': math.isinf,
            'isnan': math.isnan,
            'ldexp': math.ldexp,
            'modf': math.modf,
            'trunc': math.trunc,
            'exp': math.exp,
            'expm1': math.expm1,
            'log': math.log,
            'log1p': math.log1p,
            #'log2': math.log2, # requires Python 3.2
            'log10': math.log10,
            'pow': math.pow,
            'sqrt': math.sqrt,
            'acos': math.acos,
            'asin': math.asin,
            'atan': math.atan,
            'atan2': math.atan2,
            'cos': math.cos,
            'hypot': math.hypot,
            'sin': math.sin,
            'tan': math.sin,
            'degrees': math.degrees,
            'radians': math.radians,
            'acosh': math.acosh,
            'asinh': math.asinh,
            'atanh': math.atanh,
            'cosh': math.cosh,
            'sinh': math.sinh,
            'tanh': math.tanh,
            'erf': math.erf,
            'erfc': math.erfc,
            'gamma': math.gamma,
            'lgamma': math.lgamma,
        }
        
        l = Lexer("".join(args))
        p = Parser(list(l))
        
        try:
            bot.replyout(channel, user, "%g" % self.eval_node(p.toplevel()))
        except KeyError:
            bot.replyout(channel, user, "Unknown constant or function: %s" % exc_info()[1][0])
        except:
            bot.replyout(channel, user, "Error")
        
    def eval_node(self, node):
        if isinstance(node, Token):
            return node.value
        elif isinstance(node, BinOp):
            op = self.BINARY_OPERATORS[node.op.value]
            return op(self.eval_node(node.lhs), self.eval_node(node.rhs))
        elif isinstance(node, UnaryOp):
            op = self.UNARY_OPERATORS[node.op.value]
            return op(self.eval_node(node.rhs))
        elif isinstance(node, Constant):
            return self.CONSTANTS[node.name.value]
        elif isinstance(node, FunctionCall):
            args = [self.eval_node(n) for n in node.args]
            func = self.FUNCTIONS[node.name.value]
            return func(*args)
        raise SyntaxError
        
    def roll(self, dice, sides):
        if dice < 1 or sides < -1 or sides == 0:
            raise SyntaxError
        
        sum = 0
        
        for die in range(0, dice):
            if sides == -1:
                sum = sum + randint(-1, 1) # Fudge dice!
            else:
                sum = sum + randint(1, sides)
            
        return sum