#!/usr/bin/python
# Filename: func_doc.py

def printMax(x,y):
    '''Print the max of two numbers.

    The two values must be integers'''
    x = int(x)
    y = int(y)
    if x>y:
        print(x,'x is the max one')
    else:
        print(y,'y is the max one')

printMax(3,5)
print(printMax.__doc__)