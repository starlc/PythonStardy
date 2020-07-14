#!/usr/bin/python
# Filename: str_methods.py

name = 'Swaroop'

if name.startswith('Swa'):
    print('Yes,the string starts with "Swa"')

if 'a' in name :
    print('Yes, it contains the string "a"')


delimeter = '_*_'
mylist = ['a','b','c','d']
print(delimeter.join(mylist))