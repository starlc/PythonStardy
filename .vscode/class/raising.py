#!/usr/bin/python
# Filename: raising.py


class ShortInputException(Exception):
    '''A user-defined exception class.'''
    def __init__(self, length, atleast):
        Exception.__init__(self)
        self.length = length
        self.atleast = atleast

    def __str__(self):
        return self.msg


try:
    s = input('Enter something-->')
    if len(s) < 3:
        raise ShortInputException(len(s), 3)
except EOFError:
    print('\n Why did you do an EOF on me?')
except ShortInputException as x:
    print('\n The input was of length %d,\
    was expecting at least %d.' % (x.length, x.atleast))

else:
    print('No exception was raised.')