#!/usr/bin/python
# Filename: break.py

while True:
    s = input("Enter something:")
    if s=='quit':
        break
    print('length of the string is',len(s))

print('done')