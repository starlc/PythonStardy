#!/usr/bin/python
# Filename: if.py

number = 23
guess = int(input('Enter an integer:'))
if guess == number:
    print('get it')
elif guess < number:
    print('big more')
else:
    print('a little')
    pass