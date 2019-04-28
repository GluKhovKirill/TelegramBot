#!/usr/bin/python 
# -*- coding: utf-8 -*-
import math


class MathExecutor:
    def __init__(self, equation):
        self.error_codes = {"ERR" : "Что-то пошло не так!",
                            "ZERODIV": "Вы попытались поделить на 0. К сожалению, это ещё не определено!",
                            "OPS": "Я не могу это выполнить..."}
        self.equation = equation
        
        
    def execute(self):
        # Сам исполнитель (вычислитель)
        answer = self.count(self.equation)
        if answer[0]:
            return str(answer[1])
        else:
            return self.error_codes[answer[1]]        
    
    def count(self, equation):
        if "_" in equation:
            return (False, "OPS")
        equation = equation.replace("pi", str(math.pi))
        equation = equation.replace("e", str(math.e)).replace(",",".")
        #CHECK
        for symbol in equation:
            if symbol.isalpha():
                return (False, "OPS")
        #*************
        try:
            return (True, eval(equation, {'__builtins__':{}}))
        except ZeroDivisionError:
            return (False, "ZERODIV")
        except BaseException as e:
            return (False, "ERR")