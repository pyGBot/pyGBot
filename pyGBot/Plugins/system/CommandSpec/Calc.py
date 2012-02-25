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

from pyGBot.Plugins.system.Commands import BaseCommand
from pyGBot.Plugins.system.Auth import AuthLevels as AL

import ast, math, operator
from sys import exc_info
from random import randint
from re import sub

class Calc(BaseCommand):    
    level = AL.User
    def __init__(self, bot, channel, user, args):
        self.OPERS = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv, # int / int = float
            ast.Pow: operator.pow, # use ^ for powers instead of **
            ast.FloorDiv: self.roll, # hijacked operator for dicerolls
        }
        
        self.CONSTANTS = {
            'pi': math.pi,
            'e': math.e,
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
            # Custom functions
            'roll': self.roll,
        }
    
        try:
            # Note the regex. #d gets replaced with #** to hijack the default POW operator for dicerolls. 
            bot.replyout(channel, user, "%g" % self.eval_str(sub("(\d)d","\g<1>//","".join(args).replace("^","**"))))
        except:
            bot.replyout(channel, user, "Error: %s" % exc_info()[1])
    
    def eval_binop(self, node):
        op_type = type(node.op)
        if op_type in self.OPERS:
            return self.OPERS[op_type](self.eval_node(node.left), self.eval_node(node.right))
        else:
            raise ValueError("Unsupported binary operation %r" % (type(node.op).__name__,))
    
    def eval_function_call(self, node):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Unsupported function")
    
        func_name = node.func.id.replace("&", "d")
    
        if func_name in self.FUNCTIONS:
            func = self.FUNCTIONS[func_name]
        else:
            raise ValueError("Unsupported function %r" % (node.func.id,))
    
        if node.args is not None:
            args = [self.eval_node(v) for v in node.args]
        else:
            args = []
    
        if node.kwargs is not None:
            kwargs = dict((k, eval_node(v)) for (k, v) in node.kwargs.iteritems())
        else:
            kwargs = {}
    
        return func(*args, **kwargs)
    
    def eval_constant(self, node):
        const = node.id
        if const in self.CONSTANTS:
            return self.CONSTANTS[const]
        else:
            raise ValueError("Unknown variable: %s" % const)
    
    def eval_node(self, node):
        if isinstance(node, ast.Expression):
            return self.eval_node(node.body)
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            return self.eval_binop(node)
        elif isinstance(node, ast.Call):
            return self.eval_function_call(node)
        elif isinstance(node, ast.Name):
            return self.eval_constant(node)
        raise ValueError("Unsupported node type %r" % (type(node).__name__,))
    
    def eval_str(self, expr):
        return self.eval_node(ast.parse(expr, mode='eval'))
    
    def roll(self, rolls, sides):
        sum = 0
        for i in range(0, rolls):
            sum = sum + randint(1, sides)
        return sum